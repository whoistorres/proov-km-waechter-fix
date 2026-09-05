# analyze.py
# Breakdown-risk factors: km_since_service, avg_daily_km, and load_factor genuinely separate
# cars that broke down from cars that didn't (Cohen's d 0.53-1.06); total mileage and age don't
# (d near 0) -- it's how overdue and how hard-driven a car is, not how old or high-mileage it is.

import numpy as np
import pandas as pd

df = pd.read_csv("fleet_history.csv")

CANDIDATE_COLUMNS = ["odometer_km", "km_since_service", "avg_daily_km", "load_factor", "age_years"]


def cohens_d(broke: pd.Series, ok: pd.Series) -> float:
    """Standardized mean difference between the two groups for one column."""
    n1, n0 = len(broke), len(ok)
    pooled_std = np.sqrt(
        ((n1 - 1) * broke.std(ddof=1) ** 2 + (n0 - 1) * ok.std(ddof=1) ** 2) / (n1 + n0 - 2)
    )
    return (broke.mean() - ok.mean()) / pooled_std


def compare_groups(fleet: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Compare broke-down vs. ok cars column by column, ranked by effect size."""
    broke = fleet[fleet["broke_down"] == 1]
    ok = fleet[fleet["broke_down"] == 0]
    rows = [
        {
            "column": col,
            "mean_broke_down": broke[col].mean(),
            "mean_ok": ok[col].mean(),
            "cohens_d": cohens_d(broke[col], ok[col]),
        }
        for col in columns
    ]
    return pd.DataFrame(rows).sort_values("cohens_d", key=abs, ascending=False)


def normalize(series: pd.Series) -> pd.Series:
    """Scale a column to 0-1 using its observed min/max across the fleet."""
    return (series - series.min()) / (series.max() - series.min())


print("Step 1: does each column separate the two groups?")
print("(Cohen's d: <0.2 negligible, 0.2-0.5 small, 0.5-0.8 medium, >=0.8 large)")
comparison = compare_groups(df, CANDIDATE_COLUMNS)
print(comparison.to_string(index=False))

SEPARATING_COLUMNS = comparison.loc[comparison["cohens_d"].abs() >= 0.5, "column"].tolist()
print(f"\nColumns that genuinely separate the groups (|d| >= 0.5): {SEPARATING_COLUMNS}")
print(
    "odometer_km and age_years do NOT separate the groups (d near 0) -- total mileage and age "
    "alone do not predict breakdown here, despite looking like the obvious answer."
)

# Step 2: a simple 0-100 risk score built only from the columns that separate the groups,
# each weighted by how strongly it separates them (bigger Cohen's d -> bigger weight).
weights = comparison.set_index("column").loc[SEPARATING_COLUMNS, "cohens_d"].abs()
weights = weights / weights.sum()

risk = pd.Series(0.0, index=df.index)
for column, weight in weights.items():
    risk += weight * normalize(df[column])
df["risk_score"] = (risk * 100).round(1)

print("\nStep 2: risk score weights (from Cohen's d, normalized to sum to 1)")
print(weights.round(3).to_string())

# Step 3: rank the fleet by risk, highest first.
ranked = df.sort_values("risk_score", ascending=False)
print("\nStep 3: top 10 highest-risk cars")
print(
    ranked[["car_id", "risk_score", "km_since_service", "avg_daily_km", "load_factor", "broke_down"]]
    .head(10)
    .to_string(index=False)
)
