# Network flow, trust boundaries and failure behavior

**Status:** target network behavior; no working engine exists in TGWS-CORE yet.

## Expected flow

```text
Telegram client -> OS loopback -> local listener -> secret check -> MTProto framing
  -> policy gate -> active-network DNS/TCP -> TLS+WSS or permitted direct TCP
  -> [optional configured owner relay] -> Telegram DC
```

- Loopback is not a security boundary against all other applications on the same device. A separate MTProto secret is required, and local acceptance must be capacity-limited.
- Direct TCP is not TLS and must not be described as TLS authenticated. MTProto transport obfuscation is not Telegram end-to-end encryption.
- WSS must validate certificate chain and hostname; requested SNI must match the intended host; never disable trust checks to force connectivity.
- Unknown DC, arbitrary destination/IP/port, untrusted redirect, arbitrary URL path and incompatible protocol tags must fail closed.
- WSS endpoint and relay authorization should be bounded to user-selected allowlists; an optional relay needs its **own** inbound authentication and server-side destination allowlist.
- DNS resolution is performed within the currently selected OS network context; an old result must not revive a stale attempt.

## Policy and transition table

| State | Event | Allowed next state | Forbidden behavior |
| --- | --- | --- | --- |
| STOPPED | explicit start | STARTING | Start from stale callback |
| STARTING | listener ready | LISTENING | Claim Telegram connected |
| LISTENING | authenticated local handshake | CONNECTING | Dial before authentication |
| CONNECTING | permitted remote ready | ACTIVE | Replay encrypted payload on route change |
| CONNECTING | failed route | CONNECTING or FAILED | Bypass RELAY_ONLY/MANUAL restriction |
| ACTIVE | network changed | CLOSING -> LISTENING | Continue old-network session |
| Any live state | explicit stop | CLOSING -> STOPPED | Leave sockets/tasks running |

A transport handshake success proves **only** transport establishment; a protocol response proves a narrower MTProto step; actual Telegram message/media delivery needs device E2E observation.

## Resource and retry design

- Proposed defaults **for prototyping, not production commitments:** 8 local sessions; 10 s local handshake; 25 s overall route setup; 8 s single dial; 10 s stalled write; 5 min useful-data idle deadline; maximum framed payload 4 MiB. Review these with platform measurements.
- Use a bounded queue of at most one max-size message per direction per session, and explicit admission accounting for queued, active and closing sessions. Avoid packet-sized copies at each layer.
- Backoff is per route with bounded exponential cooldown. Count socket setup, payload progress and clean close separately.
- Close by resource owner; no wait on a future that requires the same event-loop thread to make progress.
- No automatic retry once application payload has advanced stream cipher state. Recover by closing and allowing the client to re-establish a fresh session.

## Optional Cloudflare transport

Cloudflare Worker is **not in either repository and is not deployed by this design**. If implemented later, review Worker runtime connection limits, buffering, token location/telemetry and upstream socket lifetime separately; never assume unlimited WebSocket send backpressure. The source of truth is the future pinned Worker deployment, not a README example.

## Observable events

Publish fixed `phase`, `transport_kind`, `close_category`, `network_generation` and aggregate timings/counters. Never export unredacted credential URL, secret, IP/name of a private relay, Telegram content, socket exception string, network operator or device identifiers.
