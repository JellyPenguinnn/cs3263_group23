"""Native TLS verifies trust and hostnames without a live network or credential."""

from concurrent.futures import ThreadPoolExecutor
import socket
import ssl
import subprocess

import httpx
import pytest
import truststore

from scheduling.providers import RequestBudget, SoCLaaSProvider


def test_provider_uses_verified_native_context_without_environment_routing(monkeypatch):
    original_context = ssl.SSLContext
    real_client = httpx.Client
    captured = {}

    def client(**kwargs):
        captured.update(kwargs)
        return real_client(**kwargs)

    monkeypatch.setattr(httpx, "Client", client)
    monkeypatch.setenv("HTTPS_PROXY", "http://invalid.example:8080")
    monkeypatch.setenv("SSL_CERT_FILE", "/does-not-exist")
    with SoCLaaSProvider(api_key="test-only", budget=RequestBudget(1, 32)):
        context = captured["verify"]
        assert isinstance(context, truststore.SSLContext)
        assert context.verify_mode == ssl.CERT_REQUIRED
        assert context.check_hostname is True
        assert captured["trust_env"] is False
        assert captured["follow_redirects"] is False
        assert ssl.SSLContext is original_context


@pytest.fixture(scope="module")
def local_certificate(tmp_path_factory):
    directory = tmp_path_factory.mktemp("tls")
    cert, key = directory / "cert.pem", directory / "key.pem"
    config = directory / "openssl.cnf"
    config.write_text(
        "[req]\nprompt=no\ndistinguished_name=dn\nx509_extensions=ext\n"
        "[dn]\nCN=localhost\n[ext]\nsubjectAltName=DNS:localhost\n"
        "basicConstraints=critical,CA:TRUE\n"
        "keyUsage=critical,digitalSignature,keyEncipherment,keyCertSign\n"
        "extendedKeyUsage=serverAuth\n"
    )
    subprocess.run(
        ["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes",
         "-keyout", str(key), "-out", str(cert), "-days", "1",
         "-config", str(config)],
        check=True, capture_output=True,
    )
    return cert, key


@pytest.mark.parametrize("trusted,hostname,accepted", [
    (True, "localhost", True),
    (False, "localhost", False),
    (True, "wrong.example", False),
])
def test_native_handshake_fails_closed(local_certificate, trusted, hostname, accepted):
    cert, key = local_certificate
    server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    server_context.load_cert_chain(cert, key)
    client_context = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    if trusted:
        client_context.load_verify_locations(cafile=str(cert))
    # socketpair stays entirely within the process: no connect(), port or network.
    client_socket, server_socket = socket.socketpair()
    client_socket.settimeout(5)
    server_socket.settimeout(5)

    def serve():
        try:
            with server_context.wrap_socket(server_socket, server_side=True) as connection:
                return connection.recv(1)
        except (ssl.SSLError, ConnectionError):
            return None

    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            server = executor.submit(serve)
            if accepted:
                with client_context.wrap_socket(client_socket, server_hostname=hostname) as connection:
                    connection.sendall(b"x")
                assert server.result(timeout=6) == b"x"
            else:
                with pytest.raises(ssl.SSLCertVerificationError):
                    client_context.wrap_socket(client_socket, server_hostname=hostname)
                client_socket.close()
                server.result(timeout=6)
    finally:
        client_socket.close()
        server_socket.close()
