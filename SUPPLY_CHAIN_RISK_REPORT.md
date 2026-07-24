# مخاطر سلسلة التوريد

- GitHub Actions مثبتة على commit SHA، مع `persist-credentials: false` وصلاحيات دنيا ومهل وconcurrency.
- downloads تمر عبر HTTPS افتراضيًا، مع SHA-256 وحجب private IP وإعادة تحقق redirects.
- نموذج OCR محلي فقط افتراضيًا، `trust_remote_code=false`، `local_files_only=true`، وsafetensors.
- datasets تعتمد catalog موثوقًا وchecksum ورخصة حسب الغرض.
- SBOM بصيغة CycloneDX 1.6 موجود في `SBOM.json`.
- المخاطر المتبقية: لا توجد توقيعات Sigstore أو provenance منشورة، ولا قرارات قانونية فعلية للرخص، وبعض الإصدارات ذات ranges لا lock شامل لها.
- التوصية: توليد lock/constraints خاص بكل منصة، توقيع artifacts، وحفظ provenance في CI موثوق قبل النشر.
