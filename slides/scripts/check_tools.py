"""Verify presentation utilities and the offline PDF handout."""
from pathlib import Path
import json
import re
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = Path('/tmp/mta-workshop-slide-qa')
OUT.mkdir(exist_ok=True)
with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    context = browser.new_context(viewport={'width':1440,'height':900}, reduced_motion='reduce')
    context.add_init_script('window.print=()=>{window.__printCalls=(window.__printCalls||0)+1;}')
    errors = []
    context.on('page', lambda page: page.on('pageerror', lambda error: errors.append(str(error))))
    page = context.new_page()
    page.goto((ROOT/'index.html').as_uri())
    page.wait_for_function('window.SLIDES_READY')
    page.evaluate('Reveal.slide(12,0,0)')
    original = page.evaluate('Reveal.getIndices()')
    page.locator('#deck-tools').click()
    assert page.locator('#tools-dialog').is_visible()
    assert page.evaluate('Reveal.getIndices()') == original
    assert page.locator('#deck-tools').get_attribute('aria-expanded') == 'true'
    page.screenshot(path=str(OUT/'tools-menu.png'))
    page.keyboard.press('Escape')
    assert page.locator('#tools-dialog').is_hidden()
    assert not page.evaluate('Reveal.isOverview()')
    page.locator('#deck-tools').click()
    page.locator('#tools-overview').click()
    assert page.evaluate('Reveal.isOverview()')
    page.keyboard.press('Escape')
    assert not page.evaluate('Reveal.isOverview()')
    page.locator('#deck-tools').click()
    page.locator('#tools-fullscreen').click()
    page.wait_for_function('Boolean(document.fullscreenElement)')
    page.locator('#deck-tools').click()
    assert page.locator('#tools-fullscreen strong').inner_text() == 'Exit full screen'
    page.locator('#tools-fullscreen').click()
    page.wait_for_function('!document.fullscreenElement')
    page.locator('#deck-tools').click()
    page.locator('#tools-restart').click()
    assert page.evaluate('Reveal.getCurrentSlide().id') == 'workshop-title'
    page.locator('#deck-tools').click()
    with context.expect_page() as popup:
        page.locator('#tools-pdf').click()
    pdf_page = popup.value
    pdf_page.wait_for_function('window.PDF_READY', timeout=30000)
    assert pdf_page.evaluate('window.__printCalls') == 1
    assert pdf_page.locator('.pdf-page').count() == 21
    assert pdf_page.locator('#deck-toolbar').is_hidden()
    assert pdf_page.locator('#weekday-result').is_visible()
    assert pdf_page.locator('#scatter-result').is_visible()
    assert pdf_page.locator('#station-example-result').is_visible()
    assert pdf_page.locator('.comparison-panel').is_visible()
    assert 'five' in pdf_page.locator('#token-context').inner_text()
    assert page.evaluate('Reveal.getCurrentSlide().id') == 'workshop-title'
    pdf_page.locator('#pdf-save').click()
    assert pdf_page.evaluate('window.__printCalls') == 2
    pdf_page.locator('.pdf-page').first.screenshot(path=str(OUT/'pdf-title.png'))
    pdf_page.locator('.pdf-page').nth(12).screenshot(path=str(OUT/'pdf-histograms.png'))
    pdf = pdf_page.pdf(path=str(OUT/'tools-export-check.pdf'), print_background=True, prefer_css_page_size=True)
    assert pdf.startswith(b'%PDF')
    pages = len(re.findall(rb'/Type\s*/Page\b',pdf))
    assert pages == 21, pages
    pdf_page.emulate_media(media='print')
    assert pdf_page.locator('#pdf-controls').is_hidden()
    assert not errors, errors
    print(json.dumps({'tools':'passed','fullscreen':'passed','pdf_pages':pages,'page_errors':errors}))
    browser.close()
