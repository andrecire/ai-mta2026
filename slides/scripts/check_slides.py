"""Check the twenty-one-slide offline deck with Python Playwright in networkcc."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = Path('/tmp/mta-workshop-slide-qa')
OUT.mkdir(exist_ok=True)

FIT = """() => {
 const s = Reveal.getCurrentSlide(); const bounds=s.getBoundingClientRect();
 const footer=s.querySelector('.deck-footer').getBoundingClientRect();
 return [...s.querySelectorAll('h2,h3,p,table,figure,button,.source-link,.prediction-principle,.token-demo,.model-families,.allocation-status,.iteration-ring,#station-chart')]
 .filter(e=>!e.closest('.notes,.deck-footer'))
 .filter(e=>{let c=getComputedStyle(e);return c.display!=='none'&&c.visibility!=='hidden'&&c.opacity!=='0'&&e.getBoundingClientRect().width>0})
 .filter(e=>{const r=e.getBoundingClientRect();return r.left<bounds.left-2||r.right>bounds.right+2||r.bottom>footer.top-5})
 .map(e=>({tag:e.tagName,class:e.className,text:e.textContent.slice(0,80),bottom:e.getBoundingClientRect().bottom,footer:footer.top}));
}"""

with sync_playwright() as p:
    browser=p.chromium.launch(channel='chrome',headless=True)
    context=browser.new_context(viewport={'width':1440,'height':900},reduced_motion='reduce')
    page=context.new_page()
    errors=[]; requests=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    page.route('http://**/*',lambda route:(requests.append(route.request.url),route.abort()))
    page.route('https://**/*',lambda route:(requests.append(route.request.url),route.abort()))
    page.goto((ROOT/'index.html').as_uri())
    page.wait_for_function('window.SLIDES_READY === true')
    assert page.locator('.slides > section').count()==21
    assert page.locator('.deck-footer').count()==21
    assert page.locator('#allocation-rows button').count()==45
    assert page.evaluate('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)')
    # Opening and closing contacts are visible immediately and use the supplied address.
    for index,selector,title in [(0,'#workshop-title','Artificial Intelligence for Data Analysis'),(20,'#thank-you','Thank you!')]:
        page.evaluate('(i)=>Reveal.slide(i,0,-1)',index)
        assert page.locator(f'{selector}>h2').inner_text()==title
        assert page.locator(f'{selector} .workshop-author').inner_text()=='Andre A. Cire'
        email=page.locator(f'{selector} .workshop-email a')
        assert email.is_visible() and email.get_attribute('href')=='mailto:andre.cire@rotman.utoronto.ca'
        assert page.locator(f'{selector} .fragment').count()==0
    assert page.locator('#thank-you .next-steps-title').inner_text()=='Continue exploring.'
    # Contents stays in the bottom-left and opens without advancing the deck.
    page.evaluate('Reveal.slide(1,0,-1)')
    page.locator('#deck-contents').click()
    assert page.locator('#contents-dialog').is_visible()
    assert page.locator('#contents-dialog [data-slide]').count()==21
    assert page.evaluate('Reveal.getIndices().h')==1
    page.locator('#contents-dialog [data-slide="11"]').click()
    assert page.evaluate('Reveal.getIndices().h')==11
    assert page.locator('#contents-dialog').is_hidden()
    assert page.locator('#station-delays .fragment.visible').count()==0
    page.locator('#deck-contents').click()
    assert page.locator('#contents-dialog [aria-current="page"]').get_attribute('data-slide')=='11'
    page.screenshot(path=str(OUT/'contents-menu.png'))
    page.keyboard.press('Escape')
    assert page.locator('#contents-dialog').is_hidden()
    assert not page.evaluate('Reveal.isOverview()')
    page.locator('#deck-contents').click()
    page.locator('.contents-close').click()
    assert page.locator('#contents-dialog').is_hidden()
    page.locator('#deck-contents').blur()
    # The opening slide waits for each presenter click, including the first photo.
    page.evaluate('Reveal.slide(1,0,-1)')
    assert page.locator('#problem .fragment.visible').count()==0
    assert page.locator('#problem .station-photo').is_hidden()
    for step in range(6):
        page.keyboard.press('ArrowRight')
        page.wait_for_timeout(80)
        assert page.evaluate('Reveal.getIndices().h')==1
        assert page.evaluate('Reveal.getIndices().f')==step
        assert page.locator(f'#problem .fragment[data-fragment-index="{step}"].visible').count()>0
        assert page.locator('#problem .support-example.visible').count()==min(3,max(0,step-1))
        assert page.locator('#problem .takeaway').is_visible()==(step==5)
    page.keyboard.press('ArrowLeft')
    assert page.locator('#problem .takeaway').is_hidden()
    assert page.locator('#problem .support-example.visible').count()==3
    page.emulate_media(reduced_motion='no-preference')
    page.evaluate('Reveal.slide(1,0,1)')
    page.keyboard.press('ArrowRight')
    assert page.locator('.crowd-person').first.evaluate("e=>getComputedStyle(e).animationName")=='crowd-arrives'
    page.wait_for_timeout(1600)
    assert page.locator('.crowd-person').last.evaluate("e=>e.getAnimations().length")==0
    page.emulate_media(reduced_motion='reduce')
    assert page.locator('.crowd-person').first.evaluate("e=>getComputedStyle(e).animationName")=='none'
    fit=[]
    for i in range(21):
        page.evaluate('(i)=>Reveal.slide(i,0,-1)',i)
        page.wait_for_timeout(250)
        fit.extend(page.evaluate(FIT))
        page.screenshot(path=str(OUT/f'slide-{i+1}-initial.png'))
        while page.evaluate('Reveal.nextFragment()'):
            page.wait_for_timeout(250)
            fit.extend(page.evaluate(FIT))
        page.screenshot(path=str(OUT/f'slide-{i+1}-final.png'))

    page.evaluate('Reveal.slide(2,0,-1)')
    assert page.locator('#goal .fragment.visible').count()==0
    for step in range(8):
        page.keyboard.press('ArrowRight')
        assert page.evaluate('Reveal.getIndices().h')==2
        assert page.evaluate('Reveal.getIndices().f')==step
        assert page.locator('.passenger-summary').is_visible()==(step>=4)
        assert page.locator('.allocation-demo').is_visible()==(step>=5)
    page.keyboard.press('ArrowLeft')
    assert page.locator('#goal [data-fragment-index="7"]').is_hidden()
    page.keyboard.press('ArrowRight')
    page.locator('[data-key="S01-0"]').click()
    assert page.locator('#passenger-count').inner_text()=='240'
    page.locator('[data-key="S02-0"]').click()
    page.locator('[data-key="S12-0"]').click()
    assert page.locator('#selection-count').inner_text()=='3 / 3 pairs selected'
    assert page.locator('#passenger-count').inner_text()=='500'
    page.locator('[data-key="S09-0"]').click()
    assert 'Deselect' in page.locator('#allocation-message').inner_text()
    assert page.locator('#passenger-count').inner_text()=='500'
    page.locator('[data-key="S01-0"]').click()
    assert page.locator('#passenger-count').inner_text()=='260'
    page.locator('[data-key="S04-0"]').click()
    assert page.locator('#passenger-count').inner_text()=='420'
    page.locator('[data-key="S12-0"]').click()
    page.locator('[data-key="S02-2"]').click()
    assert page.locator('#passenger-count').inner_text()=='650'
    assert page.locator('#allocation-rows button[aria-pressed="true"]').count()==3
    assert page.evaluate('Reveal.getIndices().h')==2
    assert page.evaluate('Reveal.getIndices().f')==7
    page.screenshot(path=str(OUT/'slide-3-selection.png'))
    page.locator('#reset-allocation').click()
    assert page.locator('#passenger-count').inner_text()=='0'
    assert page.locator('#selection-count').inner_text()=='0 / 3 pairs selected'
    assert page.locator('#allocation-rows button[aria-pressed="true"]').count()==0

    page.evaluate('Reveal.slide(3,0,-1)')
    assert page.locator('#data .fragment.visible').count()==0
    data_steps=page.locator('#data .fragment').evaluate_all('es=>[...new Set(es.map(e=>Number(e.dataset.fragmentIndex)))].sort((a,b)=>a-b)')
    for step in data_steps:
        page.keyboard.press('ArrowRight')
        assert page.evaluate('Reveal.getIndices().h')==3
        assert page.evaluate('Reveal.getIndices().f')==step
        expected=page.locator('#data .fragment').evaluate_all('(es,step)=>es.filter(e=>Number(e.dataset.fragmentIndex)<=step).length',step)
        assert page.locator('#data .fragment.visible').count()==expected
        assert page.locator('#log-view').is_visible()==page.locator('#data .source-link').is_visible()
        assert page.locator('#data-count').is_visible()==page.locator('#data .period').is_visible()
    page.keyboard.press('ArrowLeft')
    assert page.locator('#data .data-purpose>span').is_hidden()
    page.keyboard.press('ArrowRight')
    assert page.locator('#log-rows tr').count()==3
    assert page.locator('#data-count').inner_text()=='708'
    assert page.locator('#window-view,.data-switch,.holdout').count()==0
    assert page.locator('#download-csv').is_enabled()
    assert page.locator('#download-csv').get_attribute('download')=='ttc_training_log_jan_sep_2025.csv'
    assert page.locator('#download-csv').get_attribute('href').startswith('blob:')
    assert 'January–September 2025' in page.locator('#download-status').inner_text()
    fit.extend(page.evaluate(FIT))
    page.screenshot(path=str(OUT/'slide-4-log.png'))

    page.evaluate('Reveal.slide(4,0,-1)')
    assert page.locator('#llm .fragment.visible').count()==0
    for step in range(8):
        page.keyboard.press('ArrowRight')
        assert page.evaluate('Reveal.getIndices().h')==4
        assert page.evaluate('Reveal.getIndices().f')==step
        assert page.locator('.context-stage').is_visible()==(step>=2)
        assert page.locator('.model-stage').is_visible()==(step>=3)
        assert page.locator('.prediction-stage').is_visible()==(step>=3)
        assert page.locator('#generate-token').is_visible()==(step>=4)
        assert page.locator('#llm [data-fragment-index="6"]').is_visible()==(step>=6)
        assert page.locator('.family-note').is_visible()==(step>=7)
    page.keyboard.press('ArrowLeft')
    assert page.locator('.family-note').is_hidden()
    page.keyboard.press('ArrowRight')
    assert page.locator('#token-context').inner_text()=='The next train arrives in five'
    for _ in range(2):page.locator('#generate-token').click()
    assert page.evaluate('Reveal.getIndices().f')==7
    assert page.locator('#token-context').inner_text()=='The next train arrives in five minutes.'
    assert page.locator('#generate-token').is_disabled()
    fit.extend(page.evaluate(FIT))
    page.screenshot(path=str(OUT/'slide-5-generated.png'))
    page.locator('#reset-tokens').click()
    assert page.locator('#token-context').inner_text()=='The next train arrives in'
    assert page.locator('#llm-network .network-node').count()==14
    page.emulate_media(reduced_motion='no-preference')
    # First reveal: the output waits for the network without another click.
    page.evaluate('Reveal.slide(4,0,2)')
    page.keyboard.press('ArrowRight')
    assert page.locator('.model-symbol.network-active').count()==1
    assert page.locator('.prediction-stage').is_hidden()
    assert page.locator('#token-context').inner_text()=='The next train arrives in'
    page.wait_for_function("!document.querySelector('.model-symbol').classList.contains('network-active')")
    assert page.locator('.prediction-stage').is_visible()
    assert page.locator('#token-context').inner_text()=='The next train arrives in five'
    assert page.locator('.token-name').all_text_contents()==['five','two','ten']
    assert page.locator('.token-probability').all_text_contents()==['58%','27%','15%']
    assert page.evaluate('Reveal.getIndices().f')==3
    page.evaluate('Reveal.slide(4,0,7)')
    page.locator('#generate-token').click()
    assert page.locator('.model-symbol.network-active').count()==1
    assert page.locator('.prediction-stage').is_hidden()
    assert page.locator('#generate-token').is_disabled()
    assert page.locator('#token-context').inner_text()=='The next train arrives in five'
    page.wait_for_timeout(350)
    page.screenshot(path=str(OUT/'slide-5-network-active.png'))
    page.wait_for_function("!document.querySelector('.model-symbol').classList.contains('network-active')")
    assert page.locator('.model-symbol.network-active').count()==0
    assert page.locator('.prediction-stage').is_visible()
    assert page.locator('#token-context').inner_text()=='The next train arrives in five minutes'
    assert page.locator('.token-name').all_text_contents()==['minutes','seconds','hours']
    assert page.locator('.token-probability').all_text_contents()==['85%','10%','5%']
    page.screenshot(path=str(OUT/'slide-5-network-result.png'))
    page.locator('#generate-token').click()
    page.locator('#reset-tokens').click()
    assert page.locator('.model-symbol.network-active').count()==0
    page.wait_for_timeout(1400)
    assert page.locator('#token-context').inner_text()=='The next train arrives in'
    assert page.locator('.prediction-stage').is_visible()
    page.emulate_media(reduced_motion='reduce')
    page.locator('#generate-token').click()
    assert page.locator('.model-symbol.network-active').count()==0
    page.locator('#reset-tokens').click()

    page.evaluate('Reveal.slide(5,0,-1)')
    assert page.locator('.comparison-table tbody tr.visible').count()==0
    assert page.locator('.comparison-table tbody tr:visible').count()==0
    for step in range(10):
        page.locator('#one-shot h2').click()
        assert page.locator('.comparison-table tbody tr.visible').count()==step//2+1
        assert page.locator('.comparison-table tbody tr:visible').count()==step//2+1
        assert page.locator('.comparison-table tbody td:last-child:visible').count()==(step+1)//2
        assert page.locator('.comparison-table tbody tr').nth(step//2).locator('td').first.is_visible()==(step%2==1)
        assert page.locator('.comparison-table tbody tr').nth(step//2).locator('td').last.is_visible()==(step%2==1)
        assert page.locator('.comparison-panel').is_visible()
        assert page.locator('.process-note').is_hidden()
        if step==2:page.screenshot(path=str(OUT/'slide-6-awaiting-contrast.png'))
    page.keyboard.press('ArrowRight')
    assert page.locator('.process-note').is_visible()
    page.keyboard.press('ArrowRight')
    assert page.locator('.exercise-panel').is_visible()
    for name,choice in [('invitation','one'),('ttc','process'),('competition','process')]:
        page.locator(f'[data-case="{name}"] [data-choice="{choice}"]').click()
        assert page.locator(f'[data-case="{name}"] .exercise-feedback').inner_text()
    fit.extend(page.evaluate(FIT))
    page.screenshot(path=str(OUT/'slide-6-discussion.png'))
    page.locator('#back-to-comparison').click()
    assert page.locator('.comparison-panel').is_visible()
    assert not page.locator('.exercise-panel').is_visible()
    assert page.locator('.comparison-table tbody tr.visible').count()==5
    assert page.locator('.comparison-table tbody tr:visible').count()==5
    page.screenshot(path=str(OUT/'slide-6-full-table.png'))
    for step in range(9,-2,-1):
        page.keyboard.press('ArrowLeft')
        assert page.evaluate('Reveal.getIndices().h')==5
        assert page.locator('.comparison-table tbody tr.visible').count()==step//2+1
        assert page.locator('.comparison-table tbody tr:visible').count()==step//2+1
        assert page.locator('.comparison-table tbody td:last-child:visible').count()==(step+1)//2
        assert page.locator('.comparison-table tbody td:visible').count()==2*((step+1)//2)
    page.keyboard.press('ArrowLeft')
    assert page.evaluate('Reveal.getIndices().h')==4
    # Keyboard access to interaction buttons should activate, not advance slides.
    page.locator('#generate-token').focus()
    page.keyboard.press('Enter')
    assert page.evaluate('Reveal.getIndices().h')==4
    assert 'five' in page.locator('#token-context').inner_text()
    page.locator('#generate-token').blur()
    # New process and data-reading slides build in order and reverse cleanly.
    page.evaluate('Reveal.slide(6,0,-1)')
    for step in range(4):
        page.keyboard.press('ArrowRight')
        assert page.locator('.process-step:visible').count()==min(step+1,3)
        assert page.locator('.process-foundation').is_visible()==(step==3)
    page.keyboard.press('ArrowLeft')
    assert page.locator('.process-foundation').is_hidden()
    page.emulate_media(reduced_motion='no-preference')
    page.evaluate('Reveal.slide(6,0,-1)')
    page.keyboard.press('ArrowRight')
    assert page.locator('.scan-row').evaluate("e=>getComputedStyle(e).animationName")=='read-row'
    page.emulate_media(reduced_motion='reduce')
    page.evaluate('Reveal.slide(7,0,-1)')
    for step in range(3):
        page.keyboard.press('ArrowRight')
        assert page.locator('.reading-step:visible').count()==step+1
        assert page.locator('.audit-summary').is_visible()==(step==2)
    assert page.locator('#reading-rows tr').count()==3
    assert page.locator('#audit-missing').inner_text()=='0'
    assert '143 min' in page.locator('#audit-range').inner_text()
    page.keyboard.press('ArrowLeft')
    assert page.locator('#understand-data').get_attribute('data-reading-step')=='units'
    assert page.locator('.audit-summary').is_hidden()
    # Slide 7 uses a slower fade and highlight, with reversible click builds.
    page.emulate_media(reduced_motion='no-preference')
    page.evaluate('Reveal.slide(7,0,-1)')
    page.wait_for_timeout(850)
    page.keyboard.press('ArrowRight')
    page.wait_for_timeout(150)
    opacity=float(page.locator('.reading-step').first.evaluate('e=>getComputedStyle(e).opacity'))
    assert 0 < opacity < 1,opacity
    page.wait_for_timeout(800)
    assert page.locator('.reading-step').first.evaluate('e=>getComputedStyle(e).opacity')=='1'
    page.emulate_media(reduced_motion='reduce')
    # Prompt ingredients appear individually, then the refinement guidance.
    page.evaluate('Reveal.slide(8,0,-1)')
    for step in range(6):
        page.keyboard.press('ArrowRight')
        assert page.locator('.prompt-ingredient:visible').count()==min(step,4)
        assert page.locator('.prompt-guidance').is_visible()==(step==5)
    page.keyboard.press('ArrowLeft')
    assert page.locator('.prompt-guidance').is_hidden()
    page.evaluate('Reveal.slide(9,0,2)')
    assert page.locator('#hands-on .explore-tab').count()==3
    assert page.locator('.exploration-result').count()==0
    for name in ['columns','rows','stations']:
        page.locator(f'[data-explore="{name}"]').click()
        assert page.evaluate('Reveal.getIndices().h')==9
        assert page.locator(f'[data-explore="{name}"]').get_attribute('aria-pressed')=='true'
        prompt=page.locator('#analysis-prompt').inner_text()
        assert not any(label in prompt for label in ['Task:','Context:','Output:','Checks:'])
        assert page.locator('#analysis-prompt').evaluate('e=>getComputedStyle(e).fontStyle')=='italic'
        fit.extend(page.evaluate(FIT))
        page.screenshot(path=str(OUT/f'slide-10-{name}.png'))
    # An unavailable clipboard should still leave a usable manual-copy path.
    page.evaluate("Object.defineProperty(navigator,'clipboard',{value:undefined,configurable:true})")
    page.locator('#copy-analysis-prompt').click()
    assert 'Text selected' in page.locator('#copy-prompt-status').inner_text()
    assert page.evaluate('getSelection().toString()')==page.locator('#analysis-prompt').inner_text()
    assert page.evaluate('Reveal.getIndices().h')==9
    page.evaluate('getSelection().removeAllRanges()')
    # Pattern cycle builds on four clicks, then animates only while complete.
    page.evaluate('Reveal.slide(10,0,-1)')
    for step in range(4):
        page.keyboard.press('ArrowRight')
        assert page.locator('.cycle-stage:visible').count()==min(step+1,3)
        assert page.locator('.pattern-return').is_visible()==(step==3)
    assert page.locator('.return-signal').evaluate('e=>getComputedStyle(e).animationName')=='none'
    page.emulate_media(reduced_motion='no-preference')
    page.evaluate('Reveal.slide(10,0,0)')
    for step in range(1,4):
        page.keyboard.press('ArrowRight')
        arc=page.locator(f'.iteration-ring [data-fragment-index="{step}"] > .ring-arc')
        page.wait_for_timeout(300)
        progress=float(arc.evaluate('e=>getComputedStyle(e).strokeDashoffset').replace('px',''))
        assert 0 < progress < 1,progress
        assert arc.evaluate('e=>getComputedStyle(e).markerEnd')=='none'
        page.wait_for_timeout(900)
        assert float(arc.evaluate('e=>getComputedStyle(e).strokeDashoffset').replace('px',''))==0
        assert 'cycle-arrowhead' in arc.evaluate('e=>getComputedStyle(e).markerEnd')
    assert page.locator('.return-signal').evaluate('e=>getComputedStyle(e).animationName')=='cycle-return'
    page.wait_for_timeout(6000)
    assert float(page.locator('.return-signal').evaluate('e=>getComputedStyle(e).opacity'))>0
    page.screenshot(path=str(OUT/'slide-11-cycle.png'))
    page.keyboard.press('ArrowLeft')
    assert page.locator('.return-signal').evaluate('e=>getComputedStyle(e).animationName')=='none'
    assert page.locator('.cycle-stage:visible').count()==3
    page.evaluate('Reveal.slide(9,0,2)')
    assert page.locator('.cycle-icon').first.evaluate('e=>getComputedStyle(e).animationName')=='none'
    page.emulate_media(reduced_motion='reduce')
    # Both chart views must show the same independently verified station sums.
    import csv
    from collections import Counter
    expected=Counter()
    with (ROOT.parent/'ttc_case/data/training_log_entries.csv').open() as source:
        for record in csv.DictReader(source):
            expected[record['station']]+=int(record['Min Delay'])
    assert sum(expected.values())==4479 and len(expected)==15
    page.evaluate('Reveal.slide(11,0,-1)')
    for step in range(3):
        page.keyboard.press('ArrowRight')
        assert page.locator('.station-chart-workspace').is_visible()==(step>=1)
        assert page.locator('.station-prompt-panel').is_visible()==(step==2)
        assert page.locator('#station-chart').is_hidden()
    for kind,selector in [('bar','.station-bar'),('pie','.station-slice')]:
        page.locator(f'[data-chart="{kind}"].station-chart-tab').click()
        assert page.locator('#station-chart').is_hidden()
        assert page.locator('#show-station-example').is_visible()
        page.locator('#show-station-example').click()
        assert page.locator('#station-chart').is_visible()
        assert page.locator('#show-station-example').is_hidden()
        actual=page.locator(selector).evaluate_all('es=>Object.fromEntries(es.map(e=>[e.dataset.station,Number(e.dataset.minutes)]))')
        assert actual==dict(expected)
        assert page.evaluate('Reveal.getIndices().h')==11
        assert 'use different colors' in page.locator('#station-chart-prompt').inner_text().lower()
        if kind=='pie':
            assert 'Show percentages' in page.locator('#station-chart-prompt').inner_text()
            percentages=page.locator('.pie-percentage').evaluate_all('es=>Object.fromEntries(es.map(e=>[e.dataset.station,e.textContent]))')
            assert percentages=={station:f'{minutes/sum(expected.values())*100:.1f}%' for station,minutes in expected.items()}
        page.locator('#copy-station-prompt').click()
        assert page.evaluate('getSelection().toString()')==page.locator('#station-chart-prompt').inner_text()
        page.evaluate('getSelection().removeAllRanges()')
        fit.extend(page.evaluate(FIT))
        page.screenshot(path=str(OUT/f'slide-12-{kind}.png'))
    page.keyboard.press('ArrowLeft')
    assert page.locator('.station-prompt-panel').is_hidden()
    # Weekday histograms use the requested IQR filter and identical one-minute bins.
    from collections import defaultdict
    weekday_expected=defaultdict(lambda:[0]*10)
    with (ROOT.parent/'ttc_case/data/training_log_entries.csv').open() as source:
        for record in csv.DictReader(source):
            if int(record['Min Delay'])<=10.5:
                weekday_expected[record['Day']][int(record['Min Delay'])-1]+=1
    page.evaluate('Reveal.slide(12,0,-1)')
    for step in range(2):page.keyboard.press('ArrowRight')
    assert page.locator('#weekday-result').is_hidden()
    page.locator('[data-reveal-target="weekday-result"]').click()
    assert page.locator('#weekday-result').is_visible()
    assert page.evaluate('Reveal.getIndices().h')==12
    for day,bins in weekday_expected.items():
        actual=page.locator(f'[data-weekday="{day}"] .weekday-bin').evaluate_all('es=>es.map(e=>Number(e.dataset.count))')
        assert actual==bins
    page.locator('[data-copy-target="weekday-prompt"]').click()
    assert page.evaluate('getSelection().toString()')==page.locator('#weekday-prompt').inner_text()
    page.evaluate('getSelection().removeAllRanges()')
    fit.extend(page.evaluate(FIT))
    page.screenshot(path=str(OUT/'slide-13-histograms.png'))
    # Scatter points and correlation reconcile to the real CSV; zoom is display-only.
    with (ROOT.parent/'ttc_case/data/training_log_entries.csv').open() as source:
        pairs=[(int(r['Min Delay']),int(r['Min Gap'])) for r in csv.DictReader(source)]
    xmean=sum(x for x,y in pairs)/len(pairs); ymean=sum(y for x,y in pairs)/len(pairs)
    expected_r=sum((x-xmean)*(y-ymean) for x,y in pairs)/(sum((x-xmean)**2 for x,y in pairs)*sum((y-ymean)**2 for x,y in pairs))**.5
    page.evaluate('Reveal.slide(13,0,-1)')
    for step in range(3):page.keyboard.press('ArrowRight')
    assert page.locator('#scatter-result').is_hidden()
    page.locator('[data-reveal-target="scatter-result"]').click()
    assert page.locator('#scatter-result').is_visible()
    actual=page.locator('.scatter-point').evaluate_all('es=>es.map(e=>[Number(e.dataset.delay),Number(e.dataset.gap)])')
    assert actual==[list(pair) for pair in pairs]
    assert f'{expected_r:.3f}' in page.locator('#scatter-correlation-value').inner_text()
    fit.extend(page.evaluate(FIT))
    page.screenshot(path=str(OUT/'slide-14-scatter-all.png'))
    page.locator('[data-scatter-limit="20"]').click()
    zoom=[pair for pair in pairs if max(pair)<=20]
    assert page.locator('.scatter-point').count()==len(zoom)
    assert f'{len(pairs)-len(zoom)} outside' in page.locator('#scatter-view-note').inner_text()
    assert 'r still uses all 708' in page.locator('#scatter-view-note').inner_text()
    assert page.evaluate('Reveal.getIndices().h')==13
    fit.extend(page.evaluate(FIT))
    page.screenshot(path=str(OUT/'slide-14-scatter-zoom.png'))
    page.locator('[data-scatter-limit="150"]').click()
    assert page.locator('.scatter-point').count()==708
    page.locator('[data-copy-target="scatter-prompt"]').click()
    assert page.evaluate('getSelection().toString()')==page.locator('#scatter-prompt').inner_text()
    page.evaluate('getSelection().removeAllRanges()')
    # Plot examples and student task reveal one item per click.
    page.evaluate('Reveal.slide(14,0,-1)')
    for step in range(10):
        page.keyboard.press('ArrowRight')
        assert page.locator('.plot-kind:visible').count()==min(step+1,9)
    page.emulate_media(reduced_motion='no-preference')
    assert page.locator('.plot-kind .mini-grow').first.evaluate('e=>getComputedStyle(e).animationName')=='plot-grow'
    page.emulate_media(reduced_motion='reduce')
    page.evaluate('Reveal.slide(15,0,-1)')
    for step in range(5):
        page.keyboard.press('ArrowRight')
        assert page.locator('.insight-statement').is_visible()==(step==4)
    # The merged prediction slide keeps the introduction and three methods.
    page.evaluate('Reveal.slide(16,0,-1)')
    assert page.locator('#passenger-rate,#baseline-total,.model-equation').count()==0
    for step in range(6):
        page.keyboard.press('ArrowRight')
        assert page.locator('.prediction-method:visible').count()==min(max(step-1,0),3)
        assert page.locator('.prediction-principle').is_visible()==(step==5)
    assert page.locator('.prediction-principle p').count()==1
    # The moving average uses July–September only, with zero-record windows included.
    with (ROOT.parent/'ttc_case/data/training_windows.csv').open() as source:
        train_windows=list(csv.DictReader(source))
    monthly={}
    for record in train_windows:
        if record['station']=='Bloor-Yonge' and record['time_window']=='07:00-09:00':
            monthly.setdefault(record['date'][:7],[]).append(int(record['recorded_delay_minutes']))
    expected_means={month:sum(values)/len(values) for month,values in monthly.items()}
    expected_forecast=sum(expected_means[month] for month in ['2025-07','2025-08','2025-09'])/3
    page.evaluate('Reveal.slide(17,0,-1)')
    for step in range(3):
        page.keyboard.press('ArrowRight')
        assert page.locator('.moving-average-example').is_visible()==(step>=1)
        assert page.locator('#moving-average-prompt').is_visible()==(step>=2)
    actual=page.locator('.moving-observation').evaluate_all('es=>Object.fromEntries(es.map(e=>[e.dataset.month,Number(e.dataset.mean)]))')
    assert actual==expected_means
    assert abs(float(page.locator('#moving-forecast').get_attribute('data-value'))-expected_forecast)<1e-12
    page.locator('[data-copy-target="moving-average-prompt"]').click()
    assert page.evaluate('getSelection().toString()')==page.locator('#moving-average-prompt').inner_text()
    page.evaluate('getSelection().removeAllRanges()')
    fit.extend(page.evaluate(FIT))
    page.screenshot(path=str(OUT/'slide-18-moving-average.png'))
    # Both testing downloads work offline and contain only the held-out months.
    page.evaluate('Reveal.slide(18,0,-1)')
    for step in range(6):
        page.keyboard.press('ArrowRight')
        assert page.locator('.testing-downloads').is_visible()==(step==5)
    downloaded={}
    for kind in ['log','windows']:
        with page.expect_download() as download_info:
            page.locator(f'#download-test-{kind}').click()
        download=download_info.value
        target=OUT/download.suggested_filename
        download.save_as(target)
        with target.open() as source: downloaded[kind]=list(csv.DictReader(source))
        assert page.evaluate('Reveal.getIndices().h')==18
    test_logs,test_windows=downloaded['log'],downloaded['windows']
    assert len(test_logs)==229 and len(test_windows)==2970
    assert set(r['Date'][:7] for r in test_logs)=={'2025-10','2025-11','2025-12'}
    assert max(r['date'] for r in train_windows)<min(r['date'] for r in test_windows)
    with (ROOT.parent/'ttc_case/data/training_log_entries.csv').open() as source:
        assert list(test_logs[0])==csv.DictReader(source).fieldnames
    assert all(int(r['Min Delay'])>0 for r in test_logs)
    assert any(int(r['recorded_delay_minutes'])==0 for r in test_windows)
    assert sum(int(r['Min Delay']) for r in test_logs)==sum(int(r['recorded_delay_minutes']) for r in test_windows)
    assert len({(r['date'],r['station_id'],r['time_window']) for r in test_windows})==2970
    fit.extend(page.evaluate(FIT))
    page.screenshot(path=str(OUT/'slide-19-testing.png'))
    # Web sketch enforces three selections and computes its benchmark from the scores.
    page.evaluate('Reveal.slide(19,0,4)')
    choices=page.locator('.planner-pair')
    assert choices.count()==6
    for i in range(4):choices.nth(i).click()
    assert page.locator('.planner-pair[aria-pressed="true"]').count()==3
    assert 'Remove one' in page.locator('#planner-message').inner_text()
    scores=choices.evaluate_all('es=>es.map(e=>Number(e.dataset.score))')
    assert page.locator('#planner-total').inner_text()==f'{sum(scores[:3]):.1f}'
    page.locator('#planner-best').click()
    assert page.locator('#planner-total').inner_text()==f'{sum(sorted(scores,reverse=True)[:3]):.1f}'
    assert page.evaluate('Reveal.getIndices().h')==19
    page.screenshot(path=str(OUT/'slide-20-selected.png'))
    page.locator('#planner-reset').click()
    assert page.locator('#planner-total').inner_text()=='0.0'
    assert page.locator('.planner-pair[aria-pressed="true"]').count()==0
    page.locator('[data-copy-target="interface-prompt"]').click()
    assert page.evaluate('getSelection().toString()')==page.locator('#interface-prompt').inner_text()
    page.evaluate('getSelection().removeAllRanges()')
    fit.extend(page.evaluate(FIT))
    for size in [{'width':1280,'height':720},{'width':1024,'height':768},{'width':1920,'height':1080}]:
        page.set_viewport_size(size)
        page.evaluate('Reveal.layout()')
        for i in range(21):
            page.evaluate('(i)=>Reveal.slide(i,0,0)',i)
            page.evaluate('while(Reveal.nextFragment()) {}')
            page.wait_for_timeout(150)
            fit.extend(page.evaluate(FIT))
    report={'slides':21,'external_resource_requests':requests,'page_errors':errors,'fit_issues':fit,'interactions':'passed'}
    (OUT/'report.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
    assert not errors,errors
    assert not requests,requests
    assert not fit,fit
    browser.close()
