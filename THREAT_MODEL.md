# نموذج التهديد — STRIDE

## الجهات المهددة

مستخدم إنترنت غير موثق، مستخدم خبيث موثق، عامل مخترق، مساهم dataset أو
model خبيث، مسؤول خبيث، تبعية أو CI runner مخترق، وحساب محلي محدود أو قارئ
لنظام الملفات.

## STRIDE

| الفئة | التهديدات الرئيسية | الأصول | الضوابط/الاختبارات |
|---|---|---|---|
| Spoofing | تزوير عامل أو مستخدم أو model ID | jobs, identities, models | مفاتيح ثابتة الزمن، ملكية، revision/hash |
| Tampering | تعديل manifest/license/checkpoint/result | datasets, jobs, exports | schema، catalog سلطوي، SHA-256، حالات ذرية |
| Repudiation | إعادة callback أو إنكار عملية إدارية | jobs, lifecycle | request ID، أحداث منظمة، idempotency، audit |
| Information disclosure | IDOR، paths، OCR/log/backup leak | user files, secrets | ownership، redaction، attachments، root isolation |
| Denial of service | PDF/image/ZIP/JSON/queue/model bombs | CPU/RAM/disk/workers | حدود مبكرة، quotas، timeout، rate limit |
| Elevation of privilege | command injection، traversal، unsafe model code | host, roots | no shell، executable policy، safe resolver، no remote code |

## أعلى مسارات الخطر

1. manifest خبيث يحاول قراءة ملف خارج `dataset://`.
2. سجل ترخيص مزور يحاول إدخال dataset محظور في training.
3. ZIP أو backup يحاول الكتابة خارج جذر الاستعادة.
4. OCR command أو endpoint يحاول تنفيذ برنامج/SSRF أو تسريب البيئة.
5. عامل يحمل نتيجة مزورة أو يعيد callback قديمًا.
6. PDF/image/model يستهلك الذاكرة قبل تطبيق الحدود.
7. واجهة local-only تُربط عامًا بلا هوية مستخدم.
8. OCR output يصنع XML/DOCX/CSV/HTML نشطًا أو مضللًا.

## قرار أولي

الخدمة صالحة للاختبار المحلي فقط. بوابة الإصدار العام تبقى مغلقة حتى انتهاء
هذا التقييم، ثم تظل مشروطة بموفر الهوية وTLS وقرار الترخيص الخارجي.
