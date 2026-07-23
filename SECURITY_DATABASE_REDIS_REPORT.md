# تقرير أمن SQLite وRedis والصفوف

- قيم SQL parameterized، وأسماء الأعمدة الديناميكية محصورة بقوائم صريحة.
- SQLite يفعّل foreign keys وWAL وbusy timeout، والنسخ الاحتياطي يستخدم API snapshot ثم integrity check.
- transitions محددة، وjob IDs فريدة، وownership مفروض في callbacks.
- RQ payload لا يحمل إلا job ID؛ تفاصيل الملفات تبقى في DB/storage.
- Redis افتراضيًا loopback، مع hooks لـrediss وcertificate requirements وtimeouts.
- لا يملك runtime worker صلاحية إعداد datasets أو التدريب.

المتبقي: عند Redis مشترك يجب فرض ACL/TLS ومنع أي كاتب غير موثوق لأن RQ يعتمد الثقة في منتج الصف.
