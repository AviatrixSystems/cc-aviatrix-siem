# Splunk Integration

When routing to a Splunk HEC destination, map the following output fields:

- `avx_sourcetype` → Splunk `sourcetype` (e.g., `aviatrix:firewall:l4`)
- `avx_source` → Splunk `source` (e.g., `avx-l4-fw`)
- `avx_host` → Splunk `host`
