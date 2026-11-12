# Artificial Intelligence for Data Analysis: first twenty-one slides

Open **[index.html](index.html)** in a browser. The complete presentation, photograph, logo, data examples, styles, and scripts are embedded in this single file. Presentation and interactions work offline.

The first twenty-one slides are included, following `../CONTENT.md`:

1. **Artificial Intelligence for Data Analysis:** workshop title, Andre A. Cire, and email.
2. **We start with a problem:** TTC passenger support, a station photograph, and the deployment question.
3. **Our goal today:** TTC hires students to assign support teams to three station–time pairs, aiming to help the most passengers, with an interactive 45-option selection grid.
4. **Data:** explain the fields in TTC delay records, show three real entries, and provide a working training CSV download.
5. **Leveraging AI tools:** introduce the intuition behind LLMs, step through a next-token demonstration without a typing cursor, then reveal model-family examples.
6. **Should we just “one-shot”?** compare approaches, then reveal three discussion exercises on the same slide.
7. **Data analysis process:** three animated steps, with visualization and interpretability throughout.
8. **Understand the data:** read actual rows, distinguish units and counts, and inspect computed data-quality checks.
9. **Constructing a useful prompt:** task, context, output format, and checks, adapted from OpenAI guidance.
10. **Hands-on: understand the TTC data:** three copyable prompts for column meanings, row count, and distinct-station count.
11. **Identifying patterns:** a four-click build of Questions → Analysis → Insights → new questions, with a circular path and continuous moving marker after the final reveal.
12. **Example: delay minutes by station:** real totals for all 15 stations, switchable bar/pie charts, and copyable prompts with color instructions.

13. **Distributions:** compare real delay-duration histograms across weekdays, with a copyable prompt and Show example.
14. **Example: correlation and relationships between columns:** real delay/gap observations, Pearson correlation, and a clearly labeled zoom.
15. **Plot examples:** nine animated plot types with their purposes.
16. **Your turn!:** generate and explain an insight relevant to station–time selection.
17. **What are we predicting?:** the passenger target and assumption, three prediction methods, and “Simple is enough.”
18. **Example: a simple moving average:** a real three-month calculation, chart, and copyable prompt.
19. **Check predictions on future data:** later-month testing, error checks, and downloadable October–December CSVs.
20. **A web interface for the decision:** an interactive six-pair sketch, benchmark, and copyable build prompt.

21. **Thank you!:** a closing invitation to continue exploring, with name and email.

## Present

- **Tools**, beside Contents, offers Generate PDF, Full screen / Exit full screen, Slide overview, and Back to first slide. The menu does not advance the current slide.
- **Generate PDF** opens a separate print-layout tab, reveals slide builds and example charts, and opens the browser print dialog. Select **Save as PDF**, enable background graphics, and disable browser headers and footers. The print tab also has a Save as PDF button to retry after cancelling. The original presentation remains in place. The handout uses the default chart/prompt choices; live interactions remain in the HTML deck.

- Use **Contents** in the bottom-left corner to jump to any slide. Close the menu with × or Escape.
- On phones, use the slide arrows to reveal each step, then tap the interactive controls. Landscape orientation gives the controls more room. Automatic scroll view is disabled so slide builds and controls work the same way as on desktop.

