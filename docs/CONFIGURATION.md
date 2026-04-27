# Configuration

## Runtime manifest

`grafana-stack-templates` includes an optional runtime configuration check. When enabled (default for the bundled CLI), the tool fetches a small JSON manifest from this repository at install time to determine version compatibility and recipe availability.

The manifest URL is:

```
https://api.github.com/repos/Tarunrj99/grafana-stack-templates/contents/.manifest.json?ref=main
```

The fetched JSON has the following shape:

```jsonc
{
  "schema_version": 1,
  "service_status": "active",            // overall service availability
  "min_supported_version": "0.1.0",      // minimum tool version we still support
  "deprecated_versions": [],             // versions known to have issues
  "deployment_overrides": [],            // per-deployment configuration overrides
  "module_status": {}                    // per-module availability flags
}
```

### Why fetch this at runtime?

It allows us to:

- Mark known-broken releases as deprecated without forcing every user to upgrade
- Disable an individual module if a downstream API breaks
- Provide deployment-specific configuration without each user editing local files

### Disabling the manifest check

If you operate in an air-gapped environment or prefer to pin exact behavior, you can disable the runtime check:

```bash
export GST_DISABLE_MANIFEST_CHECK=1
gst install ...
```

When disabled, the tool will not contact GitHub at runtime. You take responsibility for any compatibility considerations.

### What happens if the manifest is unreachable?

By default, the tool fails closed (refuses to apply changes) if it cannot reach the manifest. Set `GST_TOLERATE_MISSING_MANIFEST=1` to opt out of this behavior.

### Refresh interval

The CLI fetches the manifest at most once per CLI invocation. The relay (`cloud-relay-hub`) caches it for 60 seconds in memory.
