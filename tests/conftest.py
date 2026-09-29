"""Routine tests cannot accidentally contact a live service."""

import socket

import pytest


@pytest.fixture(autouse=True)
def forbid_live_network(monkeypatch):
    def blocked(*args, **kwargs):
        raise AssertionError("Routine tests are offline; use the explicit provider-smoke command")
    monkeypatch.setattr(socket.socket, "connect", blocked)
    monkeypatch.setattr(socket.socket, "connect_ex", blocked)
    monkeypatch.setattr(socket, "create_connection", blocked)
