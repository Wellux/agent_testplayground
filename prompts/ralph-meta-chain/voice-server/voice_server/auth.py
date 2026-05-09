"""Tailscale-aware origin guard.

We check the request's remote-address against a list of trusted CIDR subnets.
Default list is `100.64.0.0/10` (Tailscale CGNAT range) plus loopback.
This is intentionally simple — Tailscale ACLs are the real enforcer. The
guard exists to refuse traffic from random LAN/WAN sources if the user
accidentally exposes the port.
"""
from __future__ import annotations

import ipaddress
import logging
from typing import Iterable

from fastapi import HTTPException, Request

from .config import trusted_subnets

log = logging.getLogger(__name__)


def _parse_subnets(spec: Iterable[str]) -> list[ipaddress._BaseNetwork]:
    nets: list[ipaddress._BaseNetwork] = []
    for s in spec:
        try:
            nets.append(ipaddress.ip_network(s, strict=False))
        except ValueError:
            log.warning("ignoring bad subnet spec %r", s)
    return nets


def origin_guard(request: Request) -> None:
    client = request.client
    if client is None:
        raise HTTPException(status_code=403, detail="no client info")
    try:
        addr = ipaddress.ip_address(client.host)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=f"bad remote address: {e!s}") from e
    nets = _parse_subnets(trusted_subnets())
    if not any(addr in n for n in nets):
        log.warning("rejected origin %s (not in trusted subnets)", addr)
        raise HTTPException(status_code=403, detail="origin not in trusted subnets")
