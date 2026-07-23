# تقرير تصدير بيانات التدريب

يدعم المصدر سبعة تنسيقات: generic JSONL، multimodal conversation، plain OCR، Markdown، layout، reading order وword bounding boxes.

السياسات المطبقة:

- تقسيم حتمي على `source_document_id` بلا تسرب صفحات.
- exact checksum dedup وواجهة perceptual duplicate.
- ترتيب وتوازن حتمي حسب dataset/profile/difficulty.
- `--max-contribution-per-source`.
- benchmark exclusions وحاجز الترخيص.
- رفض synthetic evaluation للتدريب التجاري ورفض الملفات غير الموجودة أو checksum المخالف.
- لا يبدأ التصدير أي تدريب.

قبول النهاية صدّر 23 سجلًا، `document_leakage=[]`، تحت `E:\clouda_merged_state\artifacts\training`.
