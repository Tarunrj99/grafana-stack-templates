{{ define "app_status.title" -}}
{{ if eq .Status "firing" }}:rotating_light: CRITICAL — {{ len .Alerts.Firing }} service(s) DOWN{{ else }}:large_green_circle: RESOLVED — {{ len .Alerts.Resolved }} service(s) UP{{ end }}
{{- end }}

{{ define "app_status.text" -}}
{{ if eq .Status "firing" }}*:red_circle: {{ len .Alerts.Firing }} alert(s) firing*{{ else }}*:large_green_circle: {{ len .Alerts.Resolved }} alert(s) resolved*{{ end }}
Group: `{{ .GroupKey }}`

{{ range .Alerts -}}
─────────────────────────────
{{ if eq .Status "firing" }}:red_circle:{{ else }}:large_green_circle:{{ end }} *Service:* `{{ index .Labels "service" }}`   *Severity:* `{{ index .Labels "severity" }}`   *Team:* `{{ index .Labels "team" }}`
*Endpoint:* `{{ index .Annotations "runbook_url" }}`
*Started:* {{ .StartsAt.Format "2006-01-02 15:04:05 MST" }}{{ if eq .Status "resolved" }}
*Resolved:* {{ .EndsAt.Format "2006-01-02 15:04:05 MST" }}{{ end }}
{{ index .Annotations "description" }}

<{{ index .Annotations "runbook_url" }}|:wrench: *Runbook*>  ·  <{{ index .Annotations "dashboard_url" }}|:bar_chart: *Dashboard*>  ·  <{{ .SilenceURL }}|:no_bell: *Silence*>
{{ end }}
─────────────────────────────
_Grafana Cloud SM · alertgroup=appstatus_
{{- end }}
