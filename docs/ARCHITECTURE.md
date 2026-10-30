# TGWS-CORE — architecture decision record (proposed)

> **Coordination note:** [TECHNICAL_SPECIFICATION.md](TECHNICAL_SPECIFICATION.md) is the requirements baseline and [INTEGRATION_CONTRACT.md](INTEGRATION_CONTRACT.md) owns the integration contract. The ABI outline below is a discussion sketch, not an override or competing approved interface.\n\n**Snapshot:** 2026-10-30; baseline `main` commit `c2681d8950a990588b1f1b746ada83be87f03080`. **Status: proposed, not implemented.**

## System boundaries

```text
Android (Kotlin/Compose)              iOS (Swift/SwiftUI)
       | UI + OS lifetime                   | UI + OS lifetime
       +---- Platform Adapter / capability negotiation ----+
                  | stable versioned ABI (candidate)      |
                  v                                       v
                 Core facade: start / stop / status / events
                            |
                 Policy + session supervisor
                /            |              \
         Local listener   Crypto/framing    Route planner
                            |              |
                       MTProto bytes   DNS/TCP/WSS connectors
                                            |
                                  Optional owner relay / DC
```

Platform adapters provide clocks, entropy, network identity, DNS/sockets or platform-compatible handles, persistent secret access, app states and secure event delivery. No UI framework, background privilege or filesystem path is compiled into core policy.

## Modules to implement

- `core-api`: typed config, explicit capabilities, version negotiation and safe diagnostics.
- `listener`: bound strictly to selected loopback family/port; isolated local clients.
- `mtproto`: deterministic framing, secret validation and reversible stream cipher state; parity tests from upstream.
- `session`: per-session owner, deadlines, capacity guards, cancellation generation and memory accounting.
- `transport`: strict WSS/TLS and bounded TCP adapters; no arbitrary remote destination selection.
- `routing`: explicit modes `DIRECT`, `RELAY_ONLY`, `AUTO`; allowlist-based fallback and backoff.
- `observability`: enum-and-counter-only events; no plaintext, private URLs, tokens or provider exceptions.

Core does **not** implement a system VPN. Native app and optional entitlement-constrained extensions remain platform-specific.

## Candidate stable interface (not yet an ABI)

```text
tgws_api_version() -> {major,minor,features}
tgws_create(config_bytes, callbacks) -> opaque_handle | error
tgws_start(handle) -> result
tgws_update_network(handle, generation, capabilities) -> result
tgws_poll_event(handle, event_buffer, capacity) -> length | error
tgws_stop(handle) -> result
tgws_destroy(handle) -> result
```

Requirements: explicit buffer lengths and maximums; no borrowed pointer retained; same allocator frees both sides or caller-owned buffers; no exceptions unwind over C; callbacks cannot call into destroyed handles; serialized ownership of session state; idempotent stop; deterministic shutdown even when a dial is blocked. Use typed tagged versioned event records and documented endianness. **Do not implement this pseudocode verbatim without an ABI review.**

## Language decision (ADR-0001)

**Candidate A — Rust core / C ABI:** strongest language-level memory discipline and identical protocol logic; cost: native packaging, ABI, async cancellation, FFI validation, iOS distribution. **Candidate B — Kotlin Multiplatform:** simpler Android integration; iOS socket/background and library ecosystem require direct proof, and bridging Swift is not automatically simple. **Candidate C — separate Kotlin+Swift engines:** quickest OS-native access, but protocol/security parity burden doubles. Prefer **A only after a two-device technical spike** and equivalent API tests.

## Non-negotiable invariants

1. A client with no valid local MTProto secret cannot cause an outbound dial.
2. No fallback or hidden direct route violates explicit user policy.
3. Once payload consumes a stream cipher state, an attempt must not transparently replay it on another connection.
4. Untrusted peer frames cannot exceed configured per-message/per-session memory budgets.
5. Network generation N never overwrites a connected generation N+1.
6. All sockets and tasks are owned, cancelable, and released on stop.
7. UI, event streams and crash reports cannot reveal secrets or raw packet data.

These are **specification conditions**, not claims of passing tests.
