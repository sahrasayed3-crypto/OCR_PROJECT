# نتائج الاختبارات الأمنية

## النتائج النهائية

- Full pytest النهائي: 300 passed, 0 failed, 2 skipped.
- Security suite بعد إضافة property tests: 22 passed, 0 failed, 2 skipped.
- Coverage: 75.12% total; 79.11% statements; 60.60% branches.
- Ruff: pass.
- Black check: pass.
- mypy: pass على 148 ملف مصدر.
- compileall: pass للمصدر المثبت معزولًا.
- Bandit: 33 raw warnings؛ 0 confirmed unresolved.
- pip-audit: 0 vulnerabilities عبر 121 dependency record.
- detect-secrets: 7 false positives؛ 0 true secrets.
- Wheel/sdist: pass.
- Isolated install/import/CLI/API: pass.

الحالتان المتجاوزتان تتطلبان صلاحية إنشاء روابط رمزية غير متاحة للحساب على Windows. الشيفرة المقابلة اختُبرت بمراجعة المسار وباختبارات الروابط حيث تسمح المنصة.

الأدلة الآلية محفوظة أيضًا في `E:\clouda_merged_state\artifacts\security_assessment`.
