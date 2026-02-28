# Sync Strategy: log-integration-engine → Cribl Pack

## Overview

The Aviatrix SIEM Connector (log-integration-engine) is the source of truth for log parsing logic. The Cribl pack is a derivative. This document describes how to keep them in sync.

## Architecture Mapping

```
log-integration-engine              →  aviatrix-cribl-pack
─────────────────────                  ──────────────────────
logstash-configs/                      pipelines/avx-parse/conf.yml
├── filters/10-microseg.conf          │  Stage 2a: L4 Microseg functions
├── filters/11-l7-dcf.conf           │  Stage 2b: L7/MITM functions
├── filters/12-suricata.conf         │  Stage 2c: Suricata functions
├── filters/13-fqdn.conf             │  Stage 2d: FQDN functions
├── filters/14-cmd.conf              │  Stage 2e: CMD functions
├── filters/15-gateway-stats.conf    │  Stage 3a + 3b: Net + Sys Stats
├── filters/16-tunnel-status.conf    │  Stage 3c: Tunnel Status
├── filters/17-cpu-cores-parse.conf  │  Stage 3b: cpu_cores Code function
├── filters/90-timestamp.conf        │  Stage 4: Timestamp normalization
├── filters/95-field-conversion.conf │  Stage 4: Type conversion Evals
├── patterns/avx.conf                │  knowledge/grok/aviatrix.conf
└── test-tools/sample-logs/          │  samples/aviatrix-syslog.log
    test-samples.log
```

## Sync Approaches

### Approach 1: Manual Diff Review

When log-integration-engine is updated:

1. Check recent changes:
   ```bash
   cd /Users/christophermchenry/Documents/Scripting/log-integration-engine
   git log --oneline --since="2 weeks ago" -- logstash-configs/
   ```

2. Review diffs for each changed filter:
   ```bash
   git diff v0.1-alpha..HEAD -- logstash-configs/filters/
   git diff v0.1-alpha..HEAD -- logstash-configs/patterns/
   ```

3. Manually translate Logstash changes to Cribl pipeline functions

### Approach 2: AI-Assisted Sync (Recommended)

Use Claude Code to automate the translation:

1. **Trigger:** New tag on log-integration-engine (e.g., `v0.2.0`)
2. **Diff generation:** `git diff v0.1-alpha..v0.2.0 -- logstash-configs/`
3. **Claude prompt:**
   ```
   Given this Logstash filter diff from the Aviatrix SIEM Connector,
   update the corresponding Cribl pipeline functions in
   pipelines/avx-parse/conf.yml. Maintain the same stage grouping
   and field naming conventions.
   ```
4. **Review:** Human reviews Claude's changes
5. **Test:** Run samples through Cribl Preview
6. **Release:** Tag and build .crbl

### Approach 3: GitHub Actions Automation (Future)

```yaml
# .github/workflows/sync-from-upstream.yml
on:
  workflow_dispatch:
    inputs:
      upstream_tag:
        description: 'log-integration-engine tag to sync from'
        required: true

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Clone upstream
        run: git clone https://github.com/AviatrixSystems/aviatrix-siem-connector upstream
      - name: Generate diff
        run: |
          cd upstream
          git diff ${{ inputs.upstream_tag }}..HEAD -- logstash-configs/ > ../upstream-diff.patch
      - name: AI-assisted translation
        # Use Claude API to translate Logstash diff to Cribl changes
        # This step would call Claude with the diff + current conf.yml
      - name: Create PR
        # Create a PR with the translated changes for review
```

## Translation Patterns: Logstash → Cribl

### Grok filter → Grok function
```ruby
# Logstash
grok {
  match => { "message" => "pattern %{FIELD:name}" }
  tag_on_failure => []
}
```
```yaml
# Cribl
- id: grok
  filter: "__avx_type === 'type'"
  conf:
    pattern: "pattern %{FIELD:name}"
    srcField: _raw
```

### Mutate convert → Eval function
```ruby
# Logstash
mutate { convert => { "field" => "integer" } }
```
```yaml
# Cribl
- id: eval
  conf:
    add:
      - name: field
        value: "Number(field) || 0"
```

### Ruby filter → Code function
```ruby
# Logstash
ruby { code => "event.set('field', value)" }
```
```yaml
# Cribl
- id: code
  conf:
    code: |
      __e.field = value;
```

### Conditional → Filter expression
```ruby
# Logstash
if "tag" in [tags] { ... }
```
```yaml
# Cribl
filter: "__avx_type === 'tag'"
```

### Add tag → Set __avx_type
```ruby
# Logstash
mutate { add_tag => ["microseg"] }
```
```yaml
# Cribl (done in Stage 1 Classify)
__avx_type = 'microseg'
```

## Release Coordination

Both repos should use compatible tags:

| log-integration-engine | aviatrix-cribl-pack | Notes |
|----------------------|--------------------|----|
| `v0.1-alpha` | `v0.1.0` | Initial port |
| `v0.2.0` | `v0.2.0` | Aligned versions going forward |

When log-integration-engine cuts a new tag, the Cribl pack should be updated and tagged within the same release cycle.
