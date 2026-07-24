# تقرير أمن OCR والنماذج

- OCR command يحتاج executable allowlist صريح، ويستعمل argv بلا shell، cwd مؤقتًا ثابتًا، بيئة مصغرة، timeout ومخرجات 4 MiB.
- model/processor يجب أن يكونا داخل model root وغير symlink.
- Transformers يستعمل local-only، no remote code، safetensors وweights-only.
- حدود الصورة والرموز والمهلة معرفة.
- document content لا يتحكم في أدوات أو ملفات؛ يدخل فقط كبيانات prompt.
- OCR output يمر بتطهير XML/control/bidi قبل DOCX.
- لا توجد automatic remote model downloads.

المتبقي: pin/checksum لكل نموذج إنتاجي يجب توفيره من registry ومخزن artifacts المعتمد.
