# Security policy (pre-implementation)

TGWS-CORE is an **unimplemented design**. No stable/security-supported release or dependency security claim exists.

Do not put real MTProto secrets, tokens, credential-bearing URLs, crash dumps, device/network identifiers or exploitable vulnerabilities in public issues. Use GitHub's private **Security → Report a vulnerability** feature when available; otherwise contact the repository maintainer privately to agree on a secure channel first.

Security invariant proposals are in [docs/SECURITY_THREAT_MODEL.md](docs/SECURITY_THREAT_MODEL.md). Test requirements are in [docs/TEST_MATRIX.md](docs/TEST_MATRIX.md). Any future Cloudflare Worker and mobile binary must be audited separately at their deployed/signed revisions.
