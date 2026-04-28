{{/*
  app_status_slack — Variant A (default)

  Block-kit-friendly Slack template for application status alerts produced
  by the alert-rules/sm-http-healthcheck module (and any other rule that
  follows the same label set).

  Required labels:      service, severity
  Required annotations: runbook_url, dashboard_url
  Notes:
    - "Today X:YZ PM your local" portion is rendered by Slack's native
      <!date^TIMESTAMP^...> token so every viewer sees their own timezone.
    - We deliberately omit `team` and the Silence link to keep the message
      tight in mobile-width channels.
*/}}

{{ define "app_status.title" -}}
{{ if eq .Status "firing" }}:rotating_light: {{ len .Alerts.Firing }} service{{ if gt (len .Alerts.Firing) 1 }}s{{ end }} DOWN{{ else }}:white_check_mark: {{ len .Alerts.Resolved }} service{{ if gt (len .Alerts.Resolved) 1 }}s{{ end }} recovered{{ end }}
{{- end }}

{{ define "app_status.text" -}}
{{ range .Alerts -}}
{{ if eq .Status "firing" }}:red_circle:{{ else }}:large_green_circle:{{ end }} *{{ index .Labels "service" }}* · {{ index .Labels "severity" }}
{{ index .Annotations "runbook_url" }}
*Started:* {{ .StartsAt.Format "02 Jan 2006 15:04 UTC" }} · <!date^{{ .StartsAt.Unix }}^Today {time} your local|local time>
{{- if eq .Status "resolved" }}
*Resolved:* {{ .EndsAt.Format "02 Jan 2006 15:04 UTC" }} · <!date^{{ .EndsAt.Unix }}^Today {time} your local|local time>
{{- end }}
:link: <{{ index .Annotations "runbook_url" }}|Open> · :bar_chart: <{{ index .Annotations "dashboard_url" }}|Dashboard>

{{ end -}}
{{- end }}
