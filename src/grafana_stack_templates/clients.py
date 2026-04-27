"""HTTP clients for Grafana Cloud APIs.

Two distinct APIs:
  - Grafana stack API (alert rules, contact points, templates, policies)
  - Synthetic Monitoring API (separate host, separate token)

Both wrap `requests.Session` with retries and consistent error handling.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


class APIError(RuntimeError):
    def __init__(self, status: int, body: str, url: str):
        self.status = status
        self.body = body
        self.url = url
        super().__init__(f"HTTP {status} on {url}: {body[:300]}")


@dataclass
class Env:
    """Runtime credentials and endpoint URLs."""

    grafana_url: str          # e.g. https://yourstack.grafana.net
    grafana_token: str        # service-account token (glsa_...)
    sm_url: str               # e.g. https://synthetic-monitoring-api-...grafana.net
    sm_token: str             # SM access token
    slack_webhook: str | None = None
    dry_run: bool = False

    @property
    def grafana_api(self) -> str:
        return f"{self.grafana_url.rstrip('/')}/api"


class GrafanaClient:
    """Client for the Grafana stack API (alert rules, contact points, templates)."""

    def __init__(self, env: Env):
        self.env = env
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {env.grafana_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "grafana-stack-templates",
            "X-Disable-Provenance": "true",
        })

    def _url(self, path: str) -> str:
        return f"{self.env.grafana_api}{path}"

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = self._url(path)
        if self.env.dry_run:
            return {"_dry_run": True, "method": method, "url": url, "body": kwargs.get("json")}
        r = self.session.request(method, url, timeout=30, **kwargs)
        if not r.ok:
            raise APIError(r.status_code, r.text, url)
        if r.headers.get("Content-Type", "").startswith("application/json"):
            return r.json() if r.text else None
        return r.text

    def list_alert_rules(self) -> list[dict[str, Any]]:
        if self.env.dry_run:
            return []
        return self._request("GET", "/v1/provisioning/alert-rules") or []

    def get_alert_rule(self, uid: str) -> dict[str, Any] | None:
        try:
            return self._request("GET", f"/v1/provisioning/alert-rules/{uid}")
        except APIError as e:
            if e.status == 404:
                return None
            raise

    def create_alert_rule(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/v1/provisioning/alert-rules", json=payload)

    def update_alert_rule(self, uid: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("PUT", f"/v1/provisioning/alert-rules/{uid}", json=payload)

    def list_contact_points(self) -> list[dict[str, Any]]:
        if self.env.dry_run:
            return []
        return self._request("GET", "/v1/provisioning/contact-points") or []

    def upsert_contact_point(self, payload: dict[str, Any]) -> dict[str, Any]:
        existing = [cp for cp in self.list_contact_points() if cp.get("name") == payload["name"]]
        if existing:
            uid = existing[0]["uid"]
            return self._request("PUT", f"/v1/provisioning/contact-points/{uid}", json=payload)
        return self._request("POST", "/v1/provisioning/contact-points", json=payload)

    def list_templates(self) -> list[dict[str, Any]]:
        return self._request("GET", "/v1/provisioning/templates") or []

    def upsert_template(self, name: str, body: str) -> Any:
        return self._request(
            "PUT",
            f"/v1/provisioning/templates/{name}",
            json={"name": name, "template": body},
        )

    def list_folders(self) -> list[dict[str, Any]]:
        if self.env.dry_run:
            return []
        return self._request("GET", "/folders") or []

    def upsert_folder(self, uid: str, title: str) -> dict[str, Any]:
        if self.env.dry_run:
            return {"_dry_run": True, "uid": uid, "title": title}
        for f in self.list_folders():
            if f.get("uid") == uid:
                return f
        return self._request(
            "POST",
            "/folders",
            json={"uid": uid, "title": title},
        )


class SMClient:
    """Client for the Synthetic Monitoring API (separate host + token)."""

    def __init__(self, env: Env):
        self.env = env
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {env.sm_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "grafana-stack-templates",
        })

    def _url(self, path: str) -> str:
        return f"{self.env.sm_url.rstrip('/')}{path}"

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = self._url(path)
        if self.env.dry_run:
            return {"_dry_run": True, "method": method, "url": url, "body": kwargs.get("json")}
        r = self.session.request(method, url, timeout=30, **kwargs)
        if not r.ok:
            raise APIError(r.status_code, r.text, url)
        return r.json() if r.text else None

    def list_checks(self) -> list[dict[str, Any]]:
        if self.env.dry_run:
            return []
        return self._request("GET", "/api/v1/check/list") or []

    def create_check(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/api/v1/check/add", json=payload)

    def update_check(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/api/v1/check/update", json=payload)

    def find_by_target_and_job(self, target: str, job: str) -> dict[str, Any] | None:
        for c in self.list_checks():
            if c.get("target") == target and c.get("job") == job:
                return c
        return None
