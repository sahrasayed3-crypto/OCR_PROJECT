# Rendering pipeline

Status: **complete** for PDF, PNG, JPEG, TIFF, and WEBP inputs.

The renderer processes pages incrementally, applies EXIF orientation, flattens
alpha safely, supports color/grayscale/binary output, constrains DPI,
dimensions, and pixels, and writes atomically under the dataset state root.
Multi-frame TIFF and PDF page ranges are supported. Source and output SHA-256,
renderer version, config hash, dimensions, and status are recorded in a
versioned JSONL manifest.

Existing outputs are never overwritten. `--dry-run` plans work and
`render-resume` skips checksum-verified completed pages.

