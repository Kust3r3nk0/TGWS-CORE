# Reproducible verification matrix

**Today runnable:** `python3 -m unittest discover -s tests -p 'test_*.py' -v` verifies **fixture structure only**. Future CORE integration tests below do **not** exist yet. Do not label them passed. All remote peers must be isolated local mocks unless an owner explicitly performs separate device acceptance.

| Test ID | Precondition and stimulus | Required oracle | Layer | Current status |
| --- | --- | --- | --- | --- |
| CORE-001 | Bind localhost on 1443, connect from loopback and non-loopback | no public listener | integration | planned |
| CORE-002 | Valid-length init with wrong dummy secret | reject with 0 remote dials | protocol | planned |
| CORE-003 | 63-byte init then EOF | close within deadline | protocol | planned |
| CORE-004 | Untrusted localhost WSS certificate | TLS failure; never ignore hostname | integration | planned |
| CORE-005 | RELAY_ONLY with dead relay | no direct route | integration | planned |
| CORE-006 | WSS refusal and permitted TCP | once-only connection; no replay | integration | planned |
| CORE-007 | delayed dial from old network generation | no stale session | integration | planned |
| CORE-008 | 9 clients with max 8 | bounded session and queue | load | planned |
| CORE-009 | throttled receiver | bounded RSS/queue and stop | load | planned |
| CORE-010 | stop during TLS stall | no leaked descriptor; port reusable | integration | planned |
| CORE-011 | dummy credential marker in input | not in exported events | unit | planned |
| CORE-012 | fragmented 4 MiB message | byte-exact, bounded memory | load | planned |
| CORE-013 | optional Worker arbitrary dst | no outbound dial | future | blocked: no Worker |
| CORE-014 | FFI double-stop and stale handle | no UAF/double-free | future | blocked: no ABI |

Cases and falsifiable oracles are also recorded in [JSON](../contracts/scenarios.v1.json). The current Python unit checks are **specification lint**, not tests of these oracles.

## Execution blueprint when implementation exists

1. Pin source SHA, reference upstream SHA, compiler/runtime versions, fixture SHA and platform build.
2. Use local encrypted test peer, self-signed test-only CA, controlled clock for backoff, fixed dummy secret, and deterministic binary frames.
3. Record command, allowlisted environment, quotas and test result. Run network programs only in an OS-enforced **network-disabled sandbox with isolated loopback**, read-only source, scratch-only writes and resource limits.
4. Compare exact ciphertext/plaintext reference vectors without logging live secrets; run both valid and invalid fixtures.
5. Add stress with 1, 4, 8 and 9 sessions and 1 KiB / 64 KiB / 4 MiB messages. Repeat over network loss and stop/restart.
6. Repeat platform acceptance on devices only after the owner approves it; record **status by OS** without public identifiers or private relay addresses.

## Work allocation

- **P0:** implement and test minimal loopback listener + shutdown; confirm iOS app-to-Telegram feasibility first.
- **P1:** cryptographic/framing fixtures, WSS/TLS and routing policy.
- **P2:** failure injection, backpressure, network epoch, FFI resource ownership.
- **P3:** media and device long-run data (only after privacy review).

Never turn a planned case green using a stub that simply returns expected constants.
