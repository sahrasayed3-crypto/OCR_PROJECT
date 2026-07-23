# تقرير أمن CI/CD

- `permissions: contents: read`.
- actions/checkout وsetup-python مثبتان على SHA موثقة.
- checkout لا يحتفظ credentials.
- jobs لها timeout، وworkflow له concurrency cancellation.
- لا نشر تلقائي ولا صلاحية packages/id-token.
- الاختبارات والتنسيق والتحليل والبناء قابلة للتنفيذ محليًا.
- SBOM وأدوات الأمن معرفة في extras، لكن workflow الحالي لا ينشر artifacts أو provenance.

المتبقي: إضافة secret scan وpip-audit وSBOM والتوقيع كخطوات CI إلزامية بعد اعتماد سياسة المؤسسة.
