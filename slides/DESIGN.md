# Working design and writing guide

These are the working conventions for the twenty-one-slide draft, refined with the user.

## Visual reference

Follow `../format_slides/Presentation_NetworkChanceConstraints/`:

- Quarto + Reveal.js, 1280 x 720 canvas, 16:9.
- White background, navy text (`#182c3e`), teal emphasis (`#267f77`), blue links (`#226a85`). Orange (`#a4592f`) highlights a constraint or uncertainty. Use pale fills sparingly.
- Avenir Next, then Segoe UI and sans-serif fallbacks.
- Titles: 44px, medium weight, left aligned, in the same position across slides, with a thin divider line underneath.
- Main explanatory text: approximately 25-32px. Tables and diagram labels: 17-24px. Sources and small captions: 12-15px.
- Keep the reference deck's whitespace, thin divider lines, and restrained footer. Use the University of Toronto Scarborough Management logo at its original proportions. Credit Andre A. Cire, without copying the reference deck's co-authors.
- Use a single composed visual area or two purposeful columns. Reserve the bottom 94px for the footer. Shorten or stage content before shrinking type.

## Writing

- Follow the slide order and intent in `../CONTENT.md`. The current draft contains slides 1–21. Preserve the user's direct edits to `index.qmd` when extending the deck.
- Use short, direct sentences and concrete business terms.
- Name the task, objective and constraints explicitly. Explain technical language with the TTC case.
- Avoid “This is not X; this is Y” and similar negative/contrastive slogans. Omit statements about unrelated alternatives.
- Avoid generic claims about transformation, value creation or AI superiority. Explain the specific action or benefit.
- Put the main point on the slide. Put qualifications, source detail, facilitation prompts, and extra explanations in speaker notes.
- Retain visible labels for invented numbers, real-data limitations needed to read a visual, and image credits.
- Prefer simple verbs: inspect, predict, compare, select, check.
- Treat frontier capability and model openness as different dimensions. Avoid unverified model rankings or unnecessary version numbers.
- Explain that an AI assistant may generate an answer in one request while still using a workflow internally. The student's choice is how much of the process to inspect and guide.

## Animation and interaction

- Advance with presenter-controlled builds. Use motion to reveal a concept or state change.
- Slide 2 starts with its title and footer only. Reveal the photograph, passenger-help statement, and each of the three examples on separate clicks; finish with the bold deployment question. Colour “Where” and “when” warm orange and the rest of that question black.
- Pair Slide 2's examples with small illustrations on their right: crowded platforms (people gathering), door problems (obstructed doors), and weather disruptions (rain). Crowding is an illustrative consequence of delays; only door and weather examples map to dataset reasons. Keep that distinction in the source caption and speaker notes. Play each short animation when revealed, then keep a static illustration visible.
- Keep interactions within the requested slide. Slide 6 replaces its table with exercises instead of adding another slide or compressing both.
- Give interactive controls clear labels, visible focus, and a reset/back action.
- An interaction must not accidentally advance the slide. Source links remain clickable.
- Changes should be reversible. Backward navigation must restore the appropriate build.
- Keep animations short and respect reduced motion. Avoid decorative loops. Slide 11 deliberately repeats the Questions → Analysis → Insights cycle to explain iteration, as requested. The token-generation demonstration has no blinking cursor or editable-text affordance.
- Slide 3 reveals each main element separately. Choose three station–time pairs without staffing inputs. Keep the expected-passenger total on the left, visible before revealing the selection grid.
- Slide 4 explains what a recorded delay entry contains. Use only the workshop dataset; reserve training discussion for the end and omit a testing-set section and prediction-table view. Keep the CSV download button explicitly marked as a placeholder until its real link is supplied.
- Distinguish a simulation from measured data. The expected-passenger scores and token probabilities are labelled illustrations. TTC delay logs do not contain passenger counts.
- Slide 7 reveals the three process steps with short schematic animations, then visualization and interpretability. Slide 8 highlights a real row, its units, and computed quality checks, with 750 ms reveals and 850 ms highlights. Slide 9 introduces task, context, output format, and checks one ingredient per click. Slide 9 also assembles the ingredients into a natural prompt. Slide 10 shows three copyable prompts in italic prose across one spacious column, with no results or ingredient labels; switching views must not advance the presentation. Save charts and comparisons for pattern identification.

## Evidence and implementation

- Source data examples from the prepared CSVs through `scripts/prepare_data.py`.
- Keep original photographs and logos in `assets/` and include source/licence links.
- Retain editable content in QMD, HTML/CSS, and JavaScript. Do not manually patch the generated HTML.
- Embed assets in the final HTML for offline use. Use `networkcc` for Python, Quarto, and browser checks.
- Check every slide and build visually. Test actual controls, constrained selections, backward navigation, keyboard access, and layout at different aspect ratios.
