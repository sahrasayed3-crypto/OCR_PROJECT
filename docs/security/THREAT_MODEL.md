# Threat model

Primary assets are user documents, worker credentials, correction data,
licensed datasets, model files, and runtime databases. Relevant threats include
oversized or malformed PDFs, ZIP bombs, XML entities, image decompression,
path traversal, hostile filenames, unauthorized worker calls, secret leakage,
dataset license bypass, cross-domain data access, and accidental user-document
training.

Implemented controls include bounded streaming, archive and XML validation,
external roots, opaque job IDs, parameterized SQL, header authentication,
constant-time key comparison, trusted hosts, security headers, queue
capabilities, license gates, consent gates, and repository scanning.

Production authentication, rate limiting, TLS termination, proxy trust, and
network policy are deployment responsibilities not visible in application code.
