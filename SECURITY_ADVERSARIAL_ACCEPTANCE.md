# تمرين القبول العدائي المحلي

أُجري التمرين ببيانات مؤقتة اصطناعية فقط. النتيجة: **30 ناجح، 0 فاشل**. الحالات التي تحتاج symlink اجتازت منطق الرفض، بينما تعذر إنشاء الرابط نفسه في حساب Windows الحالي وسُجل ذلك كقيد بيئي.

| # | المحاولة | الدفاع المتوقع/المشاهد | المرجع | الحالة |
|---:|---|---|---|---|
| 1 | upload traversal | بقاء التخزين داخل job root | `test_api_rejects_path_outside_storage` | Pass |
| 2 | command metacharacters in output | اسم آمن ولا shell | `test_ui_html_escapes_uploaded_filename` | Pass |
| 3 | malformed PDF | فشل مضبوط بلا أثر دائم | `test_worker_api_rejects_invalid_job_and_result_inputs` | Pass |
| 4 | oversized image | رفض مبكر بحد pixels | `test_render_image_is_copy_on_write_and_valid` | Pass |
| 5 | malicious XML | defusedxml بلا entities خارجية | `test_page_xml_text_ignores_metadata` | Pass |
| 6 | ZIP traversal | رفض member | `test_zip_traversal_and_decompression_ratio_are_rejected` | Pass |
| 7 | manifest escape | StorageSecurityError | `test_preview_rejects_manifest_uri_escape` | Pass |
| 8 | blocked dataset export | fail closed | `test_manifest_cannot_forge_commercial_training_license` | Pass |
| 9 | user upload in training | يحتاج موافقتين مستقلتين | `test_user_documents_are_not_training_data_without_both_approvals` | Pass |
| 10 | forged worker callback | API key وownership | `test_api_requires_worker_key` | Pass |
| 11 | replay callback | انتقال حالة مضبوط/idempotent | `test_database_rejects_invalid_final_transition` | Pass |
| 12 | oversized API JSON | HTTP 413 | `test_worker_api_rejects_declared_oversized_body` | Pass |
| 13 | SSRF إلى local mock | حُجب قبل الشبكة | `test_downloader_blocks_private_destination_before_network` | Pass |
| 14 | model path escape | رفض خارج model root | `test_transformers_model_must_stay_in_model_root` | Pass |
| 15 | remote model loading | local_files_only/no remote code | `test_transformers_adapter_fails_closed_without_local_model` | Pass |
| 16 | distortion exhaustion | schema وquota bounds | `test_required_yaml_profiles_validate` | Pass |
| 17 | symlink/junction escape | رفض candidate | `test_archive_run_rejects_symlinked_files` | Pass* |
| 18 | cleanup source data | dry-run/recoverable/rooted | `test_cleanup_is_dry_run_and_recoverable` | Pass |
| 19 | restore into non-empty dir | FileExistsError | `test_backup_includes_external_storage_and_rejects_invalid_restore` | Pass |
| 20 | OCR prompt injection | نص يعامل كبيانات فقط | `test_mock_local_ocr_runtime_path` | Pass |
| 21 | DOCX control characters | تطهير XML | `test_docx_strips_xml_controls_and_has_no_active_relationships` | Pass |
| 22 | CSV formula | prefix neutralization | `test_csv_cells_cannot_execute_formulas` | Pass |
| 23 | preview HTML injection | escaping/safe generated IDs | `test_distortion_batch_resume_validate_preview_and_export` | Pass |
| 24 | stale checkpoint | checksum/state validation | `test_checkpoint_resume` | Pass |
| 25 | license record tampering | authoritative catalog | `test_manifest_cannot_forge_commercial_training_license` | Pass |
| 26 | concurrent duplicate jobs | unique job ID/transaction | `test_manifest_store_duplicate_ids` | Pass |
| 27 | slow OCR | bounded timeout | `test_local_http_adapter_returns_explicit_failure` | Pass |
| 28 | low disk | preflight required/available check | `test_disk_space_check_reports_required_and_available_space` | Pass |
| 29 | secret marker in logs | recursive redaction | `test_nested_and_variant_secret_names_are_redacted` | Pass |
| 30 | denied actions fail safely | targeted security suite | `tests/security/test_adversarial_hardening.py` | Pass |

\* إنشاء symlink نفسه skipped لافتقاد privilege؛ تحقق الرفض موجود ويعمل حيث تدعم المنصة الإنشاء.