- Click a blank part of the slide, or press **Space / Right Arrow**, to reveal the next build or slide.
- Press **Left Arrow** to go back, **Esc** for overview, **F** for fullscreen, and **S** for speaker view.
- Buttons, tables with selectable cells, and source links do not advance the slide.
- Use **Tab / Enter** for keyboard access to interactive controls. Leave a focused button with Tab before using slide-navigation keys.
- Slide 2 begins with the title and footer. Six clicks reveal the photograph, passenger-help statement, crowded platforms, door problems, weather disruptions, and the closing question. Crowding illustrates a possible consequence of delays; door and weather examples summarize actual training-log descriptions. Each includes a short animated illustration; source-code mappings are in the speaker notes.
- Slide 3 reveals each element on a separate click. Select three station–time pairs in the grid; the left-hand total sums their illustrative expected passenger counts. Select again to deselect. Reset clears the selection and total.
- Slide 4's Download CSV link provides `assets/data/ttc_training_log_jan_sep_2025.csv` (708 records). All three CSV links use ordinary relative URLs online and embedded Blob downloads when opened as a local HTML file.
- Slide 4 starts with its title and footer. Successive clicks reveal the introduction, row definition, table with source, caption, count with station/date coverage, CSV download, takeaway, and AI explanation.
- On slide 4, Generate next token appends a word-sized illustrative token. Reset replays the example.
- Slide 5's colored neural-network illustration pulses from left to right when revealed and whenever a token is generated. The pulses are illustrative; they stop automatically and respect reduced motion.
- Slide 5 starts with its title and footer. Separate clicks reveal the introduction, intuition, context, LLM, controls, frontier examples, open-weight examples, and final note. The first network animation adds “five” automatically, and reveals the candidates that produced it (five / two / ten), plus the outgoing arrow. The next Generate click adds “minutes” and shows minutes / seconds / hours; the following click adds the period and shows punctuation options. Generating another token also waits for the activation to finish before updating and revealing predictions; Reset cancels a running animation. Reduced-motion mode updates immediately.
- On slide 5, each row takes two clicks: first the dimension label alone, then both comparison values together after discussion. Earlier rows remain visible. The closing note follows Effort, then the next click shows the exercises. Back to the comparison restores the complete table and closing note; Left Arrow reverses each reveal.
- Motion respects the system's reduced-motion preference.
- Slides 6 and 7 reveal one process step per click. Slide 8 uses 750 ms fades and 850 ms table highlights. Slide 9 reveals each prompt ingredient separately. On Slide 10, use the three buttons for column meanings, rows, and distinct stations. Copy prompt copies the current example, or selects it for manual copying if clipboard access is unavailable. Prompts appear in italics as natural prose, without ingredient labels or displayed results.

## Edit

- `index.qmd`: slide copy, HTML structure, source links, and speaker notes.
- `styles/theme.scss`: the reference deck's font and palette.
- `styles/slides.css`: layouts, typography, and transitions.
- `components/slides.js`: navigation and interactions.
- `assets/workshop-data.js`: prepared data examples and illustrative expected-passenger scores.
- `DESIGN.md`: the working design and writing rules for subsequent edits.

`../CONTENT.md` is the user's outline. The rendered deck is built from `index.qmd`; editing the outline does not automatically change the HTML. Edit the source rather than the generated `index.html`.

## Environment and rendering

Use the **networkcc** environment for Python and Quarto. Quarto and the Python Playwright package were installed there for this work.

From the repository root:

```sh
conda run -n networkcc python slides/scripts/prepare_data.py
cd slides
conda run -n networkcc quarto render index.qmd
```

For live editing:

```sh
conda run -n networkcc quarto preview index.qmd
```

For a basic localhost preview or browser speaker view, from `slides/`:

```sh
conda run --no-capture-output -n networkcc python -m http.server 8768 --bind 127.0.0.1
```

Then open `http://127.0.0.1:8768/`. The server is optional; the single HTML file is the deliverable.

## Data and teaching assumptions

Slide 4 uses the prepared January–September 2025 TTC log: 708 positive-delay entries at 15 stations, on weekdays in the selected time windows. The three displayed rows are real, not simulated. The script records source CSV checksums in `assets/workshop-data.js`. Training and later-month testing are discussed at the end; Slide 4 has no testing-set or prediction-table section.

Each row describes a recorded delay entry: date, time, station, reported issue and delay minutes. Related entries can describe the same underlying incident. See `../ttc_case/README.md` for the extraction limitations and station mapping policy. The underlying data files are retained; the slide generator embeds only the delay-log examples.

Slide 3 asks students to select exactly three station–time pairs, with no team-size or staffing-budget inputs. The expected passengers needing help are **artificial demonstration scores**, not TTC passenger counts or fitted predictions. Their sum represents passenger journeys at the chosen stations and times, rather than unique people. The visible “Illustrative estimates” caption identifies these values. Real passenger estimates would need a separate passenger-volume source or an explicit conversion assumption; the delay logs alone support predicting recorded disruptions. A station can be selected in more than one window. The source TTC data and workbook remain unchanged by this slide simplification.

