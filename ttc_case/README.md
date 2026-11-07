# TTC passenger-support workshop data

Prepared for the one-hour undergraduate AI and data analytics workshop.

The real-data task is to predict whether a positive-delay entry will be recorded at a station in a particular two-hour window. The decision task will select three station-time assignments for additional passenger support. This package prepares the observations; it does not solve the selection problem or invent passenger counts.

## Start here

- Open [the student workbook](../outputs/ttc_workshop/ttc_workshop_data.xlsx). It contains **Training**, **Candidates**, and **Dictionary** sheets, with filters and frozen headers.
- For an AI tool or Python, use [training_windows.csv](data/training_windows.csv) and [deployment_candidates.csv](data/deployment_candidates.csv).
- To demonstrate cleaning and aggregation, start with [training_log_entries.csv](data/training_log_entries.csv). It contains 708 positive-delay log entries, preserves their original columns, and adds explicit mappings and provenance. The 1,074 zero-minute training entries have been removed from this student file.
- Keep `instructor/` and the complete `raw/` download out of the initial student handout. They contain held-out outcomes.
- Student training and testing delay-record CSVs omit `positive_delay` and `identical_record_group`; these flags remain in the instructor audit.

## Scope

| Item | Choice |
|---|---|
| Real observation period | 1 January-31 December 2025 |
| Training period | January-September 2025: 195 weekdays, 8,775 station-time observations |
| Held-out evaluation period | October-December 2025: 66 weekdays, 2,970 station-time observations |
| Candidate stations | 15, fixed as a geographical teaching sample, not selected by held-out performance |
| Time windows | 07:00-09:00, 12:00-14:00, 16:00-18:00, Toronto local time |
| Candidate assignments per day | 45: 15 stations x 3 windows |
| Historical deployment exercise | Monday, 6 October 2025; 45 candidate rows with no outcomes |
| Primary prediction target | `has_recorded_delay`: at least one matching entry with `Min Delay > 0` |

The stations are Bloor-Yonge, Union, St George, Kennedy, Finch, Kipling, Eglinton, Dundas, Warden, Victoria Park, Sheppard-Yonge, Don Mills, Islington, Spadina, and Wilson. Historical names are retained. `S01`-`S15` are teaching identifiers, not official TTC IDs. See [stations.csv](data/stations.csv).

The October exercise is a retrospective forecast made with data through 30 September. It is not a forecast of current TTC operations. The official snapshot also contains 2026 data, which is preserved in `raw/` but excluded from the exercise.

## Sources and attribution

