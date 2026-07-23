# تقرير أمن distortion

- profiles تقرأ بـsafe YAML وتتحقق بـJSON Schema وبحدود parameters/chains/variants.
- source/output URIs تمر عبر StorageRoots.
- JSONL محدود بالحجم والأسطر والسجلات.
- generated IDs تُطبع إلى أسماء ملفات آمنة.
- writes ذرية ولا تعدل المصدر؛ cleanup dry-run افتراضي ويتحقق من completion/root/symlink.
- preview يهرب HTML، وCSV neutralizes formulas.
- resume/checkpoints تخضع للmanifest والحالة ولا تسمح overwrite صامت.

النتيجة: Pass.
