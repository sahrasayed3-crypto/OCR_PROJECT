# تقرير أمن API والواجهة

- FastAPI worker endpoints تتطلب worker API key حيث يلزم، مع مقارنة ثابتة الزمن ودعم current/previous rotation.
- اختبارات الملكية تمنع worker غير المالك من failure/result transitions.
- حجم الطلب المعلن يُرفض مبكرًا بـ413، والنماذج تحد JSON/metadata.
- download paths تتحقق من root والملكية، وتوجد security headers.
- health العام لا يكشف المفتاح أو محتوى الوثائق.
- bind الافتراضي 127.0.0.1، وأي public bind يتطلب إقرار حماية خارجية.
- TestClient smoke من wheel معزول: HTTP 200 على `/health`.
- لا يوجد OIDC إنتاجي؛ الحد `ExternalOIDCRequired` يفشل مغلقًا.

النتيجة: Pass محليًا، Blocked للنشر العام حتى OIDC/TLS.
