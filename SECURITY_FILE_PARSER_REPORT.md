# تقرير أمن الملفات والمحللات

- PDF: حدود bytes/pages/projected pixels، معالجة فشل مضبوطة، وعدم تنفيذ JavaScript أو embedded files.
- Images: `MAX_IMAGE_PIXELS` وحدود pixels/frame count في rendering/OCR.
- XML: defusedxml لبيانات PAGE/ALTO وRasam؛ لا DTD/XXE.
- ZIP/DOCX/backup: traversal، absolute/device names، links، duplicates، case collisions، ratio/member/byte limits محجوبة.
- restore يكتب كل عضو بـexclusive create بدل `extractall`.
- storage URI يمنع ADS، reserved devices، trailing dots/spaces، controls، Unicode ambiguity والتجاوز.
- مسارات ingestion محصورة في مجلد manifest؛ model/training/distortion/lifecycle محصورة في roots الخاصة بها.

النتيجة: Pass للاختبارات الاصطناعية المحدودة.
