# تقرير أمن datasets والتدريب

- قرار الرخصة يأتي من catalog موثوق حسب purpose، لا من manifest المقدم.
- commercial training يفشل مغلقًا للمصادر pending/research/synthetic غير المصرح بها.
- user documents مستبعدة افتراضيًا وتتطلب موافقتين مستقلتين.
- output URI محصور، والصورة يجب أن توجد ويطابق checksum.
- السجلات والنصوص محدودة الحجم، وتقسيم المستند يمنع leakage عبر splits.
- deduplication وdocument-level deterministic split مختبران.
- provenance وstatus المحفوظان يعكسان القرار الموثوق.

النتيجة البرمجية: Pass. القرار القانوني الفعلي للمصادر الخارجية blocker.
