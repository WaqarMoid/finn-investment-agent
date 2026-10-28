import socket
import ipaddress
from urllib.parse import urlparse
from typing import Tuple

BLOCKED_IP_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),      # Loopback
    ipaddress.ip_network("10.0.0.0/8"),       # RFC 1918 Private
    ipaddress.ip_network("172.16.0.0/12"),    # RFC 1918 Private
    ipaddress.ip_network("192.168.0.0/16"),   # RFC 1918 Private
    ipaddress.ip_network("169.254.0.0/16"),   # Link-Local / Cloud Metadata (AWS/GCP/Azure)
    ipaddress.ip_network("0.0.0.0/8"),        # Broadcast / unspecified
    ipaddress.ip_network("::1/128"),          # IPv6 Loopback
    ipaddress.ip_network("fe80::/10"),        # IPv6 Link-Local
    ipaddress.ip_network("fc00::/7"),         # IPv6 Unique Local
]

def validate_url_ssrf_safe(url: str) -> Tuple[bool, str]:
    """Validates that a URL is a publicly accessible HTTP(S) address and not an internal network or metadata target.

    Guarantees:
    - Scheme must be http or https (no file://, gopher://, ftp://).
    - Hostname must resolve to a valid IP.
    - Resolved IP must NOT be in loopback, RFC 1918, link-local, or cloud metadata ranges.
    """
    if not url:
        return False, "URL cannot be empty"

    try:
        parsed = urlparse(url)
    except Exception as e:
        return False, f"Malformed URL: {e}"

    if parsed.scheme.lower() not in ["http", "https"]:
        return False, f"Invalid scheme '{parsed.scheme}'. Only http and https are permitted."

    hostname = parsed.hostname
    if not hostname:
        return False, "URL missing hostname"

    # Reject obvious local names directly
    lower_host = hostname.lower()
    if lower_host in ["localhost", "127.0.0.1", "metadata.google.internal", "instance-data"]:
        return False, f"Blocked target: {hostname} is a restricted internal host."

    # Resolve hostname to IP address
    try:
        addr_info = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        return False, f"Could not resolve hostname '{hostname}'"

    for family, _, _, _, sockaddr in addr_info:
        ip_str = sockaddr[0]
        try:
            ip_obj = ipaddress.ip_address(ip_str)
            for blocked_net in BLOCKED_IP_NETWORKS:
                if ip_obj in blocked_net:
                    return False, f"Blocked target: {hostname} resolves to restricted private IP {ip_str}"
        except ValueError:
            return False, f"Invalid IP address format: {ip_str}"

    return True, "Valid public URL"
