# Open issues

1. **Release blocker — production authentication:** connect the Streamlit
   runtime and worker API to the deployment identity provider; rotate worker
   header keys through the secret manager.
2. **Release blocker — edge security:** terminate TLS, set the allowed-host
   list, and enforce rate/request limits at the reverse proxy.
3. **Release blocker — legal review:** approve or reject every `pending`,
   `blocked`, and `research_only` dataset before any training use.
4. **Release blocker — OCR model:** select, license, pin, scan, and evaluate
   model weights. Local OCR is disabled by default and no weights are present.
5. **Operational decision:** configure Redis durability/monitoring before
   distributed workers are enabled.
6. **Known non-blocker:** 267 checksum duplicates are cataloged. They remain
   preserved until provenance-aware deduplication is approved.
7. **Known non-blocker:** 12 of 100 reviewed RASAM pages failed validation and
   remain rejected, with evidence retained.
