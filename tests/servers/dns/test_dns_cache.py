# -*- coding: utf-8 -*-

from unittest import TestCase
import pytest
from xTool.servers.dns.dns_cache import DNSCacheTable


class TestDNSCacheTable(TestCase):
    def setUp(self):
        self.tl_dns_cache = 10
        self.cached_hosts = DNSCacheTable(self.tl_dns_cache)
        self.key = ("example.com", 9000)
        self.addrs = [{
            "hostname": 'example.com',
            "host": "192.168.10.1",
            "port": 9000,
            "proto": 0,
        }, {
            "hostname": 'example.com',
            "host": "192.168.10.2",
            "port": 9000,
            "proto": 0,
        }]

    def test_add(self):
        self.cached_hosts.add(self.key, self.addrs)
        assert self.key in self.cached_hosts

    def test_remove(self):
        self.cached_hosts.remove(self.key)
        assert self.key not in self.cached_hosts

        self.cached_hosts.add(self.key, self.addrs)
        assert self.key in self.cached_hosts
        self.cached_hosts.remove(self.key)
        assert self.key not in self.cached_hosts

    def test_clean(self):
        self.cached_hosts.add(self.key, self.addrs)
        assert self.key in self.cached_hosts
        self.cached_hosts.clear()
        assert self.key not in self.cached_hosts
        with pytest.raises(TypeError):
            self.cached_hosts.expired()

    def test_next_addrs(self):
        with pytest.raises(KeyError):
            self.cached_hosts.next_addrs(self.key)
        self.cached_hosts.add(self.key, self.addrs)
        addrs = self.cached_hosts.next_addrs(self.key)
        assert addrs == self.addrs
        addrs = self.cached_hosts.next_addrs(self.key)
        assert addrs == [self.addrs[1], self.addrs[0]]
        addrs = self.cached_hosts.next_addrs(self.key)
        assert addrs == self.addrs
