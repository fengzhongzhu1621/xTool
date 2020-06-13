# -*- coding: utf-8 -*-

from xTool.status import has_message_body
from xTool.header import is_entity_header, is_hop_by_hop_header, remove_entity_headers


def test_has_message_body():
    tests = (
        (100, False),
        (102, False),
        (204, False),
        (200, True),
        (304, False),
        (400, True),
    )
    for status_code, expected in tests:
        assert has_message_body(status_code) is expected


def test_is_entity_header():
    tests = (
        ("allow", True),
        ("extension-header", True),
        ("", False),
        ("test", False),
    )
    for header, expected in tests:
        assert is_entity_header(header) is expected


def test_is_hop_by_hop_header():
    tests = (
        ("connection", True),
        ("upgrade", True),
        ("", False),
        ("test", False),
    )
    for header, expected in tests:
        assert is_hop_by_hop_header(header) is expected


def test_remove_entity_headers():
    tests = (
        ({}, {}),
        ({"Allow": "GET, POST, HEAD"}, {}),
        (
            {
                "Content-Type": "application/json",
                "Expires": "Wed, 21 Oct 2015 07:28:00 GMT",
                "Foo": "Bar",
            },
            {"Expires": "Wed, 21 Oct 2015 07:28:00 GMT", "Foo": "Bar"},
        ),
        (
            {"Allow": "GET, POST, HEAD", "Content-Location": "/test"},
            {"Content-Location": "/test"},
        ),
    )

    for header, expected in tests:
        assert remove_entity_headers(header) == expected
