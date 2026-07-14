# AMD Developer Cloud Readiness

## Project Summary

Clouda PDF is an open-source, model-agnostic PDF-to-DOCX project preparing for Arabic OCR evaluation and optional future OCR model integration. A primary model candidate has been selected, but it is not final yet.

## Why AMD GPUs Are Relevant

The selected primary Arabic OCR candidate may require GPU evaluation or fine-tuning/adaptation. AMD GPU access would help test whether a ROCm-compatible workflow is practical and cost-efficient.

## Planned ROCm Usage

ROCm usage is planned, not validated. The first goal is diagnostics and compatibility testing, followed by benchmarking of the selected primary model candidate only after legal data permissions and model license terms are confirmed.

## Model Candidate Status

A primary model candidate has been selected. Training has not started yet because dataset licensing and written-permission verification are still in progress. Other legally usable OCR systems may remain as baselines for comparison, not as claims of final support.

## Training Approach

No training is currently active. Future work may use LoRA or QLoRA only after dataset licensing, written permissions, and clear evaluation splits are complete.

## Evaluation Plan

Use the same frozen test set, preprocessing, normalization, CER/WER scripts, runtime measurements, and failure-mode reporting for each candidate.

## Estimated VRAM And Compute Needs

Still unverified for the selected primary model candidate. Initial work should start with diagnostics and small benchmarks, then scale only after memory and throughput are measured.

## Data Pipeline

Use consented or public-domain data with manifests, hashes, split metadata, source, license, and permission status.

## Synthetic Distortion Pipeline

Apply blur, noise, skew, JPEG compression, shadows, yellowing, bleed-through, uneven lighting, and edge degradation only to source pages that are legally usable.

## Checkpoint And Resume Strategy

Do not commit checkpoints or weights. Store them in controlled storage with versioned metadata if training becomes approved.

## Risk Controls

- No ROCm support claims before validation.
- No paid cloud resources should be created by automation.
- No unlicensed data or model weights should be uploaded.
- Keep CPU fallback and unavailable-model behavior explicit.

## 30-Day Execution Plan

1. Confirm dataset permissions and model license status.
2. Run ROCm diagnostics with `tools/system_rocm_info.py`.
3. Benchmark the selected primary candidate and public baselines.
4. Record CER/WER, runtime, RAM, VRAM, and failures.
5. Decide whether ROCm integration is viable.

## Expected Outputs

Benchmark report, hardware/software notes, dependency constraints, failure-mode report, and updated integration recommendation.

## Repository Readiness

Tests pass locally without GPU. ROCm dependencies are optional and not required for the current direct-text workflow.

## Licensing Readiness

Incomplete until every benchmark dataset and model has documented use and redistribution terms.
