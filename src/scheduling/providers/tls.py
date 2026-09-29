"""Verified TLS for the approved endpoint, including its missing Linux issuers."""

from importlib.resources import files
import platform
import ssl

import certifi
import truststore


def create_tls_context():
    if platform.system() != "Linux":
        return truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    # OpenSSL does not fetch missing intermediates. These ordinary (not TRUSTED)
    # certificates only complete paths to existing Mozilla roots. Disallow partial
    # chains so neither supplemental certificate becomes a new trust anchor.
    context = ssl.create_default_context(cafile=certifi.where())
    context.verify_flags &= ~ssl.VERIFY_X509_PARTIAL_CHAIN
    context.load_verify_locations(
        cadata=files("scheduling.providers").joinpath("issuer-chain.crt").read_text(encoding="ascii")
    )
    return context