Source: Toronto Transit Commission, published through the [City of Toronto Open Data portal, TTC Subway Delay Data](https://open.toronto.ca/dataset/ttc-subway-delay-data/). Retrieved on **7 November 2026**. Contains information licensed under the [Open Government Licence - Toronto](https://open.toronto.ca/open-data-license/).

The official snapshot covers 1 January 2025-30 September 2026 and contains 47,915 rows. Its 2025 portion contains 25,737 rows and at least one network-level entry on every calendar date. Network coverage is a useful download check, not proof of complete station reporting.

[source_manifest.json](source_manifest.json) records exact resource URLs, resource IDs, downloaded byte counts, SHA-256 checksums, and the publisher's refresh metadata. The unmodified downloads and CKAN package metadata are in `raw/`. The downloaded TTC readme defines `Min Delay` as delay to subway service and `Min Gap` as time between trains.

## Data files

| File | Use |
|---|---|
| `data/training_windows.csv` | Main prediction dataset: one row per weekday, station and time window; 8,775 rows |
| `data/deployment_candidates.csv` | The 45 assignments available on the historical target Monday; features only |
| `data/test_windows_features.csv` | All 2,970 held-out observations with outcomes removed |
| `data/training_log_entries.csv` | 708 positive-delay training log rows; zero-minute entries removed; original fields plus mapping/provenance |
| `data/stations.csv` | The 15 teaching stations and their subway lines in 2025 |
| `data/delay_codes.csv` | Official code descriptions with a punctuation-encoding repair |
| `data/data_dictionary.csv` | Definition and modelling role of each panel column |
| `instructor/test_windows_with_outcomes.csv` | Held-out features and outcomes, to evaluate predictions after they are frozen |
| `instructor/all_windows_2025.csv` | Full 11,745-row panel for instructor inspection |
| `instructor/record_audit_2025.csv` | All 2025 source rows, mapping decisions, duplicate flags, and exclusion reasons |
| `instructor/station_label_mapping.csv` | Every original 2025 location label and its inclusion/mapping decision |
| `instructor/network_date_coverage.csv` | Network-level date coverage check |
| `instructor/training_station_time_summary.csv` | Training-only counts and rates for a potential heatmap |
| `instructor/quality_report.json` | Reconciliations, missing-code counts, and data-quality checks |

`instructor/workbook_data.json` and `instructor/previews/` are export/visual-check intermediates, not student datasets.

## Cleaning and aggregation rules

1. **Freeze the year and split by date.** Use 2025 only; train before 1 October and evaluate from 1 October onward. Do not shuffle rows across the split. Fix stations, windows and cleaning rules before evaluating predictions.
2. **Map locations conservatively.** Normalize whitespace/case and match an explicit list of station aliases. Clearly identifiable platform annotations are also included. Combine the two line-specific names for interchange stations such as Bloor-Yonge and St George. Do not fuzzy-match station names or allocate a line-wide disruption to every station.
3. **Exclude ambiguous locations.** Approaches, departing trains, yards, tail tracks, station-to-station ranges and unrecognized annotations are excluded from the panel. Other stations are outside this teaching sample. All excluded records remain in the audit. This deliberately conservative scope can undercount disruption activity associated with a selected station.
4. **Use local event start times.** A window includes its start and excludes its end: 08:59 belongs to 07:00-09:00, while 09:00 does not. An entry is counted in the window where its recorded start falls. Delays beginning before a window and continuing into it are not allocated to that window.
5. **Use weekdays only.** Monday-Friday observations are retained, including weekday public holidays. No claim is made that every weekday has a normal operating schedule. Weekend service, holiday indicators and special-event calendars can be later extensions.
6. **Remove zero-minute entries from the student log file.** `training_log_entries.csv` retains only entries with `Min Delay > 0`: 708 retained and 1,074 removed. The unmodified source and instructor audit preserve all records. The prediction panel retains no-delay windows so that disruption probabilities have the correct denominator. Its diagnostic `log_entry_count` still counts all original matching entries, including zero-minute entries; `positive_delay_count` reconciles to the filtered student log file. `Min Gap` is not used as delay minutes. Include all recorded cause codes for this general passenger-support case, rather than assuming staff prevent particular causes.
7. **Preserve identical-looking records.** There are 57 rows beyond the first identical record in the 2025 source, and 13 in the eligible extract. They are retained and flagged because there is no unique incident ID that proves they are duplicates. They do not change the binary target. Counts and minute sums describe records, not unique events.
8. **Join official descriptions without guessing.** Three 2025 codes are absent from the downloaded dictionary (`PUTO`, `TFPD`, `XXXXX`); `PUTO` appears in the selected extract. Preserve the code, mark its description unavailable, and retain its recorded delay. Missing direction/line does not disqualify an otherwise identified station record.
9. **Build a complete weekday grid.** Create every combination of 261 weekdays, 15 stations and 3 windows. Match log entries to each row. A row with no matching records receives zero counts and a zero target. See the interpretation below.

## Meaning of a zero and other limits

**`has_recorded_delay = 0` means no positive-delay record matched the station/time rules. It does not prove that there was no disruption or that the station was open.** The source does not establish station-level reporting completeness, scheduled closures, actual passenger exposure, or a complete inventory of affected stations. Network-wide date coverage cannot resolve those limitations.

The teaching model therefore predicts the probability of a **recorded positive-delay entry**, used as a proxy for passenger-support need. If the case is later presented as an operational deployment recommendation, station opening/closure calendars and reporting coverage would need to be joined before interpreting zeros as available, disruption-free service windows.

The event location can differ from the places where passengers need assistance. A delay can affect multiple stations. Summed `Min Delay` is neither unique disruption duration nor passenger-delay minutes; overlapping records may count related events repeatedly. These are material reasons to use the binary target for the first exercise.

## Prediction workflow

Use only `date`, `day_of_week`, `station_id`/`station`, and `time_window` as inputs. `station_id` is categorical, not a numerical measure. Treat time windows as categories rather than calculating a Pearson correlation with clock time. Calendar variables may be derived from the date.

The four outcome columns are known only after the window occurs. Do not use `log_entry_count`, `positive_delay_count`, or `recorded_delay_minutes` as inputs when predicting `has_recorded_delay` for that same window. Historical log code, vehicle and delay fields are available for exploration, not as known attributes of a future event.

A suitable first prediction is the historical proportion of windows with a positive-delay entry at each station and time. Students can then condition on weekday or compare a regression/classification model. There are only 39 Mondays per station-window in the training period, so weekday-specific rates can be unstable. Keep sample counts visible and consider pooling information across weekdays.

Freeze predictions before opening the held-out labels. Evaluate probability predictions over the whole held-out period, for example with mean squared probability error (Brier score), and compare with the constant training-set event rate. About 6.9% of training windows have a positive target, so classification accuracy alone is misleading: predicting zero everywhere looks accurate. The single deployment Monday is for the decision demonstration, not enough to judge a model.

## What remains a teaching assumption

The real-data package contains **no invented passenger counts, staffing costs, team sizes, or estimates of staff effectiveness**. These should be added in a separately labelled assumptions table when the decision exercise is finalized.

The agreed proposed decision is to choose three of the 45 station-time assignments under a staffing budget. A possible benefit proxy is predicted disruption probability multiplied by assumed passenger volume and an assumed help fraction. That formula is a scenario assumption, not an impact estimate from these records. The allocation rules can also specify whether the same station may receive support in multiple windows.

## Rebuild and validation

From the repository root, with Python 3.10+ and pandas installed:

```sh
python3 ttc_case/scripts/prepare_data.py
```

The script reads the frozen downloads and makes no network requests. It regenerates the CSVs, source manifest, quality report and typed Excel-export intermediate. It validates date/time parsing, weekday consistency, nonnegative delays, unique grid keys, temporal separation, all 15 stations, all 45 candidates, and exact reconciliation of log counts, positive counts and recorded minutes to the included source rows.

The Excel export uses `@oai/artifact-tool`:

```sh
node ttc_case/scripts/export_workbook.mjs
```

The local `scripts/node_modules` link points to the available Codex runtime dependencies; another computer needs that package available through its own environment. The exported workbook is data-only: no regression, recommended assignments or synthetic operating assumptions have been prefilled.
