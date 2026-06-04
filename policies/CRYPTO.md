# Cryptographic Standards

## CRYPTO-01 — Approved algorithms

| Purpose | Approved | Forbidden |
|---------|----------|-----------|
| Hashing (general) | SHA-256, SHA-3 | MD5, SHA-1 |
| Password hashing | Argon2id, bcrypt (cost ≥ 12) | plain SHA-*, MD5 |
| Symmetric encryption | AES-256-GCM | DES, 3DES, AES-ECB, RC4 |
| Asymmetric | RSA ≥ 3072, Ed25519, ECDSA P-256 | RSA < 2048 |
| Random tokens | `secrets`, `crypto.randomBytes`, `/dev/urandom` | `Math.random()`, `rand()` |

## CRYPTO-02 — No hard-coded secrets

Secrets, API keys, connection strings, and signing keys MUST come from the
secrets manager at runtime. They MUST NOT appear in:

- source code (including tests)
- configuration files committed to Git
- environment-variable defaults in Dockerfiles
