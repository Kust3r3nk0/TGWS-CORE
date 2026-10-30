# TGWS-CORE

> **Status: architecture/specification only.** There is no runnable MTProto proxy, compiled library, FFI, or verified Android/iOS transport in this repository as of 2026-10-30. Passing specification checks does not mean the proxy works.

TGWS-CORE is the planned **platform-independent network engine** for [TGWS-CLODEX](https://github.com/Kust3r3nk0/TGWS-CLODEX), an unofficial, independent Android/iOS port inspired by [Flowseal/tg-ws-proxy](https://github.com/Flowseal/tg-ws-proxy). The predecessor TGWS-Android is a historical reference, **not** the codebase to be copied.

## Responsibilities

| In this repository | Owned by TGWS-CLODEX |
| --- | --- |
| MTProto obfuscated transport and local loopback listener | Android/iOS UI, service/extension lifecycle |
| Bounded WSS/TCP connections and routing | OS permissions, DNS/network adapters and secure storage |
| Cancellation, backpressure, diagnostics, portable API | Packaging, store policy, distribution and update signing |
| Reference fixtures, fuzz/property/integration tests | Cross-platform hardware and background tests |

## First decisions

- **Safety:** no externally bound listener by default; strict TLS verification; no silent direct fallback from relay-only mode; no payload replay across attempts.
- **Portability:** separate platform capabilities from core semantics. Rust with a versioned C ABI is a *candidate*, not an approved stack. Require an Android + iOS spike before choosing it.
- **Truthful status:** the proxy is not implemented; no cloud relay, Cloudflare account, release, or official Telegram E2E is assumed.
- **Licensing:** this repository has no chosen project license. If original code is incorporated, comply with its license and notices.

## Design documents

- [Architecture and API boundaries](docs/ARCHITECTURE.md)
- [Network flows and failure semantics](docs/NETWORK_INTERACTIONS.md)
- [Security threat model and audit baseline](docs/SECURITY_THREAT_MODEL.md)
- [Scientific experiment plan](docs/EXPERIMENTS.md)
- [Test matrix and execution rules](docs/TEST_MATRIX.md)
- [Coordinated disclosure](SECURITY.md)

## Presently runnable check

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

This **only validates machine-readable design fixtures** in `contracts/scenarios.v1.json`. It does not compile a core, open sockets, authenticate a Telegram session, or test the implementation. See [test matrix](docs/TEST_MATRIX.md) for the gated future integration suite.

Reference upstream: Flowseal/tg-ws-proxy, with behavioral comparisons pinned to a separately recorded upstream commit/tag when implementation begins. No affiliation with Flowseal or Telegram is claimed.
