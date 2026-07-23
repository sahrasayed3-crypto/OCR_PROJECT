# مرجع أوامر OCR وتأسيس البيانات

اضبط أولًا:

```powershell
$env:CLOUDA_STATE_HOME='E:\clouda_merged_state'
$env:CLOUDA_PROJECT_ROOT='E:\clouda_merged_work'
```

```powershell
python -m clouda_data.pipeline.cli render SOURCE.pdf --dpi 200 --start-page 1 --end-page 10
python -m clouda_data.pipeline.cli render-status MANIFEST.jsonl
python -m clouda_data.pipeline.cli render-resume SOURCE.pdf --run-id RUN_ID
python -m clouda_data.pipeline.cli render-validate MANIFEST.jsonl

python -m clouda_data.pipeline.cli distort-preview DISTORTION_MANIFEST.jsonl --limit 10 --layout-overlay
python -m clouda_data.pipeline.cli distort-batch INPUT_MANIFEST.jsonl --profile configs\data_foundation\distortions\modern_scan_medium.yaml --seed 20260723 --variants 1 --maximum-pages 100
python -m clouda_data.pipeline.cli distort-resume INPUT_MANIFEST.jsonl --profile configs\data_foundation\distortions\modern_scan_medium.yaml --seed 20260723 --variants 1 --maximum-pages 100
python -m clouda_data.pipeline.cli distort-validate DISTORTION_MANIFEST.jsonl --quarantine
python -m clouda_data.pipeline.cli distort-status DISTORTION_MANIFEST.jsonl
python -m clouda_data.pipeline.cli list-distortion-profiles
python -m clouda_data.pipeline.cli validate-distortion-profile PROFILE.yaml

python -m clouda_data.pipeline.cli evaluate-manifest OCR_RESULTS.jsonl --output REPORT.json
python -m clouda_training.cli export DISTORTION_MANIFEST.jsonl --output E:\clouda_merged_state\artifacts\training\export.jsonl --format generic_jsonl --purpose evaluation
python -m clouda_training.cli statistics TRAINING.jsonl
python -m clouda_training.cli estimate-storage TRAINING.jsonl

python -m clouda_data.pipeline.cli cleanup-preview --older-than-days 7
python -m clouda_data.pipeline.cli cleanup-failed --older-than-days 7
python -m clouda_data.pipeline.cli cleanup-temp --older-than-days 1
python -m clouda_data.pipeline.cli archive-run RUN_DIR --output ARCHIVE.zip
python -m clouda_data.pipeline.cli verify-archive ARCHIVE.zip
```

المعاينة والإدارة:

```powershell
python -m streamlit run app.py --server.address 127.0.0.1
python -m streamlit run tools\data_foundation_app.py --server.address 127.0.0.1
```
