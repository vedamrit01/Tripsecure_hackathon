# Evaluation results

Executed on 2026-09-26 using Python 3.12.14 and Streamlit 1.55.0.

Command: `python -m unittest discover -s tests -v`

**Result: 24 tests passed, 0 failed.** Includes 22 backend tests and two Streamlit UI smoke tests. UI tests ran (not skipped) in the local verification environment.

| Area | Evidence |
|---|---|
| Budget | Baseline ₹29,480; totals calculated from integer line items; impossible ₹1,000 budget reported as infeasible |
| Adaptation | ₹18,000 replan finds a cheaper option; locked activity day/time and stay tier preserved |
| Disruption | Rain-day outdoor activities removed; conflicting outdoor locks rejected explicitly |
| Schedule | No duplicate activities or overlapping windows across both supported destinations and 3–7-day lengths |
| Input validation | Unsupported origin, unknown model fields, invalid interests and invalid budget types rejected |
| Network boundary | Non-Azure, localhost, deceptive suffix, user-info and project URLs rejected |
| Untrusted data | Obvious and obfuscated document inputs cannot enter planner/model or call tools |
| Azure adapter | Mocked valid JSON applied; malformed JSON rejected; key absent from model request body |
| UI | Build → budget repair → security inspection and understand → build complete without app exceptions |

## What these results do not establish

- No live Azure call was made: no deployment name/API key was available in the build environment.
- No live tourism or weather API response was verified during this test run.
- No real hotel availability, fares, venue opening hours or routing was verified.
- Azure extraction quality across languages and adversarial prompts has not been benchmarked.
- Pattern matching does not establish general prompt-injection detection; document isolation is enforced by application structure.
- Browser visual screenshot review, Docker build and external hosting were not performed. Streamlit UI interactions were tested through AppTest.

These results demonstrate the bounded prototype's behaviour, not production readiness or guaranteed travel feasibility.
