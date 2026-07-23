# Merge test results

Final command completed with **253 passed**, **0 failed**, **0 skipped**, and
**80.42% runtime coverage**.

| Subsystem | Tests |
|---|---:|
| PDF/DOCX runtime and UI | 159 |
| Shared contracts and metric policy | 21 |
| Data foundation | 43 |
| Migration and reconciliation | 9 |
| Queue integration | 4 |
| Model registry scaffold | 3 |
| Security behavior and repository scan | 7 |
| Training planning scaffold | 7 |
| **Total** | **253** |

Additional gates passed: Project A baseline (146 tests, 80.75% coverage), Ruff,
Black, mypy, compileall, CLI help for data and training, conversion demo,
repository scan, wheel build, source distribution build, and CI matrix
definition for Windows/Linux Python 3.11. The final wheel was also installed
into an isolated external environment and smoke-tested with its declared data
and training extras.

Coverage evidence is external at
`E:\clouda_merged_state\artifacts\reports\final_coverage.json`.
