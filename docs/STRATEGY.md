# Aviatrix Cribl Stream Pack — Strategy & Publishing Plan

## Executive Summary

Cribl Stream customers can replace the standalone Aviatrix SIEM Connector (Logstash-based) with a native **Cribl Pack** that runs inside their existing Cribl infrastructure. This eliminates the need for customers to deploy and manage separate EC2 instances, NLBs, and Logstash containers. The Pack can be published to Cribl's built-in marketplace — the **Packs Dispensary** — where customers discover, install, and upgrade it with one click directly from the Cribl Stream UI.

## Publishing Path

### Phase 1: Community Pack (Week 1-2)
- Pack ID: `cc-aviatrix-siem`
- Author: `Chris - cc`
- Anyone can publish; author-supported
- Immediate visibility in Dispensary

### Phase 2: Vendor Partnership (Future)
- Pack ID: `cribl-aviatrix-siem`
- Author: `Aviatrix` or `Cribl Packs Team`
- Requires Cribl Technology Alliances partnership
- Gets "Built by Cribl" badge, higher Dispensary visibility
- Eligible for Federal Packs Dispensary
- Reference: Palo Alto, CrowdStrike, Corelight vendor packs

## Cribl Packs Dispensary

### What It Is
The **Packs Dispensary** ([packs.cribl.io](https://packs.cribl.io)) is Cribl's built-in marketplace for shareable configuration packages. Accessible from **Processing → Packs → Add Pack → Add from Dispensary** in the Cribl Stream UI.

### Publication Process
1. Create account on [packs.cribl.io](https://packs.cribl.io) (uses Cribl.Cloud credentials)
2. Acknowledge the Pack Developer Agreement (PDA)
3. Click **Publish Pack → Upload Pack**
4. Upload the `.crbl` file (tar.gz archive of the pack directory)
5. Dispensary auto-validates configuration structure and required fields
6. Pack enters **Validating** state for human review by Cribl team
7. Email from `packs@cribl.io` — accepted or rejected with rationale
8. Once accepted, pack appears in the Dispensary

### Customer Upgrade Experience
When a new version is published, customers see an upgrade indicator on their Packs page and can update with one click. Local modifications are preserved with side-by-side reconciliation.

## Advantages Over Logstash SIEM Connector

| Dimension | Logstash SIEM Connector | Cribl Pack |
|-----------|------------------------|------------|
| Infrastructure | Dedicated EC2 instances, NLB, S3 bucket | Runs inside existing Cribl workers |
| Deployment | Terraform + Docker + config assembly script | One-click install from Dispensary |
| Destinations | 4 (Splunk, Sentinel, Dynatrace, Zabbix) | 40+ native Cribl destinations |
| Multi-destination | Requires separate Logstash instances | Native fan-out in Cribl routes |
| Testing/debugging | Blind Grok debugging, webhook viewer | Interactive Preview UI with diff |
| Volume management | None | Cribl sampling, aggregation, quota functions |
| Upgrades | Redeploy infrastructure | One-click in UI |
| Customer reach | Must find GitHub repo | Built into Cribl UI marketplace |

## Customer Journey

1. **Discover** — Search "Aviatrix" in Cribl Dispensary
2. **Install** — One-click import of pipeline, routes, grok patterns, samples
3. **Configure syslog** — Create Syslog Source on UDP/TCP 5000
4. **Point Aviatrix** — Controller → Settings → Logging → Remote Syslog → Cribl worker IP:5000
5. **Set up destinations** — Route by `avx_log_profile` and `avx_sourcetype`
6. **Verify** — Use Cribl Preview with included sample data
7. **Ongoing** — One-click upgrades from Dispensary

## Go-to-Market Recommendations

1. **Cribl Partnership Outreach** — Contact Cribl Technology Alliances for vendor pack path
2. **Source Code on GitHub** — `AviatrixSystems/aviatrix-cribl-pack` with GitHub Actions CI/CD
3. **Joint content** — Blog post, webinar, demo with Cribl
4. **Cross-reference** — Link from SIEM Connector README to Dispensary pack
5. **SE training** — Include in Aviatrix SE materials alongside Splunk/Sentinel guides
6. **Federal** — Vendor partnership required for Federal Dispensary (FedRAMP customers)
