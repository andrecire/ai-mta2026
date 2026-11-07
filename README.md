# Artificial Intelligence for Data Analysis

Management Technology Association Workshop · November 2026  
Andre A. Cire · andre.cire@rotman.utoronto.ca

An interactive, 21-slide workshop using Toronto TTC subway delay data to explore data, identify patterns, make predictions, and choose station–time assignments.

**[Open the workshop slides](https://www.andre-cire.com/ai-mta2026/)** · [GitHub repository](https://github.com/andrecire/ai-mta2026)

## Slides and data

- Edit the presentation in [slides/index.qmd](slides/index.qmd).
- Maintain future slide ideas in [CONTENT.md](CONTENT.md).
- Open [slides/index.html](slides/index.html) locally for the self-contained offline presentation.
- Training CSV: [January–September 2025](slides/assets/data/ttc_training_log_jan_sep_2025.csv), 708 positive-delay records.
- Testing CSV: [October–December 2025](slides/assets/data/ttc_testing_log_oct_dec_2025.csv), 229 positive-delay records.
- Testing window totals: [October–December 2025](slides/assets/data/ttc_testing_windows_oct_dec_2025.csv), 2,970 windows including zero-delay windows.

Download buttons work on GitHub Pages and in the standalone offline HTML. The repository contains the public TTC source snapshot and instructor calculations for reproducibility; the deployed website contains only the presentation and its three downloadable CSVs. Later-month outcomes are intended for the testing exercise.

## Edit and publish

Use the `networkcc` environment locally:

```sh
conda run -n networkcc python slides/scripts/prepare_data.py
cd slides
conda run -n networkcc quarto render index.qmd
```

For automatic local refresh, run `conda run --no-capture-output -n networkcc quarto preview index.qmd --port 8768 --no-browser` from `slides/`.

Commit and push changes to `main`. The [Pages workflow](.github/workflows/pages.yml) regenerates the data assets, renders the slides, and publishes them automatically. It can also be run manually from GitHub Actions. GitHub Pages uses **GitHub Actions** as its publishing source.

See [slides/README.md](slides/README.md) for presentation controls and verification commands, and [ttc_case/README.md](ttc_case/README.md) for data preparation, scope, and limitations.

## Attribution

TTC data is published through the [City of Toronto Open Data portal](https://open.toronto.ca/dataset/ttc-subway-delay-data/) under the [Open Government Licence – Toronto](https://open.toronto.ca/open-data-license/). Passenger estimates in the decision examples are illustrative, not measured ridership. Photo attribution is included in the slides; institutional logos retain their respective ownership.
