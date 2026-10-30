# Scientific Agent Skills — preregistration-style engineering experiment plan

**Written:** 2026-10-30, **before any TGWS-CORE runtime implementation or measurements**. All claims below are candidate hypotheses, **not observed defects**. Based on the hypothesis-generation workflow of K-Dense-AI/scientific-agent-skills. No mobile data, accounts or production endpoints are involved.

## Evidence boundary

Observed: TGWS-CORE baseline contains one README and no runnable code/tests. Reference concepts: Flowseal/tg-ws-proxy public source, official Android/Apple docs, Cloudflare Workers docs. No benchmarks were run. A local TGWS-Android predecessor exists but is excluded from source reuse; its results are not transferred to this project.

## Preregistered outcomes

- **Reliability:** successful post-auth transport setup / eligible attempts; close-category distribution; owned socket count reaches zero after stop.
- **Latency:** per-stage `dns_ms`, `tcp_ms`, `tls_ms`, `upgrade_ms`, total ready time (p50/p95 from per-attempt samples; retain all failures).
- **Capacity:** peak resident memory, queued bytes, live/closing session count, CPU, release of descriptors.
- **Correctness:** exact cryptographic/frame golden vector match, zero plaintext replays, zero route-policy violations.
- **Privacy:** exact-match scan for fixed dummy secret and private endpoint marker in event/report fixtures.

Do not use one successful WSS Upgrade as the dependent variable for Telegram message delivery.

## Rival hypotheses and differentiating tests

| ID | Candidate mechanism | Rival explanation | Discriminating prediction and refutation |
| --- | --- | --- | --- |
| H-01 | layered packet copying causes memory spikes | TLS implementation buffers dominate | Compare peak RSS with/without transport queue under the **same local** 4 MiB patterned fixture; if footprint unchanged within measurement resolution, H-01 is not supported |
| H-02 | fallback policy leaks direct TCP when relay fails | apparent direct TCP belongs to a separate legal session | Record per-attempt dummy route labels; any direct dial in RELAY_ONLY refutes policy invariant; correlate event generation, not just timestamps |
| H-03 | old-network dial completion revives stale sessions | fresh-session retry appears similar | Delay generation-1 dial, switch generation, finish old dial; ownership of any generation-1 socket after switch supports H-03 |
| H-04 | long media transfer stalls on missing backpressure | peer bandwidth or configured byte limit ends transfer | Two isolated peers, same bytes with rapid vs throttled consumer, compare queued-byte ceiling and stop latency; violating the ceiling supports H-04 |
| H-05 | iOS suspension interrupts local proxy when Telegram becomes foreground | remote peer is unreachable irrespective of app state | First test local listener + deterministic echo; then transition from app to Telegram on a physical device, compare with foreground control; no claim before paired results |
| H-06 | Worker lifetime budget cuts media | server-side Telegram route fails first | Use only an isolated Worker-compatible fake bridge with defined byte budget and a local peer; classify cause with safe fixed close codes, not one timeout |

## Reproducibility rules

- Run local cases with loopback-only peers and dummy credentials; fixed protocol vectors, seeded schedule where possible, code SHA, tool versions and CPU/RAM bounds recorded.
- For variable timing results, use at least 3 repeated runs **as an initial engineering screening plan**, not a universal statistical sample size; publish all individual measures, not only favorable averages.
- Use an empty environment allowlist, no external network, CPU/memory/process/wall-clock limits, read-only checked-out source and scratch-only writes. If unavailable, mark tests **not executed**.
- Controls: known-good local echo, deliberate invalid secret, invalid TLS cert, protocol-length violations, fake relay unreachable; keep media case bytes deterministic and non-user data.
- Aborted, inconclusive and missing measurements stay visible. Any changed hypothesis after initial observations is labeled exploratory.

**No hypothesis has been accepted/rejected; no measured effect sizes exist.**
