# Aviatrix Cloud Network Security

## About this Pack

This Pack parses, normalizes, and routes Aviatrix Cloud Network syslog data through Cribl Stream for delivery to any SIEM or observability destination. It runs natively inside your existing Cribl workers with no additional infrastructure required.

The Pack provides the following benefits:

- Classifies incoming Aviatrix syslog by log type automatically
- Parses structured fields using Grok patterns and JSON extraction
- Normalizes timestamps and converts field types
- Tags each event with sourcetype, source, host, and log profile for downstream routing
- Supports 9 Aviatrix log types across security and networking
- Produces Splunk-compatible sourcetypes for backward compatibility with existing dashboards

Supported log types:

- **L4 Microsegmentation** — eBPF-enforced network policy (allow/deny) with session tracking
- **L7/TLS Inspection** — Deep packet inspection via TLS proxy
- **Suricata IDS/IPS** — Intrusion detection/prevention alerts
- **FQDN Firewall** — DNS-based firewall rule hits
- **Controller API Audit** — API calls and admin actions (V1 and V2.5 formats)
- **VPN Session** — VPN user connect/disconnect with session metrics
- **Gateway Network Stats** — Interface throughput, packet rates, conntrack
- **Gateway System Stats** — CPU, memory, disk utilization with per-core detail
- **Tunnel Status** — Tunnel up/down state changes with cloud/region context

Every event is tagged with a log profile (`security` or `networking`) to support selective forwarding — for example, security logs to Splunk and networking logs to Datadog.

## Deployment

### Configure a Syslog Source

Create a Syslog source in Cribl Stream listening on your preferred port for UDP and/or TCP.

### Enable the Pack Route

The Pack includes a route that matches Aviatrix syslog patterns. Ensure it is enabled and positioned before any catch-all routes in your Worker Group.

### Configure Aviatrix

In Aviatrix CoPilot, navigate to Settings > Logging > Remote Syslog and point it to your Cribl Stream worker address and the port configured above.

### Configure your Destination / Update Pack Routes

To ensure proper data routing, you must make a choice: retain the current setting to use the Default Destination defined by your Worker Group, or define a new Destination directly inside this Pack and adjust the Pack's route accordingly.

### Commit and Deploy

Once everything is configured, perform a Commit & Deploy to enable data collection.

## Splunk Integration

When routing to a Splunk HEC destination, map the following output fields:

- `avx_sourcetype` → Splunk `sourcetype` (e.g., `aviatrix:firewall:l4`)
- `avx_source` → Splunk `source` (e.g., `avx-l4-fw`)
- `avx_host` → Splunk `host`

## Testing

The Pack includes 51 sample events covering all 9 log types. Use Cribl's Preview feature to verify parsing:

1. Open the `avx-parse` pipeline
2. In the Preview pane, select the `aviatrix-syslog` sample
3. Click Run to process all events
4. Verify all 9 log types parse with correct `avx_sourcetype` values

## Compatibility

- Cribl Stream 4.0+
- Aviatrix Controller 7.x and 8.x
- Legacy 7.x and 8.2+ session format support

## Upgrades

Upgrading certain Cribl Packs using the same Pack ID can have unintended consequences. See [Upgrading an Existing Pack](https://docs.cribl.io/stream/packs-upgrading) for details.

## Release Notes

### Version 0.2.2
- Embed logo as base64 for Dispensary compatibility

### Version 0.2.1
- Add PRI header support to Grok patterns for syslog source compatibility
- Update sample data with PRI headers for proper event breaking

### Version 0.2.0
- Add VPN Session log type with connect/disconnect parsing
- 51 sample events covering all 9 log types

### Version 0.1.0
- Initial release
- 8 log types with single pipeline and 5 processing stages
- Splunk-compatible sourcetype mapping

## Contributing

To contribute to the Pack, please connect with us on [Cribl Community Slack](https://cribl.io/community). You can suggest new features or offer to collaborate.

## Support

For issues with this Pack:
- GitHub Issues: [cc-aviatrix-siem](https://github.com/AviatrixSystems/cc-aviatrix-siem/issues)
- Email: support@aviatrix.com

## License

This Pack uses the following license: MIT.
