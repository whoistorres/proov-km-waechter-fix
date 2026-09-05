# What I checked, and what the agent got wrong

## What the agent got wrong
The agent didn't leave a functional bug in place I had to send it back to fix since the tests
and verify.py both went green on the changes it had been proposed. What it did do is make two judgment
calls on its own instead of stopping to check with me first, even though the brief for this task
explicitly asked for that:

- **The missing-reading car's effect on the average wear.** TASK.md never says whether a car with
  no `last_service_km` should be excluded from the fleet's average wear or counted as some default
  value. The agent decided on its own to exclude it from the average (but still count it toward
  `count` and check it for `due`) and only explained that choice after presenting the diff, not
  before writing it.
- **Deleting dead code in fleet_utils.py.** TASK.md says: "Have Bob tell you what it found BEFORE
  it fixes anything, then decide together what to fix and what to delete." The agent did report
  the five unused functions (`mean`, `format_percent`, `is_due`, `parse_service_date`,
  `chunk_list`) before touching them, which is right, but it deleted all five in the same turn
  rather than waiting for me to actually weigh in on `is_due` specifically, which was flagged as
  the riskiest one.

Neither turned out to be wrong, but both were decisions the brief said should be made together,
and the agent made them and then reported them rather than pausing.

## What I checked before I accepted its work
- I had the agent run `pytest -v` itself and show me the output of 6 of 6 tests passing, not just
  a claim that they passed. After that, I decided to run `python verify.py` and read every line myself:
  10 of 11 PASS (the interval/threshold checks, the crash fix, the average-wear math, the mileage conversion, and the added tests), with
  only this file left as the honest remaining FAIL until I decided to write it after verifying the NOTES.md myself.
- I also checked the diff of `km_wachter.py` and `fleet_report.py` line by line against the two rules
  that were established (15,000 km interval, 80% threshold) with both being untouched in the code
  and in `settings.cfg`, and `verify.py`'s own `rules_are_unchanged` / `config_rules_are_unchanged`
  checks confirm it independently of the agent's word.
- For the mileage bug specifically, I had the agent show me the before/after number for a concrete
  case (100 km) rather than just the code diff: 160.9 miles before, 62.1 miles after, which is
  the actual, checkable evidence that the fix is real and not just a plausible-looking edit.

## What the data actually said
The total mileage (`odometer_km`) and age (`age_years`) do **not** separate the cars that broke down
from the ones that didn't, since the effect size (Cohen's d) for both is close to 0, meaning the two
groups look statistically identical on those columns. But what actually separates them, is how overdue
a car is for service (`km_since_service`, d≈1.06), how hard it's driven day to day
(`avg_daily_km`, d≈0.63), and how heavily loaded it runs (`load_factor`, d≈0.53). So the risk score
is built only from those three, weighted by how strongly each one separates the groups. The obvious
assumption, which is "older, higher-mileage cars break down" is not what this data shows.
