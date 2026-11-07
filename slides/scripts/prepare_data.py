"""Prepare real data examples and illustrative expected-passenger scores."""
import csv
import hashlib
import json
import io
from collections import Counter
from statistics import median, correlation, quantiles
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT.parent / "ttc_case" / "data"

def read(name):
    with (DATA / name).open() as f:
        return list(csv.DictReader(f))

logs = read("training_log_entries.csv")
stations = read("stations.csv")
windows = read("training_windows.csv")
durations = [int(r["Min Delay"]) for r in logs]
q1, _, q3 = quantiles(durations, n=4, method="inclusive")
upper_fence = q3 + 1.5*(q3-q1)
weekday_histograms = []
for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
    minutes = [int(r["Min Delay"]) for r in logs if r["Day"] == day and int(r["Min Delay"]) <= upper_fence]
    bins = [sum(center-.5 <= value < center+.5 for value in minutes) for center in range(1,11)]
    assert sum(bins) == len(minutes)
    weekday_histograms.append({"day": day, "count": len(minutes), "mean": sum(minutes)/len(minutes), "bins": bins})
window_groups = {}
for record in windows:
    key = (record["station"], record["time_window"])
    window_groups.setdefault(key, []).append(int(record["recorded_delay_minutes"]))
window_baselines = [{"station": station, "window": window, "days": len(values), "minutes": sum(values), "mean_minutes": sum(values)/len(values)} for (station,window),values in window_groups.items()]
baseline_example = next(row for row in window_baselines if row["station"] == "Bloor-Yonge" and row["window"] == "07:00-09:00")
monthly_groups = {}
for record in windows:
    if record["station"] == "Bloor-Yonge" and record["time_window"] == "07:00-09:00":
        monthly_groups.setdefault(record["date"][:7], []).append(int(record["recorded_delay_minutes"]))
monthly_means = [{"month": month, "days": len(values), "mean": sum(values)/len(values)} for month,values in sorted(monthly_groups.items())]
moving_average = {"station": "Bloor-Yonge", "window": "07:00-09:00", "months": monthly_means,
                  "forecast": sum(r["mean"] for r in monthly_means[-3:])/3}

# Reuse the frozen, previously held-out 2025 records with the same classroom scope.
audit_path = DATA.parent / "instructor/record_audit_2025.csv"
test_windows_path = DATA.parent / "instructor/test_windows_with_outcomes.csv"
with audit_path.open() as source:
    test_logs = [r for r in csv.DictReader(source) if r["exclusion_reason"] == "included"
                 and "2025-10-01" <= r["date"][:10] <= "2025-12-31" and int(r["positive_delay"]) == 1]
test_logs.sort(key=lambda r:(r["date"],r["Time"],r["station_id"],int(r["_id"])))
test_buffer = io.StringIO(newline="")
writer = csv.DictWriter(test_buffer, fieldnames=list(logs[0]), extrasaction="ignore")
writer.writeheader(); writer.writerows(test_logs)
test_csv = test_buffer.getvalue()
test_windows_csv = test_windows_path.read_text()
test_windows = list(csv.DictReader(io.StringIO(test_windows_csv)))
assert len(test_logs) == 229 and len(test_windows) == 2970
assert {r["date"][:7] for r in test_windows} == {"2025-10","2025-11","2025-12"}
assert max(r["date"] for r in windows) < min(r["date"] for r in test_windows)
assert sum(int(r["Min Delay"]) for r in test_logs) == sum(int(r["recorded_delay_minutes"]) for r in test_windows)
assert set(r["station"] for r in test_windows) == set(r["station"] for r in windows)
downloads = [{"id": "download-csv", "filename": "ttc_training_log_jan_sep_2025.csv", "csv": (DATA / "training_log_entries.csv").read_text()},
             {"id": "download-test-log", "filename": "ttc_testing_log_oct_dec_2025.csv", "csv": test_csv},
             {"id": "download-test-windows", "filename": "ttc_testing_windows_oct_dec_2025.csv", "csv": test_windows_csv}]
download_dir = ROOT / "assets/data"
download_dir.mkdir(exist_ok=True)
for item in downloads:
    (download_dir / item["filename"]).write_text(item["csv"], newline="")
