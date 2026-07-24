# تقرير أمن النسخ والاستعادة والتنظيف

- archive validation يمنع traversal/absolute/device/symlink/special/duplicate/case collision/bombs.
- restore يرفض الوجهة symlink أو غير الفارغة، ويستخرج عضوًا بعضو بإنشاء حصري.
- قاعدة البيانات المستعادة تمر بـ`PRAGMA integrity_check`.
- cleanup محصور في roots، dry-run افتراضي، ويرفض symlink والملفات النشطة.
- archive lifecycle يتحقق من completion ويمنع اتباع الروابط.
- retention يعمل فقط داخل backup root المحدد.

النتيجة: Pass؛ اختبارات symlink نفسها skipped حيث لا يمنح Windows privilege.
