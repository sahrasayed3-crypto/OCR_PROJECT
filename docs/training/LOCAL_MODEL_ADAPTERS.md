# Local model adapters

Status: **safe adapters complete; real model selection is externally blocked**.

Adapters exist for a local HTTP service, an OpenAI-compatible local endpoint,
an absolute-path command-line engine, Transformers vision-language models,
Qwen-VL-compatible Transformers loading, and a gated synthetic mock.

Transformers loading is local-only, uses `trust_remote_code=False`, and never
downloads weights. Remote HTTP endpoints require explicit opt-in. Command
arguments use a JSON string array or parsed argument list and `shell=False`.
The mock requires `CLOUDA_ALLOW_MOCK_OCR=true` and is test-only.