scatter_points = [{"delay": int(r["Min Delay"]), "gap": int(r["Min Gap"])} for r in logs]
duration_summary = {"under10": sum(v < 10 for v in durations), "q1": q1, "q3": q3,
                    "upper_fence": upper_fence, "flagged": sum(v > upper_fence for v in durations), "max": max(durations)}
station_counts = Counter(r["station"] for r in logs)
station_minutes = Counter()
for record in logs:
    station_minutes[record["station"]] += int(record["Min Delay"])
time_counts = Counter(r["time_window"] for r in logs)
required = ["Date", "Time", "station", "code_description", "Min Delay"]
duplicate_fields = ["Date", "Time", "Station", "Code", "Min Delay", "Min Gap", "Bound", "Line", "Vehicle"]
histogram = [
    {"label": label, "count": sum(low <= value <= high for value in durations)}
    for label,low,high in [("1–4",1,4),("5–9",5,9),("10–19",10,19),("20–39",20,39),("40+",40,max(durations))]
]
# Artificial expected passenger journeys needing help, not measured ridership
# or model output. Used only to illustrate comparing three station–time pairs.
passengers = [[240,110,280],[180,150,310],[210,90,230],[160,70,190],[170,60,150],
              [140,50,180],[150,100,170],[100,160,220],[90,40,110],[110,50,130],
              [190,80,200],[80,60,100],[120,50,140],[130,110,160],[100,40,120]]
payload = {
    "stations": [{**s, "expected_passengers": passengers[i]} for i,s in enumerate(stations)],
    "windows": ["07:00-09:00", "12:00-14:00", "16:00-18:00"],
    "logs": [{k:r[k] for k in ["Date","Time","station","code_description","Min Delay"]} for r in logs[:3]],
    "log_count": len(logs),
    "weekday_histograms": weekday_histograms,
    "duration_summary": duration_summary,
    "scatter": {"points": scatter_points, "pearson_r": correlation(durations, [p["gap"] for p in scatter_points])},
    "window_baselines": window_baselines,
    "baseline_example": baseline_example,
    "moving_average": moving_average,
    "downloads": downloads,
    "exploration": {
        "station_minutes": [{"label": name, "minutes": minutes} for name,minutes in station_minutes.most_common()],
        "total_minutes": sum(durations),
        "station_counts": [{"label": name, "count": count} for name,count in station_counts.most_common()],
        "time_counts": [{"label": name, "count": time_counts[name]} for name in ["07:00-09:00","12:00-14:00","16:00-18:00"]],
        "duration_bins": histogram,
        "median_minutes": median(durations), "max_minutes": max(durations),
        "station_count": len(station_counts),
        "missing_core": sum(any(not r[k].strip() for k in required) for r in logs),
        "nonpositive_minutes": sum(value <= 0 for value in durations),
        "extra_duplicate_rows": len(logs)-len({tuple(r[k] for k in duplicate_fields) for r in logs}),
    },
    "passenger_estimate_note": "Artificial expected passenger journeys needing help per station–time pair; not measured ridership or fitted predictions. Choose exactly three pairs and sum their scores.",
    "sources": {name: hashlib.sha256((DATA/name).read_bytes()).hexdigest() for name in ["training_log_entries.csv","stations.csv","training_windows.csv"]}
}
payload["sources"].update({"instructor/record_audit_2025.csv": hashlib.sha256(audit_path.read_bytes()).hexdigest(),
                           "instructor/test_windows_with_outcomes.csv": hashlib.sha256(test_windows_path.read_bytes()).hexdigest()})
assert sum(station_minutes.values()) == sum(durations)
assert sum(row["minutes"] for row in window_baselines) == sum(durations)
assert all(row["days"] == 195 for row in window_baselines)
assert len(stations)==15 and len(logs)==708
assert all(int(r["Min Delay"])>0 for r in logs)
assert sum(row["count"] for row in histogram)==len(logs)
(ROOT/"assets/workshop-data.js").write_text("window.WORKSHOP_DATA = " + json.dumps(payload,ensure_ascii=False) + ";\n")
print("Prepared real data examples for 15 stations and 45 assignments.")
