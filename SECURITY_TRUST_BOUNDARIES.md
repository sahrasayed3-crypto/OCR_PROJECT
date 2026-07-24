# حدود الثقة

| الحد | المصدر غير الموثوق | الوجهة الأعلى ثقة | الضبط المطلوب |
|---|---|---|---|
| TB-01 | المتصفح ورفع الملفات | Streamlit/runtime | حجم ونوع ومستخدم واسم مولد |
| TB-02 | عميل العامل | FastAPI/SQLite | مفتاح عامل، ملكية job، replay/idempotency |
| TB-03 | Redis/RQ | عملية العامل | كاتبون موثوقون، payload محدود إلى job ID |
| TB-04 | PDF/image/XML/ZIP | parsers | حدود مبكرة، no entities/links/traversal |
| TB-05 | manifests | dataset/artifact roots | schema، URI resolver، checksum، ترخيص موثوق |
| TB-06 | catalog contributor | training export | قرار catalog سلطوي لا حقول manifest |
| TB-07 | model provider/file | inference process | model root، hash/revision، safetensors، no remote code |
| TB-08 | OCR text | DOCX/CSV/HTML/logs | Unicode/XML/CSV/HTML sanitization |
| TB-09 | admin configuration | subprocess/HTTP | allowlists، بيئة منقحة، timeout، SSRF controls |
| TB-10 | backup archive | restore root | empty target، member validation، exclusive writes |
| TB-11 | GitHub event/dependency | CI/build | pinned actions، read-only token، hashes، no publish |
| TB-12 | local single-user UI | public network | loopback default؛ public bind fails closed بلا هوية |

## العمليات ذات الامتياز

- تغيير إعدادات التخزين والمحركات والنماذج.
- إدارة datasets والتراخيص وتصدير التدريب.
- تشغيل برنامج OCR محلي أو endpoint بعيد.
- الاستعادة والتنظيف والأرشفة.
- كتابة نتائج العامل والحالة النهائية للوظيفة.

## افتراضات النشر

النشر العام غير معتمد حاليًا. يلزم OIDC/TLS وحدود proxy وتحديد هوية المستخدم
قبل تحويل واجهة المستخدم المحلية إلى خدمة متعددة المستأجرين. Redis وواجهة
العامل داخل شبكة خاصة فقط.
