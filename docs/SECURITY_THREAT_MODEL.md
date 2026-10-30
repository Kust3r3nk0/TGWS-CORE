# Security model & architecture-stage audit

**Date:** 2026-10-30. Baseline `c2681d8950a990588b1f1b746ada83be87f03080`. Scope: sole `README.md` in TGWS-CORE; external TGWS-CLODEX README reviewed for interface assumptions. This is **a design review, not a runtime vulnerability scan or pentest**.

**Audit result:** 0 confirmed runtime vulnerabilities, because **no executable core, dependencies, builds, binaries or deployment configuration existed** at the examined source ref. This does not certify security. Prior findings ledger: none. Runtime and operational coverage: blocked (code unavailable).

## Principals, resources and boundaries

| Lower-trust actor / input | Target resource | Required last-decision check | Attack class |
| --- | --- | --- | --- |
| Other same-device app or local process | local proxy listener | loopback bind + MTProto secret + admission | unauthorized use, local DoS |
| Peer-supplied MTProto init / framing | memory and upstream | reject invalid secret/length/DC before dial | parser abuse, resource exhaustion |
| User-controlled custom relay URL | outgoing TCP/WSS | allowlisted scheme/host/path/port and TLS | SSRF, credential exfiltration |
| Untrusted remote WebSocket/TLS peer | session and bytes | platform hostname/trust + WS frame limits | MITM, parser misuse |
| Network callback from old epoch | current session | generation ownership before mutation | stale socket/session contamination |
| Cross-platform FFI caller | native buffers/handles | ownership, lengths, version and thread-safety | UAF, double-free, crash |
| Diagnostic export / logcat / crash | secrets and private endpoints | typed redacted events, opt-in export | disclosure |
| Release pipeline / third-party dependencies | installed app/library | pinned provenance, signing and review | supply-chain compromise |

## Proposed defenses

- Keep the local secret in Keystore (Android) / Keychain (iOS) via platform adapter; do not export secret to analytics, logs or backups.
- Apply explicit size, count and time quotas before costly allocation, upstream connection or response.
- Check all configured destinations against policy after parsing and again immediately before dial; do not add an open TCP proxy or bypass DNS binding.
- TLS default verification required for all WSS endpoints; no user switch to ignore certificate errors.
- Upstream crypto parity checked against pinned Flowseal vectors; crypto review required before claiming interoperability.
- Maintain native library signature and checksum provenance per mobile build; no debug-signed production.
- Optional Cloudflare Worker must have a separate deployment and privacy audit (secrets, route restrictions, logs, capacity, account quotas).

## Finding classification

**CONFIRMED:** none. **NEEDS VALIDATION:** all rows above are future trust boundaries, not exploited vulnerabilities. **DESIGN RISKS:** memory pressure from layered 4 MiB buffers; canceled dial reactivation; unexpected direct fallback; iOS background suspension; exposing relay tokens through request paths/telemetry.

## Mandatory security gates

1. Real code exists, review exact commit SHA and complete tree.
2. Independently replay isolated, dummy-principal tests without network access.
3. Verify API memory ownership, release signing, platform privileges and deployment settings.
4. Track findings with specific affected principal, wrong result, minimal local reproduction, source location and fix; add severity **only for confirmed findings**.
5. Recheck after fixes. Never conclude production safe from green specification CI.
