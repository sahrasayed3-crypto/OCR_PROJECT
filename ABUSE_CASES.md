# حالات الإساءة

1. تخمين job ID أو استخدامه لقراءة ملف مستخدم آخر.
2. حقن `../` أو UNC أو ADS أو symlink في URI أو manifest أو archive.
3. جعل output أو restore يستبدل ملفًا موجودًا.
4. إرسال PDF أو صورة أو ZIP أو JSON يستهلك CPU/RAM/disk.
5. إدراج entity خارجية أو توسع entities في XML.
6. حقن shell metacharacters في filename أو OCR arguments.
7. توجيه downloader/provider إلى loopback أو metadata IP.
8. جعل OCR text ينتج hyperlink أو field أو control characters داخل DOCX.
9. إدخال صيغة spreadsheet في CSV أو HTML في preview.
10. تغيير `license_status` داخل manifest لتجاوز catalog.
11. تمرير وثيقة مستخدم إلى training بلا الموافقتين.
12. استبدال model/checkpoint أو تحميل pickle/remote code.
13. تزوير start/result/failure أو إعادة النتيجة بعد الإكمال.
14. حقن job داخل Redis إن أصبح Redis قابلًا للكتابة من جهة غير موثوقة.
15. تسريب مفتاح العامل أو OCR text في log/exception/health.
16. استعادة backup إلى مجلد غير فارغ أو عبر عضو archive متصادم.
17. جعل cleanup يتبع رابطًا أو يلمس المصدر.
18. تسميم split/dedup أو checkpoint لاستئناف حالة غير صحيحة.
19. تشغيل Streamlit/FastAPI على عنوان عام بلا opt-in وهوية.
20. استغلال CI action متغير أو dependency غير متحقق.
