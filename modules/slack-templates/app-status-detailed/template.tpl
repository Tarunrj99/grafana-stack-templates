{{/*
  app_status_slack — Detailed (incident-review)

  Block-kit, includes the alert description and the full label set.
  Designed for channels where every alert is going to be investigated.

  Required labels:      team, service, severity, alertgroup
  Required annotations: runbook_url, dashboard_url, description
*/}}

{{ define "app_status.title" -}}
{{ if eq .Status "firing" }}:rotating_light: {{ len .Alerts.Firing }} service{{ if gt (len .Alerts.Firing) 1 }}s{{ end }} DOWN — incident-review{{ else }}:white_check_mark: {{ len .Alerts.Resolved }} service{{ if gt (len .Alerts.Resolved) 1 }}s{{ end }} recovered — incident-review{{ end }}
{{- end }}

{{ define "app_status.text" -}}
{{ range .Alerts -}}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{{ if eq .Status "firing" }}:red_circle:{{ else }}:large_green_circle:{{ end }} *{{ index .Labels "service" }}* · {{ index .Labels "severity" }} · team:{{ index .Labels "team" }} · alertgroup:{{ index .Labels "alertgroup" }}
*Endpoint:* {{ index .Annotations "runbook_url" }}
*Started:*  {{ .StartsAt.Format "02 Jan 2006 15:04 UTC" }} · <!date^{{ .StartsAt.Unix }}^(Today {time} your local)|local time>
{{- if eq .Status "resolved" }}
*Resolved:* {{ .EndsAt.Format "02 Jan 2006 15:04 UTC" }} · <!date^{{ .EndsAt.Unix }}^(Today {time} your local)|local time>
{{- end }}
*Description:* {{ index .Annotations "description" }}

*Labels:*
{{ range $k, $v := .Labels }}  • `{{ $k }}={{ $v }}`
{{ end -}}
:link: <{{ index .Annotations "runbook_url" }}|Open> · :bar_chart: <{{ index .Annotations "dashboard_url" }}|Dashboard>{{ if index .Annotations "runbook_url" }} · :ledger: <{{ index .Annotations "runbook_url" }}|Runbook>{{ end }}

{{ end -}}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{{- end }}
