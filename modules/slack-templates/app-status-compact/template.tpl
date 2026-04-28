{{/*
  app_status_slack — Compact (single-line)

  One line per affected service. Plain mrkdwn — no block-kit, no
  attachments, no per-message overhead. Best for channels that need a
  high signal-to-noise summary on mobile.

  Required labels:      service, severity
  Required annotations: runbook_url
*/}}

{{ define "app_status.title" -}}
{{ if eq .Status "firing" }}:rotating_light: {{ len .Alerts.Firing }} DOWN{{ else }}:white_check_mark: {{ len .Alerts.Resolved }} UP{{ end }}
{{- end }}

{{ define "app_status.text" -}}
{{ range .Alerts -}}
{{ if eq .Status "firing" -}}
:red_circle: *{{ index .Labels "service" }}* DOWN since {{ .StartsAt.Format "15:04 UTC" }} · {{ index .Annotations "runbook_url" }}
{{ else -}}
:large_green_circle: *{{ index .Labels "service" }}* UP after {{ .EndsAt.Format "15:04 UTC" }} (started {{ .StartsAt.Format "15:04" }}) · {{ index .Annotations "runbook_url" }}
{{ end -}}
{{ end -}}
{{- end }}
