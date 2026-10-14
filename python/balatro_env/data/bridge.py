"""Raw-dict HTTP access to one bridge instance (no pydantic: tools compare exact JSON)."""

from __future__ import annotations

import time
from typing import Any

import requests


class BridgeError(RuntimeError):
    pass


class Bridge:
    def __init__(self, port: int, host: str = "127.0.0.1", timeout: float = 10.0):
        self.port = port
        self.base = f"http://{host}:{port}"
        self.timeout = timeout
        self.session = requests.Session()

    def _get(self, endpoint: str, retries: int = 3) -> dict[str, Any]:
        last: Exception | None = None
        for attempt in range(retries):
            try:
                r = self.session.get(f"{self.base}/{endpoint}", timeout=self.timeout)
                return r.json()
            except (requests.ConnectionError, requests.Timeout, ValueError) as exc:
                last = exc
                time.sleep(0.5 * (attempt + 1))
        raise BridgeError(f"GET /{endpoint} on port {self.port} failed: {last}")

    def _post(self, endpoint: str, body: dict[str, Any]) -> dict[str, Any]:
        # Never retried: a timed-out POST may already have executed.
        try:
            r = self.session.post(f"{self.base}/{endpoint}", json=body, timeout=self.timeout)
        except (requests.ConnectionError, requests.Timeout) as exc:
            raise BridgeError(f"POST /{endpoint} on port {self.port} failed: {exc}") from exc
        try:
            return r.json()
        except ValueError as exc:
            raise BridgeError(f"POST /{endpoint}: HTTP {r.status_code} non-JSON body {r.text[:200]!r}") from exc

    def health(self) -> dict[str, Any]:
        return self._get("health")

    def alive(self) -> bool:
        try:
            return self._get("health", retries=1).get("status") == "ok"
        except BridgeError:
            return False

    def state(self) -> dict[str, Any]:
        return self._get("state")

    def legal(self) -> dict[str, Any]:
        return self._get("legal")

    def action(self, atype: str, params: dict[str, Any] | None = None,
               meta: dict[str, Any] | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {"type": atype, "params": params or {}}
        if meta:
            body["meta"] = meta
        return self._post("action", body)

    def wait_settled(self, timeout: float = 60.0, poll: float = 0.1) -> tuple[dict[str, Any], dict[str, Any]]:
        """Poll until /legal reports settled; returns (state, legal) taken at the settled point.

        The pair is re-read until both agree on settled + phase, so obs and legal describe one decision.
        """
        deadline = time.monotonic() + timeout
        while True:
            legal = self.legal()
            if legal.get("settled"):
                state = self.state()
                legal2 = self.legal()
                if state.get("settled") and legal2.get("settled") and state.get("phase") == legal2.get("phase"):
                    return state, legal2
            if time.monotonic() > deadline:
                raise BridgeError(
                    f"port {self.port}: not settled after {timeout}s (phase={legal.get('phase')!r})"
                )
            time.sleep(poll)

    def act_settled(self, atype: str, params: dict[str, Any] | None = None,
                    meta: dict[str, Any] | None = None, timeout: float = 30.0) -> dict[str, Any]:
        """POST an action, re-posting only while the bridge answers retry:true (not yet settled)."""
        deadline = time.monotonic() + timeout
        while True:
            res = self.action(atype, params, meta)
            if res.get("ok") or not res.get("retry") or time.monotonic() > deadline:
                return res
            time.sleep(0.2)
