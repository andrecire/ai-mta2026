# Slide content organization

This outline reflects the current twenty-one slides in `slides/index.qmd`, including their interactions. Add new slide sections below to continue the workshop. Changes here guide future slide edits; they do not automatically update the rendered presentation.

## General instructions

- Keep slides short, clean, and direct, with little text.
- Use pictures, purposeful animations, and interactivity. Avoid expressions such as “This is not X. This is Y.”
- Keep a visible **Contents** button in the bottom-left corner. It opens a slide list for direct navigation.
- Place a small **Tools** button beside Contents: Generate PDF, Full screen, Slide overview, and Back to first slide. PDF opens a separate print view with revealed content and example charts, then the browser's Save as PDF dialog. Keep both controls discreet and hide them in the PDF.
- Put a thin line below every title. Use the University of Toronto Scarborough Management logo in the footer.
- Use navy text, teal emphasis, and orange highlights. Keep generous whitespace.
- Reveal elements with presenter-controlled clicks. Keep transitions smooth and respect reduced-motion preferences.
- Put source details, qualifications, and teaching notes in speaker notes where possible.
- Use the prepared TTC dataset for the workshop. Discuss model training at the end; do not introduce a testing set in these opening slides.
- Save charts, station/time comparisons, and delay-duration questions for the later pattern-identification section.

## Content

### Slide 1: Artificial Intelligence for Data Analysis

- Opening title: “Artificial Intelligence for Data Analysis”.
- Event: “Management Technology Association Workshop”, with “November 2026” directly below.
- Presenter: Andre A. Cire.
- Contact: andre.cire@rotman.utoronto.ca, linked to email.
- Large title, thin divider, and the existing University of Toronto Scarborough Management logo.
- All content appears immediately.
- An enlarged four-stage loop on the right connects data, AI, insights, and technology. A moving signal and sequential highlights suggest an iterative process. Small planets orbit the loop, with more light triangles, planets, diamonds, and squares moving around the title and presenter details and drifting through the surrounding whitespace. Keep the title and contact details on the left, and show a static diagram for reduced-motion preferences.

### Slide 2: We start with a problem

