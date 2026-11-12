"""Check phone slide builds and touch interactions in Chromium and WebKit."""
from pathlib import Path
from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = Path('/tmp/mta-workshop-mobile-qa')
OUT.mkdir(exist_ok=True)

with sync_playwright() as p:
    for engine in ['chromium', 'webkit']:
        options = {'channel': 'chrome'} if engine == 'chromium' else {}
        browser = getattr(p, engine).launch(headless=True, **options)
        device = {k: v for k, v in p.devices['iPhone 13'].items()
                  if k != 'default_browser_type'}
        context = browser.new_context(**device, reduced_motion='reduce')
        page = context.new_page()
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto((ROOT / 'index.html').as_uri())
        page.wait_for_function('window.SLIDES_READY === true')
        # Auto scroll view used to wrap sections before our setup ran, breaking
        # the contents menu, footers, and the normal fragment navigation.
        assert not page.evaluate('Reveal.isScrollView()')
        assert page.locator('.slides > section').count() == 21
        assert page.locator('.deck-footer').count() == 21
        assert page.locator('#contents-dialog [data-slide]').count() == 21

        for viewport in [{'width': 390, 'height': 664},
                         {'width': 844, 'height': 390}]:
            page.set_viewport_size(viewport)
            page.evaluate('Reveal.layout()')
            assert not page.evaluate('Reveal.isScrollView()')
            page.locator('#deck-contents').tap()
            page.locator('#contents-dialog [data-slide="2"]').tap()
            expect(page.locator('.allocation-demo')).to_be_hidden()
            for fragment in range(6):
                page.locator('.controls .navigate-right').tap()
                assert page.evaluate('Reveal.getIndices().h') == 2
                assert page.evaluate('Reveal.getIndices().f') == fragment
            expect(page.locator('.allocation-demo')).to_be_visible()
            cells = page.locator('#allocation-rows button')
            assert cells.count() == 45
            for i in range(3):
                cells.nth(i).tap()
                expect(cells.nth(i)).to_have_attribute('aria-pressed', 'true')
            expect(page.locator('#selection-count')).to_have_text('3 / 3 pairs selected')
            assert page.locator('#passenger-count').inner_text() != '0'
            cells.nth(3).tap()
            expect(cells.nth(3)).to_have_attribute('aria-pressed', 'false')
            assert page.evaluate('Reveal.getIndices().f') == 5
            page.screenshot(path=str(OUT / f'{engine}-{viewport["width"]}-slide-3.png'))
            page.locator('#reset-allocation').tap()
            expect(page.locator('#passenger-count')).to_have_text('0')
            page.locator('.controls .navigate-left').tap()
            expect(page.locator('.allocation-demo')).to_be_hidden()

            page.locator('#deck-contents').tap()
            page.locator('#contents-dialog [data-slide="11"]').tap()
            page.evaluate('while(Reveal.nextFragment()) {}')
            page.locator('#show-station-example').tap()
            expect(page.locator('#station-chart')).to_be_visible()
            page.locator('.station-chart-tab[data-chart="pie"]').tap()
            expect(page.locator('.station-chart-tab[data-chart="pie"]')).to_have_attribute('aria-pressed', 'true')
            assert page.evaluate('Reveal.getIndices().h') == 11
            print(f'{engine} {viewport}: slide builds, station selections, reset, back, and chart controls passed')
        assert not errors, errors
        browser.close()
