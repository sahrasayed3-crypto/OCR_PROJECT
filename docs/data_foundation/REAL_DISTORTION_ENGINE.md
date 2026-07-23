# Real distortion engine

Status: **complete for CPU/Pillow operators**. `RealImageDistortion` changes
pixels and is the default registry implementation; `metadata_only` remains an
explicit test operator. The registry exposes deterministic geometric, blur,
noise, compression, illumination, aging, printing, scanning, and Arabic
text-degradation operators.

Every operation records its name, implementation version, parameters,
probability, severity, derived seed, affected regions, and dimensions.
`DistortionPipeline` derives independent seeds from the run seed, page ID,
operator name, and order. It guarantees that a non-empty selected profile
applies at least one operator.

Ground-truth text is copied unchanged into external manifests. Pixel outputs
use copy-on-write atomic PNG creation and never overwrite an existing file.
Unknown operators fail explicitly.

