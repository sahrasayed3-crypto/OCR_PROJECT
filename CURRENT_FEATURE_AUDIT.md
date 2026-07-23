# تدقيق الحالة الحالية

التاريخ: 2026-07-23. الفرع: `completion/ocr-data-pipeline`.

| الميزة | الحالة المؤكدة | الدليل |
|---|---|---|
| التصيير الحقيقي | منفذ ومختبر | PDF والصور، acceptance |
| التشويه البكسلي | منفذ ومختبر | 107 مشغلات، 30/30 اختلاف |
| metadata-only | معطل افتراضيًا | اختبار صريح فقط |
| ملفات التعريف | منفذة ومختبرة | 18 YAML صالحة |
| batch وresume | منفذ ومختبر | JSONL + SQLite WAL + interruption |
| التحقق والحجر | منفذ ومختبر | JSON/JSONL/CSV/MD وquarantine |
| المعاينة | منفذة ومختبرة | HTML وcontact sheet وdiff وoverlay |
| تصنيف الصعوبة | منفذ ومختبر | 12 إشارة تقريبًا، ليس OCR accuracy |
| تقييم OCR | منفذ ومختبر | CER/WER ومقاييس مجمعة |
| تصدير التدريب | منفذ ومختبر | 7 تنسيقات، dedup، balance، no leakage |
| المحولات المحلية | منفذة ومختبرة | mock/CLI/HTTP/OpenAI/Transformers/Qwen |
| runtime mock | منفذ ومختبر، معطل افتراضيًا | acceptance=`local_model_ocr` |
| نموذج OCR حقيقي | عائق خارجي | لا أوزان ولا تنزيل تلقائي |
| واجهة الإدارة | منفذة ومختبرة بالاستيراد | محلية، تحقق، تقدم، export preview |
| دورة الحياة | منفذة ومختبرة | dry-run وحماية الجذور والأرشيف |
| تدريب GPU | معطل تصميميًا | يتطلب بيانات ونموذجًا وعتادًا معتمدًا |

التحقق النهائي: 304 passed، صفر failed، 2 skipped، coverage 75%. تقرير القبول:
`E:\clouda_merged_state\artifacts\reports\acceptance\acceptance-20260723T205210Z.json`.
