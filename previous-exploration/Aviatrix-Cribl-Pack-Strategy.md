# Aviatrix Cribl Stream Pack — Strategy & Publishing Plan

## Executive Summary

Cribl Stream customers can replace the standalone Aviatrix SIEM Connector (Logstash-based) with a native **Cribl Pack** that runs inside their existing Cribl infrastructure. This eliminates the need for customers to deploy and manage separate EC2 instances, NLBs, and Logstash containers. The Pack can be published to Cribl's built-in marketplace — the **Packs Dispensary** — where customers discover, install, and upgrade it with one click directly from the Cribl Stream UI.

A working Pack prototype has been built that ports all 8 log types from the [aviatrix-siem-connector](https://github.com/AviatrixSystems/aviatrix-siem-connector) repo, including legacy 7.x and 8.2+ session formats, Suricata JSON flattening, cpu_cores protobuf parsing, and the full security/networking log profile routing model.

---

## What the Pack Does

The Pack is a single Cribl pipeline with 5 stages that replaces the entire Logstash filter chain:

| Stage | Function | Logstash Equivalent |
|-------|----------|-------------------|
| 1. Classify & Tag | Detect log type from raw syslog, set internal routing fields | Filter ordering + `add_tag` |
| 2. Parse Security | Grok + JSON extraction for microseg, L7/MITM, Suricata, FQDN, CMD | Filters 10-14 |
| 3. Parse Networking | Grok extraction for gateway stats, tunnel status | Filters 15-17 |
| 4. Normalize | Timestamp parsing, field type conversion, computed metrics | Filters 90-95 |
| 5. Finalize | Set `avx_sourcetype`, `avx_source`, `avx_host`, `avx_log_profile` | Filter 96 + output routing |

### Supported Log Types

| Log Type | Sourcetype | Profile | Description |
|----------|-----------|---------|-------------|
| L4 Microsegmentation | `aviatrix:firewall:l4` | security | eBPF-enforced network policy with session tracking |
| L7/TLS Inspection | `aviatrix:firewall:l7` | security | traffic_server TLS proxy inspection |
| Suricata IDS/IPS | `aviatrix:ids` | security | Intrusion detection alerts (JSON, flattened) |
| FQDN Firewall | `aviatrix:firewall:fqdn` | security | DNS-based firewall rule hits |
| Controller API Audit | `aviatrix:controller:audit` | security | V1 (AviatrixCMD) and V2.5 (AviatrixAPI) formats |
| Gateway Network Stats | `aviatrix:gateway:network` | networking | Interface throughput, conntrack, rate limit violations |
| Gateway System Stats | `aviatrix:gateway:system` | networking | CPU (with per-core detail), memory, disk |
| Tunnel Status | `aviatrix:tunnel:status` | networking | Up/down changes with cloud/region context |

### Log Profiles for Selective Routing

Every event is tagged with `avx_log_profile` enabling customers to split data by use case:

- **`security`** → SIEM / SOC (microseg, L7, Suricata, FQDN, CMD)
- **`networking`** → NOC / Observability (gateway stats, tunnel status)

This replaces the `LOG_PROFILE` environment variable from the Logstash connector with native Cribl routing.

---

## Cribl Packs Dispensary — The Marketplace

### What It Is

The **Packs Dispensary** ([packs.cribl.io](https://packs.cribl.io)) is Cribl's built-in marketplace for shareable configuration packages. It's accessible directly from the Cribl Stream UI under **Processing → Packs → Add Pack → Add from Dispensary**. Existing vendor packs include Palo Alto Networks, CrowdStrike, Corelight, Microsoft Windows Events, and Exabeam.

### How Customers Access It

Customers browse or search the Dispensary from within their Cribl deployment. They can filter by data type, use case (e.g., "Security", "Enrichment"), and technology. Clicking a pack tile shows the README, and **Add Pack** installs it instantly — pipeline, routes, grok patterns, sample data, and all.

### Upgrade Experience

When a new version is published, customers see an upgrade indicator on their Packs page and can update with one click. If they've made local modifications, Cribl preserves their changes and lets them reconcile side-by-side.

---

## Publishing Requirements

### Pack Naming

| Path | Pack ID Format | Author Format | Notes |
|------|---------------|--------------|-------|
| Community | `cc-aviatrix-siem` | `Chris - cc` | Anyone can publish; author-supported |
| Vendor Partnership | `cribl-aviatrix-siem` | `Aviatrix` or `Cribl Packs Team` | Requires Cribl partnership; Cribl-validated |

**Recommendation:** Pursue the vendor partnership path. Packs in the `cribl-` namespace get the "Built by Cribl" badge and higher visibility in the Dispensary. Vendors like Palo Alto and CrowdStrike have done this.

### Required Pack Contents

| Component | Requirement | Status in Prototype |
|-----------|-------------|-------------------|
| Pipeline(s) | At least one, with Comment functions and descriptions | ✅ Built — single pipeline, 5 grouped stages |
| Sample data | At least one sample per pipeline | ✅ Built — 44 events covering all 8 log types |
| Routes | Generic filters using `_raw.match()`, not sourcetype | ✅ Built — regex match on Aviatrix log patterns |
| Catch-all route | Final route with `filter: true` to `devnull` | ⚠️ Needs to be added |
| Knowledge objects | All Grok patterns self-contained in pack | ✅ Built — `aviatrix.conf` with all custom patterns |
| README | Purpose, configuration, dependencies, support contact, release notes | ✅ Built — comprehensive |
| Logo | Optional but recommended | ⚠️ Need Aviatrix logo file |
| License | Noted in README | ✅ MIT (matches SIEM connector) |
| No sensitive data | Samples and knowledge objects scrubbed | ✅ Using sanitized test samples |
| Version | Start at `0.1.0`, then `1.0.0` for production | ✅ Set to `0.1.0` |
| Min Cribl version | Specified in `pack.yml` | ✅ Set to `4.0` |

### Publication Process

1. Create account on [packs.cribl.io](https://packs.cribl.io) (uses Cribl.Cloud credentials)
2. Acknowledge the Pack Developer Agreement (PDA)
3. Click **Publish Pack → Upload Pack**
4. Upload the `.crbl` file (tar.gz archive of the pack directory)
5. Dispensary auto-validates configuration structure and required fields
6. Pack enters **Validating** state for human review by Cribl team
7. Email from `packs@cribl.io` — accepted or rejected with rationale
8. Once accepted, pack appears in the Dispensary for all Cribl Stream customers

---

## Customer Journey (End to End)

### Step 1: Discover
Customer opens **Cribl Stream → Processing → Packs → Add Pack → Add from Dispensary**. They search "Aviatrix" or filter by "Security" / "Firewall" / "Network" use case.

### Step 2: Install
Click the Aviatrix tile → read the README → click **Add Pack**. The pipeline, routes, grok patterns, and sample data are imported into their Worker Group. No CLI, no Terraform, no Docker.

### Step 3: Configure Syslog Source
Create a Syslog Source in Cribl Stream on UDP/TCP port 5000 (or reuse an existing syslog source and enable the pack's route).

### Step 4: Point Aviatrix at Cribl
In Aviatrix Controller → Settings → Logging → Remote Syslog, set the server to the Cribl worker IP on port 5000. **Identical configuration** to the current Logstash SIEM Connector — no changes needed on the Aviatrix side.

### Step 5: Configure SIEM Destination
Set up their SIEM destination (Splunk HEC, Sentinel, Datadog, S3/Security Lake, etc.). Use `avx_log_profile` and `avx_sourcetype` fields for routing:

```
# Route all logs to Splunk
Filter: avx_sourcetype != undefined → splunk-hec

# Split: security → Splunk, networking → Datadog
Filter: avx_log_profile === 'security'    → splunk-hec
Filter: avx_log_profile === 'networking'  → datadog
```

### Step 6: Verify
Use Cribl's **Live Data** capture or **Preview** with the included sample data to confirm parsing. All 8 log types should produce structured events with no `_grokparsefailure` tags.

### Step 7: Ongoing
New pack versions appear as upgrade notifications in the Cribl UI. One-click upgrade.

---

## Advantages Over Current Logstash Connector

| Dimension | Logstash SIEM Connector | Cribl Pack |
|-----------|------------------------|------------|
| Infrastructure | Dedicated EC2 instances, NLB, S3 bucket | Runs inside existing Cribl workers |
| Deployment | Terraform + Docker + config assembly script | One-click install from Dispensary |
| Destinations | 4 (Splunk, Sentinel, Dynatrace, Zabbix) | 40+ native Cribl destinations |
| Multi-destination | Requires separate Logstash instances | Native fan-out in Cribl routes |
| Testing/debugging | Blind Grok debugging, webhook viewer | Interactive Preview UI with diff |
| Volume management | None | Cribl sampling, aggregation, quota functions |
| Upgrades | Redeploy infrastructure | One-click in UI |
| Maintenance | Aviatrix-managed Logstash configs + infra Terraform | Pack updates only |
| Customer reach | Customers must find GitHub repo | Built into Cribl UI marketplace |

---

## Go-to-Market Recommendations

### 1. Cribl Partnership Outreach
Contact Cribl's Technology Alliances / Partnerships team to discuss a vendor-branded pack (`cribl-aviatrix-siem`). This gets the "Built by Cribl" badge, higher Dispensary visibility, and potential co-marketing. Reference existing vendor packs (Palo Alto, CrowdStrike, Corelight) as precedent.

### 2. Source Code Management
Maintain the pack source in a dedicated GitHub repo (e.g., `AviatrixSystems/aviatrix-cribl-pack`) or as a directory within the existing `aviatrix-siem-connector` repo. Use GitHub Actions to auto-build the `.crbl` file on tagged releases. Cribl has documented CI/CD workflows for pack deployment via GitHub Actions.

### 3. Pre-Submission Checklist

- [ ] Add `devnull` catch-all route (required by Dispensary standards)
- [ ] Add Aviatrix logo to pack
- [ ] Test all 8 log types against a live Cribl Stream instance using Preview
- [ ] Validate cpu_cores protobuf parser against all 4 format variants in sample data
- [ ] Validate optional-field Grok patterns (gw_net_stats has many optional groups that may behave differently in Cribl vs. Logstash)
- [ ] Add function descriptions to every function (Dispensary standard)
- [ ] Add Release Notes section to README
- [ ] Add support contact info to README
- [ ] Confirm Splunk sourcetype mapping produces backward-compatible field names for existing dashboards
- [ ] Engage Cribl `#packs` Slack channel for community feedback before submitting

### 4. Co-Marketing Opportunities
- Joint blog post with Cribl: "Aviatrix Cloud Network Security Logs in Cribl Stream"
- Demo at Cribl's community events or webinars
- Reference in Aviatrix SIEM Connector README as the recommended path for Cribl customers
- Include in Aviatrix SE training materials alongside the existing Splunk/Sentinel/Dynatrace deployment guides

### 5. Federal Consideration
Cribl has a separate **Federal Packs Dispensary** for government customers that only shows Cribl-authored packs. If Aviatrix has FedRAMP or government customers using Cribl, the vendor partnership path is the only way to get into the Federal Dispensary.

---

## Pack File Inventory

The prototype pack (`.crbl` file) contains:

| File | Lines | Purpose |
|------|-------|---------|
| `pack.yml` | 19 | Pack metadata (id, version, description, author, tags) |
| `pipelines/avx-parse/conf.yml` | 681 | Main parsing pipeline — 5 stages, all 8 log types |
| `knowledge/grok/aviatrix.conf` | 31 | Custom Aviatrix Grok patterns |
| `routes.yml` | 10 | Route matching Aviatrix syslog patterns |
| `samples/aviatrix-syslog.log` | 44 | Sample events for all log types |
| `README.md` | 259 | Customer-facing documentation |

---

## Next Steps

1. **Validate the prototype** — Load `.crbl` in a Cribl Stream instance, run sample data through Preview, fix any Grok/JS issues
2. **Contact Cribl partnerships** — Explore vendor pack path vs. community submission
3. **Complete pre-submission checklist** — Add devnull route, logo, polish descriptions
4. **Publish to Dispensary** — Upload `.crbl`, await review
5. **Update SIEM Connector README** — Add Cribl as a supported destination with link to Dispensary pack
