# CLAUDE.md — Aviatrix Cribl Stream Pack

## Project Overview

This is a **Cribl Stream Pack** that parses, normalizes, and routes Aviatrix Cloud Network syslog data for delivery to any SIEM or observability destination. It is a native Cribl replacement for the standalone [Aviatrix SIEM Connector](https://github.com/AviatrixSystems/aviatrix-siem-connector) (Logstash-based).

**Primary goal:** Publish to the Cribl Packs Dispensary — first as a community pack (`cc-aviatrix-siem`), then upgrade to a Cribl-certified vendor pack (`cribl-aviatrix-siem`).

## Upstream Reference: log-integration-engine

The source of truth for parsing logic lives at:
```
/Users/christophermchenry/Documents/Scripting/log-integration-engine
```

This is the Aviatrix SIEM Connector (formerly "Log Integration Engine") — a modular Logstash ETL. The Cribl pack must stay in sync with it.

### Key files in log-integration-engine

| Path | Purpose |
|------|---------|
| `logstash-configs/filters/10-microseg.conf` | L4 microseg parsing (3 formats) |
| `logstash-configs/filters/11-l7-dcf.conf` | L7/MITM TLS inspection |
| `logstash-configs/filters/12-suricata.conf` | Suricata IDS/IPS JSON |
| `logstash-configs/filters/13-fqdn.conf` | FQDN firewall |
| `logstash-configs/filters/14-cmd.conf` | Controller CMD/API audit |
| `logstash-configs/filters/15-gateway-stats.conf` | Gateway net+sys stats |
| `logstash-configs/filters/16-tunnel-status.conf` | Tunnel state changes |
| `logstash-configs/filters/17-cpu-cores-parse.conf` | CPU cores protobuf parser |
| `logstash-configs/filters/90-timestamp.conf` | Timestamp normalization |
| `logstash-configs/filters/95-field-conversion.conf` | Type conversions |
| `logstash-configs/patterns/avx.conf` | Custom Grok patterns |
| `test-tools/sample-logs/test-samples.log` | Test data (all 8 log types) |

### Sync strategy

Changes in log-integration-engine should be reflected here. Two approaches:
1. **Manual:** Diff log-integration-engine commits, update Cribl pipeline functions accordingly
2. **AI-assisted:** Use Claude to analyze diffs from log-integration-engine tags and generate corresponding Cribl conf.yml updates. See `docs/SYNC_STRATEGY.md`.

## Pack Architecture

Single pipeline (`avx-parse`) with 5 grouped stages:

```
1. Classify & Tag    → Detect log type from _raw, set __avx_type + __avx_profile
2. Parse Security    → Grok + JSON for microseg, L7/MITM, suricata, FQDN, CMD
3. Parse Networking  → Grok for gateway stats, tunnel status, cpu_cores protobuf
4. Normalize         → Timestamp → epoch, field type conversions
5. Finalize          → Set avx_sourcetype, avx_source, avx_host, avx_log_profile
```

## Supported Log Types

| Log Type | Tag | avx_sourcetype | Profile |
|----------|-----|----------------|---------|
| L4 Microsegmentation | `microseg` | `aviatrix:firewall:l4` | security |
| L7/TLS Inspection | `mitm` | `aviatrix:firewall:l7` | security |
| Suricata IDS/IPS | `suricata` | `aviatrix:ids` | security |
| FQDN Firewall | `fqdn` | `aviatrix:firewall:fqdn` | security |
| Controller API Audit | `cmd`/`cmd_v2` | `aviatrix:controller:audit` | security |
| Gateway Network Stats | `gw_net_stats` | `aviatrix:gateway:network` | networking |
| Gateway System Stats | `gw_sys_stats` | `aviatrix:gateway:system` | networking |
| Tunnel Status | `tunnel_status` | `aviatrix:tunnel:status` | networking |

## File Structure

```
aviatrix-cribl-pack/
├── CLAUDE.md                          # This file
├── README.md                          # Customer-facing docs (shipped in pack)
├── LICENSE                            # MIT
├── pack.yml                           # Pack metadata (id, version, author, tags)
├── routes.yml                         # Route: match Aviatrix syslog → avx-parse pipeline
├── pipelines/
│   └── avx-parse/
│       └── conf.yml                   # Main pipeline: 5 stages, all parsing logic
├── knowledge/
│   └── grok/
│       └── aviatrix.conf              # Custom Aviatrix Grok patterns
├── samples/
│   └── aviatrix-syslog.log            # 44 sample events (all 8 log types)
├── docs/                              # Internal documentation (not shipped in pack)
│   ├── STRATEGY.md                    # Publishing strategy & GTM plan
│   ├── SYNC_STRATEGY.md              # Sync with log-integration-engine
│   ├── DISPENSARY_REQUIREMENTS.md    # Cribl Packs Dispensary checklist
│   └── LOGSTASH_MAPPING.md           # Filter-by-filter mapping reference
├── previous-exploration/              # Original prototype files (reference only)
└── .github/
    └── workflows/                     # CI/CD (future)
        └── build-pack.yml            # Build .crbl on tagged releases
```

## Build & Test

### Build .crbl file
```bash
# A .crbl file is just a tar.gz of the pack contents
tar -czf aviatrix-siem-$(cat pack.yml | grep version | awk '{print $2}').crbl \
  pack.yml routes.yml README.md \
  pipelines/ knowledge/ samples/
```

### Test in Cribl Stream
1. Import pack: Processing → Packs → Add Pack → Import from File
2. Open pipeline: Processing → Pipelines → avx-parse
3. Select sample: aviatrix-syslog.log
4. Preview and verify all 8 log types parse correctly

### Test with live syslog
```bash
# From log-integration-engine test tools:
cd /Users/christophermchenry/Documents/Scripting/log-integration-engine/test-tools/sample-logs
python3 stream-logs.py --target <cribl-worker-ip> --port 5000
```

## Versioning & Release Strategy

- **0.x.y** — Development / community review
- **1.0.0** — First Dispensary submission
- Tag format: `v0.1.0`, `v1.0.0`
- Each tagged release triggers GitHub Action to build `.crbl` artifact
- Cribl Dispensary updates are manual uploads (no automated publishing API)

## Dispensary Submission Checklist

- [ ] Pack has at least one pipeline with Comment functions and descriptions
- [ ] Sample data covers all log types
- [ ] Route uses `_raw.match()` regex (not sourcetype-based)
- [ ] Catch-all route with `filter: true` → `devnull` is present
- [ ] All Grok patterns self-contained (no external dependencies)
- [ ] README has: purpose, configuration, support contact, release notes
- [ ] Aviatrix logo included
- [ ] No sensitive data in samples or configs
- [ ] `minCriblVersion` set in pack.yml
- [ ] Function descriptions on every function (Dispensary standard)
- [ ] Splunk sourcetype mapping backward-compatible with existing dashboards

## Key Design Decisions

1. **Single pipeline** — All 8 log types in one pipeline (not 8 pipelines) to match Logstash's single-filter-chain model and simplify the customer route config.
2. **Internal fields prefixed with `__`** — Cribl convention for working fields (auto-cleaned or explicitly removed).
3. **Grok patterns in knowledge/grok/** — Cribl's pack-scoped knowledge objects, auto-loaded.
4. **`avx_` field prefix** — All output fields prefixed to avoid collision with customer data.
5. **No output configuration** — Pack handles parsing only; customers configure their own destinations.
