# Security Policy

## Supported Status

This repository is being prepared for public review. Treat it as pre-production.

## Secrets

Do not commit:

- `.env`
- API keys
- worker keys
- local secret stores
- logs
- databases
- uploaded PDFs
- generated DOCX files
- backups
- model weights

If a secret was committed or shared, rotate it immediately.

## Reporting Issues

Open a private security report with:

- affected component
- reproduction steps
- impact
- suggested mitigation, if known

## Current Limitations

The app is intended for trusted local development unless authentication, TLS, storage retention, and deployment hardening are added.
