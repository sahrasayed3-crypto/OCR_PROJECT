# نتائج خط الأساس للمشروع A

التاريخ: 2026-07-23  
commit المصدر: `b6e548a853991b872d804f5e71238d17fa7103a7`  
البيئة: Python 3.11.9 في `E:\clouda_merge_env` خارج المستودع.

| الفحص | النتيجة |
|---|---|
| pytest | 146 passed |
| coverage | 80.75%، أعلى من بوابة 80% |
| Ruff | passed |
| Black check | passed، 70 files unchanged |
| mypy | passed، 70 source files |
| compileall | passed |
| demo | passed |

أنتج demo الحالات المتوقعة:

- `direct_pdf_text`
- `pending_ocr_model`
- `blank_page`

ملاحظات:

- ظهرت رسالتا parser من `pypdf` عن `incorrect startxref pointer` أثناء قراءة fixture، لكن demo اكتمل بنجاح ولم يفشل الاختبار.
- لم تُستخدم خدمات خارجية أو credentials.
- لم يُشغّل الاختبار داخل أي من مستودعي المصدر.
- ملفات demo وcoverage وbytecode الناتجة داخل destination متجاهلة في Git وستزال في فحص النظافة النهائي.

