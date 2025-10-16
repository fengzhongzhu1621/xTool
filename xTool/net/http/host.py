import base64
import importlib
import socket
from binascii import Error as BinasciiError
from urllib.parse import parse_qsl, unquote, urlencode, urlparse, urlunparse

from xTool.constants import RE_HOST


def validate_host(host, allowed_hosts):
    """
    Validate the given host for this site.

    Check that the host looks valid and matches a host or host pattern in the
    given list of ``allowed_hosts``. Any pattern beginning with a period
    matches a domain and all its subdomains (e.g. ``.example.com`` matches
    ``example.com`` and any subdomain), ``*`` matches anything, and anything
    else must match exactly.

    Note: This function assumes that the given host is lowercased and has
    already had the port, if any, stripped off.

    Return ``True`` for a valid host, ``False`` otherwise.
    """
    return any(pattern == "*" or is_same_domain(host, pattern) for pattern in allowed_hosts)


def is_same_domain(host, pattern):
    """
    Return ``True`` if the host is either an exact match or a match
    to the wildcard pattern.

    Any pattern beginning with a period matches a domain and all of its
    subdomains. (e.g. ``.example.com`` matches ``example.com`` and
    ``foo.example.com``). Anything else is an exact string match.
    """
    if not pattern:
        return False

    pattern = pattern.lower()
    return pattern[0] == "." and (host.endswith(pattern) or host == pattern[1:]) or pattern == host


def urlsafe_base64_encode(s):
    """
    Encode a bytestring to a base64 string for use in URLs. Strip any trailing
    equal signs.
    """
    return base64.urlsafe_b64encode(s).rstrip(b"\n=").decode("ascii")


def urlsafe_base64_decode(s):
    """
    Decode a base64 encoded string. Add back any trailing equal signs that
    might have been stripped.
    """
    s = s.encode()
    try:
        return base64.urlsafe_b64decode(s.ljust(len(s) + len(s) % 4, b"="))
    except (LookupError, BinasciiError) as e:
        raise ValueError(e)


def split_domain_port(host):
    """
    Return a (domain, port) tuple from a given host.

    Returned domain is lowercased. If the host is invalid, the domain will be
    empty.
    """
    host = host.lower()

    if not RE_HOST.match(host):
        return "", ""

    if host[-1] == "]":
        # It's an IPv6 address without a port.
        return host, ""
    bits = host.rsplit(":", 1)
    domain, port = bits if len(bits) == 2 else (bits[0], "")
    # Remove a trailing dot (if present) from the domain.
    domain = domain[:-1] if domain.endswith(".") else domain
    return domain, port


def format_host(host: str) -> str:
    """格式化主机名 ."""
    host = host.strip("/").split("//")[-1].split(":")[0]
    return host


def url_concat(url, args):
    """Concatenate url and arguments regardless of whether
    url has existing query parameters.

    ``args`` may be either a dictionary or a list of key-value pairs
    the latter allows for multiple values with the same key.

    >>> url_concat("http://example.com/foo", dict(c="d"))
    'http://example.com/foo?c=d'
    >>> url_concat("http://example.com/foo?a=b", dict(c="d"))
    'http://example.com/foo?a=b&c=d'
    >>> url_concat("http://example.com/foo?a=b", [("c", "d"), ("c", "d2")])
    'http://example.com/foo?a=b&c=d&c=d2'
    """
    if args is None:
        return url
    parsed_url = urlparse(url)
    if isinstance(args, dict):
        parsed_query = parse_qsl(parsed_url.query, keep_blank_values=True)
        parsed_query.extend(args.items())
    elif isinstance(args, list) or isinstance(args, tuple):
        parsed_query = parse_qsl(parsed_url.query, keep_blank_values=True)
        parsed_query.extend(args)
    else:
        err = "'args' parameter should be dict, list or tuple. Not {}".format(type(args))
        raise TypeError(err)
    final_query = urlencode(parsed_query)
    url = urlunparse(
        (
            parsed_url[0],
            parsed_url[1],
            parsed_url[2],
            parsed_url[3],
            final_query,
            parsed_url[5],
        )
    )
    return url


def get_hostname(callable_path=None) -> str:
    """获得主机名 ."""
    if not callable_path:
        return socket.getfqdn()

    # Since we have a callable path, we try to import and run it next.
    # 根据配置文件中的设置的回调函数 module_path:attr_name 获取主机名
    # 加载指定模块，获得模块定义的主机属性名
    module_path, attr_name = callable_path.split(":")
    module = importlib.import_module(module_path)
    func = getattr(module, attr_name)
    # 执行属性方法返回结果
    return func()


def parse_netloc_to_hostname(uri_parts):
    """获得urlparse解析后的主机名
    Python automatically converts all letters to lowercase in hostname
    See: https://issues.apache.org/jira/browse/AIRFLOW-3615
    """
    hostname = unquote(uri_parts.hostname or "")
    if "/" in hostname:
        hostname = uri_parts.netloc
        if "@" in hostname:
            hostname = hostname.rsplit("@", 1)[1]
        if ":" in hostname:
            hostname = hostname.split(":", 1)[0]
        hostname = unquote(hostname)
    return hostname
