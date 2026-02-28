# Cribl Packs Dispensary — Submission Requirements

## Required Pack Contents

| Component | Requirement | Status |
|-----------|-------------|--------|
| Pipeline(s) | At least one, with Comment functions and descriptions | ✅ |
| Sample data | At least one sample per pipeline | ✅ |
| Routes | Generic filters using `_raw.match()`, not sourcetype | ✅ |
| Catch-all route | Final route with `filter: true` to `devnull` | ⚠️ TODO |
| Knowledge objects | All Grok patterns self-contained in pack | ✅ |
| README | Purpose, configuration, dependencies, support contact, release notes | ✅ |
| Logo | Optional but recommended | ⚠️ TODO |
| License | Noted in README | ✅ MIT |
| No sensitive data | Samples and knowledge objects scrubbed | ✅ |
| Version | Start at `0.1.0`, then `1.0.0` for production | ✅ |
| Min Cribl version | Specified in `pack.yml` | ✅ (`4.0`) |

## Pre-Submission Checklist

- [ ] Add `devnull` catch-all route (required by Dispensary standards)
- [ ] Add Aviatrix logo to pack root as `logo.png` or `logo.svg`
- [ ] Test all 8 log types against a live Cribl Stream instance using Preview
- [ ] Validate cpu_cores protobuf parser against all 4 format variants in sample data
- [ ] Validate optional-field Grok patterns (gw_net_stats has many optional groups)
- [ ] Add function descriptions to every pipeline function (Dispensary standard)
- [ ] Add Release Notes section to README
- [ ] Add support contact info to README
- [ ] Confirm Splunk sourcetype mapping is backward-compatible
- [ ] Engage Cribl `#packs` Slack channel for community feedback before submitting

## pack.yml Requirements

```yaml
id: cc-aviatrix-siem           # or cribl-aviatrix-siem for vendor
version: 0.1.0                 # semver
displayName: "Aviatrix Cloud Network Security"
description: >
  Parse, normalize, and route Aviatrix Cloud Network syslog data...
author: "Chris - cc"            # or "Aviatrix" for vendor
tags:
  - syslog
  - firewall
  - security
  - network
minCriblVersion: "4.0"
```

## Route Requirements

- Routes must use `_raw` regex matching (not field-based) for initial classification
- Must include a catch-all final route: `filter: true`, output: `devnull`
- Route filters should use `.test()` for regex matching in Cribl

## Pipeline Requirements

- Every function must have a `description` field
- Group functions into logical stages with `groupId`
- Include Comment functions at the start of each stage
- Use `id: comment` functions to explain stage purpose
- Internal working fields should use `__` prefix (Cribl convention)

## .crbl File Format

The `.crbl` file is a tar.gz archive containing the pack directory:

```bash
tar -czf cc-aviatrix-siem-0.1.0.crbl \
  pack.yml routes.yml README.md \
  pipelines/ knowledge/ samples/
```

Files that should NOT be in the .crbl:
- `CLAUDE.md` (internal development guidance)
- `docs/` (internal documentation)
- `previous-exploration/` (prototype reference)
- `.git/` (version control)
- `.github/` (CI/CD config)
- `LICENSE` (noted in README instead)