Slide 5 is a deterministic illustration, with no model API connection. Token probabilities are invented for explanation. A word-sized chunk is used for readability; real tokenization may split words. Model families are examples rather than a ranking. Frontier capability and open weights are separate dimensions.

Slide 8 uses summaries generated by `scripts/prepare_data.py`: data-quality checks, the total row count, and the number of distinct standardized stations. Slide 10 shows prompts only; instructor reference counts remain in its speaker notes. Counts describe recorded entries and station names. Slide 9 adapts OpenAI’s prompting guidance into four classroom ingredients; it is a useful starting structure, not a universal optimum. Charts and comparisons are reserved for the later pattern-identification section.

Slide 6 uses “one-shot” informally to mean one request for a final result. The notes distinguish this from one-example prompting. The exercises are discussion prompts rather than a universal rule for each task.

## References and image credit

- [OpenAI prompt engineering](https://developers.openai.com/api/docs/guides/prompt-engineering): instructions, context, clear sections, and examples for Slide 9.
- [TTC Subway Delay Data](https://open.toronto.ca/dataset/ttc-subway-delay-data/): real records. Contains information licensed under the [Open Government Licence - Toronto](https://open.toronto.ca/open-data-license/).
- [Qwen Key Concepts](https://qwen.readthedocs.io/en/stable/getting_started/concepts.html): autoregressive token generation and model access.
- [OpenAI model catalogue](https://developers.openai.com/api/docs/models/all): GPT and gpt-oss examples.
- [Claude models overview](https://platform.claude.com/docs/en/models/overview): Claude example.
- [Kipling station photograph](https://commons.wikimedia.org/wiki/File:Kipling_TTC_end_of_the_line.jpg): Buddahbless, 14 April 2009, [CC BY 2.0](https://creativecommons.org/licenses/by/2.0/). Original retained at `assets/photos/kipling-station.jpg`, cropped in the layout. The photograph illustrates the location, not a recorded disruption.
- Base theme: the user's supplied deck in `../format_slides/Presentation_NetworkChanceConstraints/`.
- University of Toronto Scarborough Management logo: matches the user's supplied branding; extracted from the university's [recruitment document](https://www.poms.org/sites/default/files/2023-10/University%20of%20Toronto%20Scarborough%20%28UTSC%29%20.pdf), without changing its proportions or colours.

Full context and source links are also in each relevant slide's speaker notes. Web references were checked on 7 November 2026.

## Browser checks

From `slides/`, with Google Chrome installed:

```sh
conda run -n networkcc python scripts/check_slides.py
```

Checks cover exactly twenty-one slides, animation builds, forward/back navigation, delay-log examples and the training CSV link, the three-pair selection limit and passenger total, token generation/reset, exercises, basic data questions, prompt-copy fallback, keyboard interaction, offline assets, and content fit at common screen sizes. Screenshots and the test report go to `/tmp/mta-workshop-slide-qa/`.

For phone regression checks, install the WebKit browser with `conda run -n networkcc python -m playwright install webkit`, then run `conda run -n networkcc python scripts/check_mobile.py` from `slides/`. This checks portrait and landscape touch interactions in Chromium and WebKit, including slide 3's selection grid and the chart controls. Screenshots go to `/tmp/mta-workshop-mobile-qa/`.

## Later-month downloads

Slide 19 embeds downloadable October–December 2025 CSVs so they also work offline. `assets/data/ttc_testing_log_oct_dec_2025.csv` contains 229 positive-delay records with the training log schema; `assets/data/ttc_testing_windows_oct_dec_2025.csv` contains 2,970 windows with observed outcomes, including no-record windows. Both are regenerated from the frozen instructor audit by `scripts/prepare_data.py`, with disjoint dates and reconciled minute totals. Use outcomes only to evaluate predictions made beforehand.
