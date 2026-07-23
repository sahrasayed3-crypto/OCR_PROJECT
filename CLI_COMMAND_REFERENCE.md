# CLI command reference

Set the roots first:

```powershell
$env:CLOUDA_STATE_HOME='E:\clouda_merged_state'
$env:CLOUDA_PROJECT_ROOT='E:\clouda_merged_work'
```

## Rendering

```powershell
python -m clouda_data.pipeline.cli render SOURCE --dpi 200 --start-page 1 --end-page 10
python -m clouda_data.pipeline.cli render-resume SOURCE --run-id RUN_ID
python -m clouda_data.pipeline.cli render-validate MANIFEST
```

## Distortion

```powershell
python -m clouda_data.pipeline.cli distort-preview MANIFEST --limit 10
python -m clouda_data.pipeline.cli distort-batch MANIFEST --profile modern_scan_medium --seed 20260723 --variants 3 --maximum-pages 100
python -m clouda_data.pipeline.cli distort-resume MANIFEST --profile modern_scan_medium --seed 20260723 --variants 3 --maximum-pages 100
python -m clouda_data.pipeline.cli distort-validate DISTORTION_MANIFEST --quarantine
```

## Evaluation and export

```powershell
python -m clouda_data.pipeline.cli evaluate-manifest OCR_MANIFEST
python -m clouda_training.cli export DISTORTION_MANIFEST --output E:\clouda_merged_state\artifacts\training\export.jsonl --format generic_jsonl --purpose commercial_training
```

## Lifecycle

```powershell
python -m clouda_data.pipeline.cli cleanup-preview
python -m clouda_data.pipeline.cli archive-run RUN_ROOT
python -m clouda_data.pipeline.cli verify-archive ARCHIVE
```

## Applications

```powershell
python -m streamlit run E:\clouda_merged_work\app.py
python -m streamlit run E:\clouda_merged_work\tools\data_foundation_app.py --server.address 127.0.0.1
```
