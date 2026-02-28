# Logstash → Cribl Filter Mapping Reference

## Overview

This document maps every Logstash filter from the log-integration-engine to its corresponding Cribl pipeline function in `pipelines/avx-parse/conf.yml`.

## Filter-by-Filter Mapping

### 10-microseg.conf → Stage 2a: L4 Microsegmentation

| Logstash Element | Cribl Function | Notes |
|-----------------|----------------|-------|
| Grok: 8.2+ with SESSION fields | `grok` filter: `__avx_type === 'microseg' && /SESSION_ID=/.test(_raw)` | Full session pattern |
| Grok: 8.2+ without SESSION | `grok` filter: `__avx_type === 'microseg' && !/SESSION_ID=/.test(_raw) && /POLICY=/.test(_raw)` | First-packet format |
| Grok: Legacy 7.x (SPT/DPT) | `grok` filter: `__avx_type === 'microseg' && /SPT=/.test(_raw)` | Legacy field names |
| Mutate: add_tag microseg | Stage 1 Classify: `__avx_type = 'microseg'` | Tag-based → field-based |
| N/A (Logstash default) | `eval` filter: `__avx_type === 'microseg' && src_ip === undefined` | Defaults for legacy |

### 11-l7-dcf.conf → Stage 2b: L7/TLS Inspection

| Logstash Element | Cribl Function | Notes |
|-----------------|----------------|-------|
| Grok: syslog header + JSON | `grok` filter: `__avx_type === 'mitm'` | Extracts `__json_payload` |
| JSON codec parse | `code` filter: `__avx_type === 'mitm' && __json_payload` | `JSON.parse()` + field mapping |
| Mutate: rename fields | Same `code` function | Maps MITM JSON → normalized fields |
| Ruby: timestamp override | Same `code` function | `_time = payload.timestamp` |
| Mutate: DROP → DENY | Same `code` function | Action normalization |

### 12-suricata.conf → Stage 2c: Suricata IDS/IPS

| Logstash Element | Cribl Function | Notes |
|-----------------|----------------|-------|
| Grok: syslog header | `grok` filter: `__avx_type === 'suricata'` | Extracts `__suricata_json` |
| Drop non-JSON | `drop` filter: regex test for non-`{` start | Removes startup notices |
| JSON codec | `code` filter: `__avx_type === 'suricata' && __suricata_json` | Full JSON parse |
| Flatten alert.* | Same `code` function | `signature`, `severity`, etc. |
| Flatten flow.* | Same `code` function | `flow_pkts_toserver`, etc. |
| Flatten http.* | Same `code` function | `http_hostname`, `http_url`, etc. |
| Flatten tls.* | Same `code` function | `tls_sni`, `tls_subject` (no cert blobs) |
| Flatten dns.* | Same `code` function | `dns_query`, `dns_rrname`, etc. |
| Drop stats events | `drop` filter: `__drop === true` | Stats flagged in code function |
| Ruby: HEC payload builder | Not needed in Cribl | Cribl destinations handle serialization |

### 13-fqdn.conf → Stage 2d: FQDN Firewall

| Logstash Element | Cribl Function | Notes |
|-----------------|----------------|-------|
| Grok: S_IP/D_IP/hostname/state | `grok` filter: `__avx_type === 'fqdn'` | Standard pattern |
| Ruby: optional fields | `code` filter: `__avx_type === 'fqdn'` | Regex for drop_reason, Rule |

### 14-cmd.conf → Stage 2e: Controller CMD/API

| Logstash Element | Cribl Function | Notes |
|-----------------|----------------|-------|
| Grok: AviatrixCMD with username | `grok` filter: `__avx_type === 'cmd'` | V1 format |
| Grok: AviatrixCMD without username | `grok` filter: `__avx_type === 'cmd' && action === undefined` | Fallback |
| Grok: AviatrixAPI (V2.5) | `grok` filter: `__avx_type === 'cmd_v2'` | New API format |
| Mutate: set gw_hostname | `eval` filter: `__avx_type === 'cmd' \|\| __avx_type === 'cmd_v2'` | Controller hostname |

### 15-gateway-stats.conf → Stage 3a + 3b: Gateway Stats

| Logstash Element | Cribl Function | Notes |
|-----------------|----------------|-------|
| Grok: AviatrixGwNetStats | `grok` filter: `__avx_type === 'gw_net_stats'` | Many optional fields |
| Ruby: rate string → bytes | `code` filter: `__avx_type === 'gw_net_stats'` | `parseRate()` function |
| Grok: AviatrixGwSysStats | `grok` filter: `__avx_type === 'gw_sys_stats'` | cpu_idle, memory, disk |

### 16-tunnel-status.conf → Stage 3c: Tunnel Status

| Logstash Element | Cribl Function | Notes |
|-----------------|----------------|-------|
| Grok: src_gw/dst_gw/state | `grok` filter: `__avx_type === 'tunnel_status'` | Basic extraction |
| Ruby: parse gateway(Cloud Region) | `code` filter: `__avx_type === 'tunnel_status'` | Cloud/region decomposition |

### 17-cpu-cores-parse.conf → Stage 3b: CPU Cores

| Logstash Element | Cribl Function | Notes |
|-----------------|----------------|-------|
| Ruby: protobuf text parser | `code` filter: `__avx_type === 'gw_sys_stats' && cpu_cores_raw` | Regex-based extraction |
| Ruby: aggregate + per-core | Same `code` function | `cpu_cores_parsed` array |

### 90-timestamp.conf → Stage 4: Normalize

| Logstash Element | Cribl Function | Notes |
|-----------------|----------------|-------|
| Date filter: various formats | `code` filter: `date !== undefined && _time === undefined` | JS `new Date()` parsing |
| Ruby: @timestamp → unix_time | Same `code` function | `Math.floor(ts/1000)` |

### 95-field-conversion.conf → Stage 4: Normalize

| Logstash Element | Cribl Function | Notes |
|-----------------|----------------|-------|
| Mutate: convert string → int | `eval` per log type | `Number(field)` expressions |

### 96-sys-stats-hec.conf → Not Needed

The Logstash HEC payload builder (`96-sys-stats-hec.conf`) is not needed in Cribl because Cribl's Splunk HEC destination handles serialization natively.

## Fields Not Ported (Intentionally)

| Logstash Field | Reason |
|---------------|--------|
| `[hec_payload]` | Cribl destinations handle HEC format |
| `[@metadata]` | Logstash-specific routing mechanism |
| `[tags]` | Replaced by `__avx_type` field-based routing |
| Output-specific ASIM fields | ASIM normalization is output-specific; may be added as separate pipeline |
