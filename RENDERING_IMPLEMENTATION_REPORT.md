# تقرير تنفيذ التصيير

التصيير مكتمل لـPDF وPNG وJPEG وTIFF وWEBP، مع نطاق صفحات وDPI وتنسيق إخراج وأوضاع color/grayscale/binary. يطبق EXIF orientation، يعالج alpha، يفرض حدود البكسلات والأبعاد، يرفض التالف، ويستخدم كتابة ذرية وSHA-256 ومنع overwrite افتراضيًا.

الأوامر: `render`، `render-status`، `render-resume`، `render-validate`.

أثبت القبول تصيير 10 مصادر اصطناعية والتحقق من manifests وبقاء hashes المصادر دون تغيير. جميع المخرجات تحت `CLOUDA_STATE_HOME`.