- Show a photograph of a TTC train at Kipling station, with image credit.
- Main statement: “Subway delays leave passengers needing help.”
- Examples, each with a small animation beside its description: crowded platforms (people gathering), door problems (obstructed doors), and weather disruptions (rain).
- Closing question: “Where and when should extra support go?” Make it bold and prominent, with “Where” and “when” in light orange and the rest in black.
- Source: [TTC Subway Delay Data](https://open.toronto.ca/dataset/ttc-subway-delay-data/). Door and weather examples summarize actual recorded reasons; crowded platforms illustrate a possible consequence of delays.

**Clicks:** Start with the title and footer only. Reveal the picture, main statement, each example separately, then the closing question. Show the data source with the weather example.

### Slide 3: Our goal today

- Role: “TTC hired you to assign support teams.”
- Objective: “Place teams where and when they maximize the number of passengers helped.”
- Your decision: choose **3 station–time pairs**. Each time window lasts **2 hours**.
- Show an interactive table: 15 stations as rows; example windows 07–09, 12–14, and 16–18 as columns.
- Selecting a cell updates “Expected passengers needing help” on the left. Allow up to three selections, deselection, and Reset. A station can be selected in more than one window.
- Label passenger values as illustrative estimates. The delay logs do not contain passenger counts; these demonstration scores are artificial.
- Show the two stages in orange: **Prediction:** “How many passengers may need help?” **Optimization:** “Which three pairs should we choose?”
- Keep team sizes and staffing budgets outside this simplified case.

**Clicks:** Reveal the assignment, objective, decision, duration, passenger total, grid, prediction, and optimization separately. Grid selections do not advance the slide.

### Slide 4: Data

- Explain: “When TTC records a subway delay, it logs the time, station, reported issue, and delay duration.”
- “One row = one recorded delay entry.”
- Show three real sample entries with Date, Time, Station, Reported issue, and Delay (min), alongside the City of Toronto Open Data source.
- Describe the prepared extract: **708 positive-delay log entries**, **15 stations**, weekdays in **January–September 2025**, within the selected time windows.
- State that records with zero delay minutes have been removed.
- Include a working **Download CSV** link for the January–September 2025 training log (708 records), available online and offline.
- Takeaway: “Turn evidence into actions.”
- Follow with: “AI will help us inspect the data, make predictions, and compare decisions.”

**Clicks:** Reveal the introduction, row definition, table with source, sample caption, count with station/date coverage, CSV download, takeaway, and AI explanation separately.

### Slide 5: Leveraging AI tools

- Introduction: “To use them effectively, we need to understand how they work.”
- Intuition: “Predict the next token based on all information so far, and pick the most likely next one.”
- Illustrate the sequence: text so far → neural network → possible next tokens.
- Starting text: “The next train arrives in”. Explain that a token is a word or part of a word.
- Use a colored neural network with activation moving from left to right. On its first reveal, automatically add “five” to the sentence when the animation finishes, and show the options that produced it: “five”, “two”, and “ten”. Keep that table until the next Generate click, which adds “minutes” and shows “minutes”, “seconds”, and “hours”.
- Provide **Generate next token** and **Reset** buttons. Keep probabilities labelled illustrative and remove any blinking typing cursor.
- Show frontier model families: **GPT / Claude**, with “Advanced general-purpose capabilities.”
- Show open-weight examples: **Qwen / gpt-oss**, with “Downloadable weights, subject to a licence.”
- Closing note: “Capability and openness are separate dimensions.”

**Clicks:** Reveal the introduction, intuition, text/definition, neural network, controls, frontier examples, open-weight examples, and closing note separately. Each Generate action waits for activation before updating the text and predictions.

**Teaching note:** This is a simplified illustration of next-token generation. Real systems can sample tokens rather than always selecting the most likely one.

### Slide 6: Should we just “one-shot”?

- Define the workshop’s use of one-shot: “That is, simply upload the data and ask for the final recommendation in one prompt.”
- Compare the approaches in a table:

| Dimension | One shot is best when... | Step by step is best when... |
| --- | --- | --- |
| Risk | Low stakes, easy to check | Consequences call for explicit checks |
| Differentiation | A standard, common answer is enough | Your framing and assumptions add value |
| Complexity | Simple and short | Answers are long, multi-layered |
| Understanding | Details can be easy to miss | Understand choices and intermediate results |
| Effort | A fast starting point | More interaction and judgement |

- Closing message: “You define the objective, assumptions, and checks. AI can support every step.”
- Then replace the comparison with three discussion examples on the same slide: summarize an event invitation; choose TTC stations and times; enter an analytics competition where other teams have comparable AI models.
- Each example offers **One prompt** and **Step by step** choices with feedback. Include **Back to the comparison**.

**Clicks:** For each row, first reveal only the dimension label, then reveal both column values together on the next click. Keep earlier rows visible. After Effort, reveal the closing message, then the discussion examples.

### Slide 7: Data analysis process

1. **Understand the data:** “What does each row mean?” Animate a highlighted data row and check mark.
2. **Identify patterns:** “What changes by station or time?” Animate growing bars.
3. **Make predictions:** “What might happen next?” Animate a projected continuation with an uncertainty band.

- Underneath: “Visualize what you find. Explain what it means.”
- Reinforce: “Visualization and interpretability matter at every step.”
- Treat the icons as schematic illustrations rather than measured TTC results.

**Clicks:** Reveal one process step at a time, then the principle underneath.

### Slide 8: Understand the data

1. **Read rows and columns:** “Explain one entry in plain language.” Show three real TTC entries and highlight the first row: at 08:13, a rail-related problem at Bloor-Yonge was logged with a 9-minute delay.
2. **Check units and counts:** “Minutes measure delay. Rows count recorded entries.” Highlight the delay-minutes column. Show 708 entries across 15 stations, and note that passenger counts require another source.
3. **Look for errors:** “Check missing values, repeated entries, and unexpected values.” Show the extract’s checks: 0 missing core values, 0 exact repeat rows, and a longest recorded delay of 143 minutes. “Investigate before changing it.”

**Clicks:** Reveal one step and its associated example per click. Match light fills on both sides: blue-grey for rows and columns, warm cream for units and counts (including the delay column), and pale green for error checks. Keep the fills visible as each step is added. Use slower slide transitions, approximately 750 ms fades and 850 ms table highlights. Backward navigation reverses the steps.

### Slide 9: Constructing a useful prompt

- Introduction: “Make the task, information, and expected answer clear.”
- Introduce four ingredients, each paired with a simple TTC example:

| Ingredient | Guiding question | Example |
| --- | --- | --- |
| Task | What should AI do? | Count the rows in the file. |
| Context | What information should it use? | Use the attached TTC delay CSV. |
| Output format | What should the answer look like? | Return the count in one sentence. |
| Checks | What rules should it follow? | Exclude the header. Count every data row. |

- Closing message: “Start simple. Check the answer. Refine the prompt.”
- Show the assembled prompt in italics: “Count the rows in the file using the attached TTC delay CSV. Return the count in one sentence. Exclude the header and count every data row.”
- Source: [OpenAI’s prompting guidance](https://developers.openai.com/api/docs/guides/prompt-engineering).
- Explain in speaker notes that this is a useful classroom structure, with no universally optimal template.

**Clicks:** Reveal the introduction, each ingredient with its example, then the closing guidance and source.

### Slide 10: Hands-on: understand the TTC data

- Introduction: “Attach the CSV. Ask one question. Check the answer.”
- Provide three question tabs, each showing a copyable prompt in italics across a spacious single-column layout. Use natural prose without Task, Context, Output, or Checks labels.
- Show only the prompts; students generate and check the answers themselves.

**What is each column?**

> *Explain every column in the attached TTC delay CSV in plain language. Return a table with each column’s name, meaning, and unit. Flag any uncertain meanings for verification.*

**How many rows?**

> *Count the rows in the attached TTC delay CSV. Return the count in one sentence. Exclude the header and count every data row without filtering.*

**How many stations?**

> *Count the distinct stations using the lowercase station column in the attached TTC CSV. Return the count and an alphabetical station list. Count each station name once and report any blank values separately.*

- Closing message: “Be precise about what to explain, what to count, and which column to use.”
- Keep the TTC data source visible. These are copyable examples rather than live AI requests.

**Clicks:** Reveal the introduction, interactive workspace, then the closing message. Tabs change the question without advancing the slide. **Copy prompt** copies the current text or selects it for manual copying when clipboard access is unavailable.


### Slide 11: Identifying patterns

Show a repeating cycle: **Questions → Analysis → Insights → new questions**.

- **Questions:** “Explore distributions and relationships across one or more columns.” Each question becomes a prompt. Use a question-mark speech bubble.
- **Analysis:** “Use a plot or a statistic to answer the question.” Examples: mean, standard deviation, correlation. Use a chart icon.
- **Insights:** “Explain what you learned and what deserves a closer look.” Ask: “What will you ask next?” Use a lightbulb icon.
- Place the question-mark speech bubble, chart, and lightbulb directly on the circular path in place of numbered nodes, with the same icons repeated beside the corresponding labels on the right. The center reads “Ask. Learn. Ask again.” A moving marker travels clockwise around the complete circle.
- Keep the diagram conceptual; the icons do not represent computed TTC results. Speaker notes include a TTC example and guidance on choosing statistics appropriate to the variables.

**Clicks:** Reveal Questions, Analysis, Insights, then the closing arc and center message. Animate each incoming arrow drawing toward its destination as that stage appears. Draw the arrowhead at the end. After the final arrow back to Questions finishes, animate the flow around the circle in a gentle repeating loop. Stop the animation when leaving the slide or reversing the final click. Respect reduced-motion settings.


### Slide 12: Example: delay minutes by station

- Ask: “How many delay minutes were recorded at each station?”
- Sum `Min Delay` by the standardized lowercase `station` field, using all 708 entries and all 15 stations. The sum across stations is 4,479 recorded minutes.
- Show two selectable examples: **Bar chart · Compare stations** and **Pie chart · Share of the total**.
- The horizontal bars start at zero, are sorted largest first, and show station totals in minutes. Highlight the largest total in orange.
- The pie shows all 15 stations, with percentages beside the slices, connecting lines, and a color legend identifying stations. Explain that small slices are harder to compare.
- Alongside each example, show a short copyable prompt in italics. Assume the data is already available in the conversation.
- Bar prompt: “Draw a bar plot that sums the delay minutes of all events at each station. Use different colors.”
- Pie prompt: “Draw a pie chart that sums the delay minutes of all events at each station and shows each station’s share. Show percentages and use different colors.”
- Keep the TTC source visible. Describe the values as sums of recorded delay minutes; they do not measure passenger waiting time or deduplicated network downtime.

**Clicks:** Reveal the question, then the chart-selection tabs and Show example button, then the prompt and Copy prompt button. Keep the chart hidden until Show example is clicked. Selecting either tab hides the chart again, allowing a pause before revealing that example. Leave extra vertical space between the question and tabs.


### Slide 13: Example: distributions

- Ask whether the day of the week matters for delay duration.
- Show a copyable prompt asking for weekday histograms with matching bins and axes, percentages, and different colors.
- Present five histograms with shared one-minute bins and percentage axes.
- Leave data-processing observations for class discussion; omit the outlier explanation from the projected slide.

**Clicks:** Question, then prompt; Show example reveals the histograms.

### Slide 14: Example: correlation and relationships between columns

- Ask whether longer delays go with longer gaps between trains.
- Draw one dot per event: Min Delay on the horizontal axis, Min Gap on the vertical axis.
- Copyable prompt: “Plot Min Delay against Min Gap, with delay on the horizontal axis. Calculate Pearson’s correlation and explain it. Add a zoomed view while keeping all entries.”
- Show all 708 real entries and Pearson r = 0.989, a strong positive association. Explain that r ranges from −1 to +1 and does not establish causation.
- Provide All entries and Zoom: 0–20 min buttons. Report entries outside the zoom; keep the coefficient based on all entries. Overlapping dots share coordinates.
- Notes discuss the related measurements, the effect of extreme observations, and why an event’s observed gap is not an input available for forecasting that event beforehand.

**Clicks:** Question, relationship, prompt; Show example reveals the plot and coefficient. View buttons do not advance the slide.

### Slide 15: Plot examples

- Show nine common plot types in a 3×3 grid with small schematic animations, one per click.
- Bar chart: compare categories, such as minutes by station.
- Line chart: track change over time, such as weekly recorded minutes.
- Histogram: see the distribution of a numeric variable, such as minutes per recorded entry.
- Scatter plot: relate two numeric columns, such as delay minutes and train gap.
- Box plot: compare medians and spread, such as duration by weekday.
- Pie chart: show parts of a whole, such as each station’s share.
- Heatmap: compare stations and time windows using color for a numeric value.
- Stacked bar chart: compare totals and composition, such as delay minutes by cause and station.
- Bubble chart: show a third variable by size, such as delay, train gap, and entry count.
- Close with “Choose the plot that answers your question.”

### Slide 16: Your turn!

- Ask students to find one insight that could help choose stations and time windows.
- Ask a question: choose the columns and write a prompt.
- Show the evidence: a plot or statistic, with correct labels and units.
- Explain the insight: what did you learn, and why does it matter for the decision?
- Provide a sentence frame: “We found ___. This matters for choosing stations and times because ___. One limitation is ___.”
- Suggest about four minutes of pair work in speaker notes.

**Clicks:** Reveal the challenge, each of the three steps, then the explanation template.

### Slide 17: What are we predicting?

- Keep the title and opening text: for each station–time pair, how many passengers would a team help, on average?
- Keep the bridge: predict recorded delay minutes → apply a passenger assumption → compare choices.
- Show the three animated methods: historical average, linear regression, and deep neural network.
- Connect regression inputs to the relationships explored earlier.
- Remove the numerical baseline example, passenger slider, and regression formula.
- End with only “Simple is enough.”
- Notes retain the passenger-proxy assumption and the need to check and explain predictions.

**Clicks:** Target, bridge, each of the three methods, then the closing line.

### Slide 18: Example: a simple moving average

- Explain: average the most recent periods to predict the next one.
- Use a three-month moving average of monthly average recorded minutes for a fixed station and time window.
- Show real Bloor-Yonge 07–09 monthly averages from January–September 2025, highlight July–September, and draw the October forecast in orange.
- Calculation: (0.48 + 0.62 + 0.73) ÷ 3 ≈ 0.61 minutes per weekday window. Include windows with no recorded delay; compute with full precision.
- Copyable prompt: “For each station and time window, predict October’s average daily delay minutes using the July, August, and September averages. Include weekdays with no recorded delay as zeros. Show the calculation and explain it. Do not use October data.”
- Explain that the averaging window moves forward after each completed month.

**Clicks:** Definition, example and picture, then prompt.

### Slide 19: Check predictions on future data

- Explain a testing set: later observations not seen when making the prediction.
- Show January–September 2025 for training and October–December 2025 for testing.
- Freeze the rule, compare predictions with reality using average absolute error in minutes, and compare with a simple baseline.
- Check stations, time windows, units, dates, and missing reporting.
- Provide working downloads for October–December: 229 positive-delay records in the same format as the training CSV, plus 2,970 station–time windows including no-record windows.
- Say students may need to adjust the prompt, column names, or date filters manually.
- Notes explain rolling one-month-ahead evaluation, avoiding future information, consistent units, and keeping a new period untouched after tuning.

**Clicks:** Definition, timeline, each of three steps, then download links and manual-adjustment note.

### Slide 20: A web interface for the decision

- Make predictions easy to inspect and choices easy to compare.
- Specify the task: select three station–time pairs.
- Show the evidence: predictions, assumptions, and a comparison.
- Build with an LLM: describe behavior, test it in the browser, then refine.
- Include an interactive sketch with six example pairs, a three-pair limit, expected passenger total, Reset, and Select best 3. Label the scores as historical average minutes × 10 assumed passengers per minute.
- Copyable prompt: “Build a web interface from a table of station–time predictions. Let me select exactly three pairs, show the expected passengers helped, and compare with the best three. Display assumptions, add Reset, and test the totals and selection limit.”
- Explain that a complete interface would include all 45 pairs. This sketch compares alternatives under assumptions; observing real outcomes is needed to evaluate actual effectiveness.

**Clicks:** Reveal the introduction, task with interactive sketch, evidence, build workflow, then the prompt and Copy prompt button.


### Slide 21: Thank you!

- Display a large “Thank you!”.
- Next steps: “Continue exploring. Ask new questions. Try different tools. Explain what you find.”
- Repeat Andre A. Cire and andre.cire@rotman.utoronto.ca.
- Match the opening slide and leave all content visible.
