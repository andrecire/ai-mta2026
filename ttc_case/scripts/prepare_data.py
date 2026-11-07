"""Build the TTC teaching extract from the frozen official downloads.

Run with Python 3.10+ and pandas. No network requests or model fitting.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW, DATA, AUDIT = (ROOT / p for p in ("raw", "data", "instructor"))
START, CUTOFF, END = "2025-01-01", "2025-10-01", "2025-12-31"
TARGET_DATE = "2025-10-06"  # A historical Monday, not a current forecast.
SOURCE_URL = "https://open.toronto.ca/dataset/ttc-subway-delay-data/"

# Fixed geographical teaching sample, not ranked using future outcomes.
# These labels and platform qualifiers are matched exactly, never fuzzily.
STATIONS = [
    ("S01", "Bloor-Yonge", "1;2", ["BLOOR STATION", "YONGE BD STATION", "YONGE STATION", "BLOOR YONGE", "YONGE-BLOOR", "YONGE AND BLOOR"]),
    ("S02", "Union", "1", ["UNION STATION", "UNION"]),
    ("S03", "St George", "1;2", ["ST GEORGE YUS STATION", "ST GEORGE BD STATION", "ST GEORGE YU STATION", "ST GEORGE STATION", "ST. GEORGE STATION", "ST GEORGE (YUS) STATIO"]),
    ("S04", "Kennedy", "2", ["KENNEDY BD STATION", "KENNEDY STATION", "KENNEDY"]),
    ("S05", "Finch", "1", ["FINCH STATION"]),
    ("S06", "Kipling", "2", ["KIPLING STATION", "KIPLING BD STATION", "KIPLING"]),
    ("S07", "Eglinton", "1", ["EGLINTON STATION", "EGLINTON"]),
    ("S08", "Dundas", "1", ["DUNDAS STATION", "DUNDAS"]),
    ("S09", "Warden", "2", ["WARDEN STATION", "WARDEN"]),
    ("S10", "Victoria Park", "2", ["VICTORIA PARK STATION"]),
    ("S11", "Sheppard-Yonge", "1;4", ["SHEPPARD STATION", "SHEPPARD-YONGE STATION", "SHEPPARD YONGE STATION", "SHEPPARD-YONGE", "SHEPPARDSTATION", "SHEPPARD - YONGE STATI", "SHEPPARD- YONGE STATIO"]),
    ("S12", "Don Mills", "4", ["DON MILLS STATION", "DON MILLS"]),
    ("S13", "Islington", "2", ["ISLINGTON STATION"]),
    ("S14", "Spadina", "1;2", ["SPADINA BD STATION", "SPADINA YUS STATION", "SPADINA STATION"]),
    ("S15", "Wilson", "1", ["WILSON STATION"]),
]
WINDOWS = [("07:00-09:00", 420, 540), ("12:00-14:00", 720, 840), ("16:00-18:00", 960, 1080)]
FEATURES = ["date", "day_of_week", "station_id", "station", "time_window"]
OUTCOMES = ["log_entry_count", "positive_delay_count", "has_recorded_delay", "recorded_delay_minutes"]


def csv(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False, lineterminator="\n", date_format="%Y-%m-%d")


def normalize(value: str) -> str:
    return " ".join(str(value).upper().split())


def map_station(label: str) -> tuple[str | None, str]:
    label = normalize(label)
    for station_id, _, _, aliases in STATIONS:
        if label in aliases:
            return station_id, "exact_station_alias"
    # Platform annotations are still clearly located at one station.
    # Approaches, tails, yards, ranges and ambiguous/truncated labels stay excluded.
    for station_id, _, _, aliases in STATIONS:
        for alias in aliases:
            if "STATION" not in alias or not label.startswith(alias):
                continue
            suffix = label[len(alias):].strip(" -([")
            if re.fullmatch(r"(?:PLAT[A-Z #0-9]*|P[12]|#?[12])\)?", suffix):
                return station_id, "station_platform_annotation"
        short = aliases[0].replace(" BD STATION", "").replace(" STATION", "")
        if re.fullmatch(re.escape(short) + r" (?:PLAT[A-Z #0-9]*|P[12])", label):
            return station_id, "station_platform_annotation"
    return None, "outside_sample_or_ambiguous_location"


def build() -> None:
    for folder in (DATA, AUDIT):
        folder.mkdir(parents=True, exist_ok=True)
    raw_path = RAW / "ttc-subway-delay-data-since-2025.csv"
    source = pd.read_csv(raw_path, keep_default_na=False)
    original_columns = list(source.columns)
    source["source_csv_row"] = range(2, len(source) + 2)
    parsed_dates = pd.to_datetime(source["Date"], format="%Y-%m-%d", errors="raise")
    source = source.loc[parsed_dates.between(START, END)].copy()
    source["date"] = pd.to_datetime(source["Date"], format="%Y-%m-%d")
    assert source["_id"].is_unique
    assert source["Time"].str.fullmatch(r"\d{2}:\d{2}").all()
    hours = source["Time"].str[:2].astype(int)
    minutes = source["Time"].str[3:].astype(int)
    assert hours.between(0, 23).all() and minutes.between(0, 59).all()
    source["minute_of_day"] = hours * 60 + minutes
    for col in ["Min Delay", "Min Gap"]:
        source[col] = pd.to_numeric(source[col], errors="raise")
        assert source[col].notna().all() and source[col].ge(0).all()
    source["day_of_week"] = source.date.dt.day_name()
    assert (source.day_of_week == source.Day).all()

    # Retain identical records: the source has no unique incident identifier that
    # would prove whether identical-looking entries represent the same event.
    key = [c for c in original_columns if c != "_id"]
    source["identical_record_group"] = source.duplicated(key, keep=False).astype(int)
    source["station_label_normalized"] = source.Station.map(normalize)
    mappings = {s: map_station(s) for s in sorted(source.station_label_normalized.unique())}
    source["station_id"] = source.station_label_normalized.map(lambda s: mappings[s][0])
    names = {s[0]: s[1] for s in STATIONS}
    source["station"] = source.station_id.map(names)
    source["station_match_rule"] = source.station_label_normalized.map(lambda s: mappings[s][1])
    source["time_window"] = ""
    for label, lo, hi in WINDOWS:
        source.loc[source.minute_of_day.ge(lo) & source.minute_of_day.lt(hi), "time_window"] = label
    source["positive_delay"] = source["Min Delay"].gt(0).astype(int)

    codes = pd.read_csv(RAW / "code-descriptions.csv", keep_default_na=False)
    assert codes.CODE.is_unique
    # Repair a confirmed UTF-8-as-Latin-1 punctuation artifact in descriptions.
    def repair(s: str) -> str:
        if "â" in s or "Ã" in s:
            try:
                return s.encode("latin1").decode("utf8")
            except (UnicodeError, ValueError):
                pass
        return s
    codes["DESCRIPTION"] = codes.DESCRIPTION.map(repair)
    descriptions = codes.set_index("CODE").DESCRIPTION.to_dict()
    source["code_description"] = source.Code.map(descriptions).fillna("Not listed in downloaded TTC code dictionary")
    source["exclusion_reason"] = "included"
    source.loc[source.time_window.eq(""), "exclusion_reason"] = "outside_three_time_windows"
    source.loc[source.date.dt.dayofweek.ge(5), "exclusion_reason"] = "weekend"
    source.loc[source.station_id.isna(), "exclusion_reason"] = "outside_sample_or_ambiguous_location"
    # Exact named station locations are used even if direction/line is missing.
    eligible = source.loc[source.exclusion_reason.eq("included")].copy()
    eligible = eligible.sort_values(["date", "Time", "station_id", "_id"])

    dates = pd.bdate_range(START, END)  # Includes weekday holidays, explicitly.
    index = pd.MultiIndex.from_product([dates, names, [w[0] for w in WINDOWS]], names=["date", "station_id", "time_window"])
    grouped = eligible.groupby(["date", "station_id", "time_window"]).agg(
        log_entry_count=("_id", "size"),
        positive_delay_count=("positive_delay", "sum"),
        recorded_delay_minutes=("Min Delay", "sum"),
    )
    panel = grouped.reindex(index, fill_value=0).reset_index()
    panel["has_recorded_delay"] = panel.positive_delay_count.gt(0).astype(int)
    panel["day_of_week"] = panel.date.dt.day_name()
    panel["station"] = panel.station_id.map(names)
    panel[OUTCOMES] = panel[OUTCOMES].astype(int)
    panel = panel[FEATURES + OUTCOMES].sort_values(["date", "station_id", "time_window"])
    train = panel.loc[panel.date.lt(CUTOFF)].copy()
    test = panel.loc[panel.date.ge(CUTOFF)].copy()
    candidates = test.loc[test.date.eq(TARGET_DATE), FEATURES].copy()

    csv(train, DATA / "training_windows.csv")
    csv(test[FEATURES], DATA / "test_windows_features.csv")
    csv(candidates, DATA / "deployment_candidates.csv")
    csv(test, AUDIT / "test_windows_with_outcomes.csv")
    csv(panel, AUDIT / "all_windows_2025.csv")
    csv(source, AUDIT / "record_audit_2025.csv")
    training_logs = eligible.loc[eligible.date.lt(CUTOFF) & eligible.positive_delay.eq(1)].copy()
    student_log_columns = original_columns.copy()
    student_log_columns.insert(student_log_columns.index("Code") + 1, "code_description")
    student_log_columns += ["station_id", "station", "time_window"]
    csv(training_logs[student_log_columns], DATA / "training_log_entries.csv")
    csv(codes[["CODE", "DESCRIPTION"]].rename(columns={"CODE": "code", "DESCRIPTION": "description"}), DATA / "delay_codes.csv")
    stations = pd.DataFrame([(a, b, c) for a, b, c, _ in STATIONS], columns=["station_id", "station", "subway_lines_2025"])
    csv(stations, DATA / "stations.csv")
    alias_table = source.groupby(["Station", "station_label_normalized"], dropna=False).size().rename("source_rows_2025").reset_index()
    alias_table["station_id"] = alias_table.station_label_normalized.map(lambda s: mappings[s][0])
    alias_table["station"] = alias_table.station_id.map(names)
    alias_table["mapping_rule"] = alias_table.station_label_normalized.map(lambda s: mappings[s][1])
    csv(alias_table, AUDIT / "station_label_mapping.csv")
    coverage = source.groupby("date").agg(network_log_entries=("_id", "size"), network_positive_delay_entries=("positive_delay", "sum")).reindex(pd.date_range(START, END))
    coverage.index.name = "date"
    assert coverage.notna().all().all(), "Missing network date: do not zero-fill without review"
    csv(coverage.reset_index(), AUDIT / "network_date_coverage.csv")

    dictionary = pd.DataFrame([
        ("date", "feature", "Local calendar date in the TTC record; yyyy-mm-dd."),
        ("day_of_week", "feature", "Derived weekday. Monday-Friday only; weekday holidays are retained."),
        ("station_id", "feature/key", "Teaching identifier S01-S15, not an official TTC identifier."),
        ("station", "feature", "Standardized historical station name; interchange platforms combined."),
        ("time_window", "feature", "Two-hour local window. Start included, end excluded."),
        ("log_entry_count", "outcome/audit", "Number of matching log rows, including zero-minute entries. Not unique incidents."),
        ("positive_delay_count", "outcome", "Number of matching log rows with Min Delay > 0. Identical-looking rows retained."),
        ("has_recorded_delay", "PRIMARY TARGET", "1 if positive_delay_count > 0, otherwise 0. Predict this using features only."),
        ("recorded_delay_minutes", "outcome", "Sum of reported Min Delay. Not passenger delay or deduplicated disruption duration."),
    ], columns=["field", "role", "definition"])
    csv(dictionary, DATA / "data_dictionary.csv")

    assert len(panel) == len(dates) * 15 * 3
    assert len(candidates) == 45 and len(candidates.station.unique()) == 15
    assert not panel.duplicated(["date", "station_id", "time_window"]).any()
    assert train.date.max() < test.date.min()
    assert panel.log_entry_count.sum() == len(eligible)
    assert panel.positive_delay_count.sum() == eligible.positive_delay.sum()
    assert panel.recorded_delay_minutes.sum() == eligible["Min Delay"].sum()
    assert (panel.has_recorded_delay == panel.positive_delay_count.gt(0)).all()
    assert (panel.positive_delay_count <= panel.log_entry_count).all()
    assert not panel.isna().any().any()
    assert set(train.station_id) == set(test.station_id) == set(names)
    assert training_logs["Min Delay"].gt(0).all()
    assert len(training_logs) == train.positive_delay_count.sum()
    assert training_logs["Min Delay"].sum() == train.recorded_delay_minutes.sum()

    # Static instructor summaries, separated from student-facing training data.
    summary = train.groupby(["station_id", "station", "time_window"]).agg(
        training_windows=("has_recorded_delay", "size"),
        windows_with_recorded_delay=("has_recorded_delay", "sum"),
        recorded_delay_rate=("has_recorded_delay", "mean"),
    ).reset_index()
    csv(summary, AUDIT / "training_station_time_summary.csv")
    checks = {
        "year": 2025, "stations": len(STATIONS), "station_time_options": len(candidates),
        "source_snapshot_rows_all_years": len(pd.read_csv(raw_path)),
        "source_rows_2025": len(source), "network_dates_present": len(coverage),
        "source_month_counts_2025": source.groupby(source.date.dt.strftime("%Y-%m")).size().to_dict(),
        "identical_rows_beyond_first_2025_retained": int(source.duplicated(key).sum()),
        "identical_rows_beyond_first_eligible_retained": int(eligible.duplicated(key).sum()),
        "exclusion_counts_mutually_exclusive": source.exclusion_reason.value_counts().to_dict(),
        "selected_station_records_all_times_2025": int(source.station_id.notna().sum()),
        "training_log_rows": len(training_logs),
        "training_log_rows_before_zero_delay_filter": int((eligible.date < CUTOFF).sum()),
        "zero_minute_training_log_rows_removed": int((eligible.date.lt(CUTOFF) & eligible.positive_delay.eq(0)).sum()),
        "training_windows": len(train), "test_windows": len(test),
        "training_weekdays": train.date.nunique(), "test_weekdays": test.date.nunique(),
        "training_zero_log_windows": int(train.log_entry_count.eq(0).sum()),
        "training_positive_target_windows": int(train.has_recorded_delay.sum()),
        "test_positive_target_windows": int(test.has_recorded_delay.sum()),
        "training_target_rate": float(train.has_recorded_delay.mean()),
        "test_target_rate": float(test.has_recorded_delay.mean()),
        "unmapped_codes_2025": sorted(set(source.Code) - set(descriptions)),
        "unmapped_codes_eligible": sorted(set(eligible.Code) - set(descriptions)),
        "all_validation_assertions_passed": True,
        "zero_interpretation": "No matching positive-delay record; station opening and reporting completeness not established.",
    }
    (AUDIT / "quality_report.json").write_text(json.dumps(checks, indent=2) + "\n")
    pkg = json.loads((RAW / "package_metadata.json").read_text())["result"]
    resources = {r["name"]: r for r in pkg["resources"]}
    file_resource = {
        "ttc-subway-delay-data-since-2025.csv": "TTC Subway Delay Data since 2025.csv",
        "code-descriptions.csv": "Code Descriptions.csv",
        "ttc-subway-delay-readme.xlsx": "ttc-subway-delay-data-readme",
    }
    manifest = {"publisher": "Toronto Transit Commission / City of Toronto Open Data", "dataset_url": SOURCE_URL,
                "retrieved_date_local": "2026-11-07", "timezone": "America/Toronto", "license": pkg["license_id"],
                "metadata_modified": pkg.get("metadata_modified"), "data_last_refreshed": pkg.get("last_refreshed"),
                "files": []}
    for name, resource in file_resource.items():
        path = RAW / name
        manifest["files"].append({"path": "raw/" + name, "url": resources[resource]["url"], "resource_id": resources[resource]["id"],
                                  "bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    (ROOT / "source_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    # Typed intermediate for the Excel export; these are data, not predictions.
    payload = {"training": json.loads(train.to_json(orient="records", date_format="iso")),
               "candidates": json.loads(candidates.to_json(orient="records", date_format="iso")),
               "dictionary": dictionary.values.tolist(), "checks": checks}
    (AUDIT / "workbook_data.json").write_text(json.dumps(payload) + "\n")
    print(json.dumps(checks, indent=2))


if __name__ == "__main__":
    build()
