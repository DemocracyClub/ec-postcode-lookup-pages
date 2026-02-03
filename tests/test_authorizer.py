"""
Tests for IP matching. Note that we need to reload `lambda_basic_auth` inline
in order for the os.environ patch to work.
"""

import importlib
import os
from unittest.mock import patch

import lambda_basic_auth
import pytest


@pytest.mark.parametrize(
    "allowlist,test_ip,expected",
    [
        # Missing/blank IP_ALLOWLIST tests
        # 192.0.2.0/24 is listed as a test range:
        # https://en.wikipedia.org/wiki/List_of_reserved_IP_addresses
        ("", "192.0.2.5", False),
        ("   ", "192.0.2.5", False),
        # Bad values in IP_ALLOWLIST
        ("invalid", "192.0.2.5", False),
        ("not.an.ip", "192.0.2.5", False),
        ("999.999.999.999", "192.0.2.5", False),
        ("invalid,192.0.2.5", "192.0.2.5", True),
        ("192.0.2.5,garbage", "192.0.2.5", True),
        ("garbage,192.0.2.0/23,invalid-cidr/24", "192.0.2.5", True),
        # IP_ALLOWLIST splitting tests
        ("192.0.2.5,10.0.0.1", "192.0.2.5", True),
        ("192.0.2.5,10.0.0.1", "10.0.0.1", True),
        ("192.0.2.5,10.0.0.1", "172.16.1.1", False),
        (" 192.0.2.5 , 10.0.0.1  ", "192.0.2.5", True),  # Whitespace
        ("192.0.2.5,,10.0.0.1", "10.0.0.1", True),  # Empty entry
        # CIDR matching tests
        ("10.0.0.0/8", "10.0.0.1", True),
        ("10.0.0.0/8", "10.255.255.255", True),
        ("10.0.0.0/8", "11.0.0.1", False),
        ("192.0.2.0/24", "192.0.2.5", True),
        ("192.0.2.0/32", "192.0.2.1", False),
        # Mixed CIDR and single IPs
        ("10.0.0.0/8,192.0.2.5", "10.0.0.1", True),
        ("10.0.0.0/8,192.0.2.5", "192.0.2.5", True),
        ("10.0.0.0/8,192.0.2.5", "172.16.1.1", False),
        # Invalid CIDRs should be ignored
        ("192.168.1.0/33", "192.0.2.5", False),  # Invalid /33
        ("invalid/24", "192.0.2.5", False),
    ],
)
def test_ip_allowlist(allowlist, test_ip, expected):
    """
    Test against a load of cases and assert the expected result
    """
    with patch.dict(os.environ, {"IP_ALLOWLIST": allowlist}):
        importlib.reload(lambda_basic_auth)

        result = lambda_basic_auth._ip_in_allowlist(test_ip)
        assert result == expected


def test_ip_allowlist_missing_env_var():
    """Test behavior when IP_ALLOWLIST environment variable is completely missing"""
    with patch.dict(os.environ, {}, clear=True):
        importlib.reload(lambda_basic_auth)

        assert not lambda_basic_auth._ip_in_allowlist("192.0.2.5")


def test_fallback_to_basic_auth():
    """Test that non-allowlisted IPs fall back to basic auth"""
    with patch.dict(os.environ, {"IP_ALLOWLIST": "192.0.2.5"}):
        importlib.reload(lambda_basic_auth)

        event = {
            "headers": {
                "X-Forwarded-For": "172.16.1.1",
                "Authorization": "Basic ZGM6ZGM=",
            }
        }

        result = lambda_basic_auth.lambda_handler(event, {})
        assert result["principalId"] == "basic-auth"
        assert result["policyDocument"]["Statement"][0]["Effect"] == "Allow"


def test_ip_allowlisted_success():
    """
    Check that we get authenticated when the reuest IP is in the allow list (or CIDR range)
    """
    with patch.dict(os.environ, {"IP_ALLOWLIST": "192.0.2.5,10.0.0.0/8"}):
        importlib.reload(lambda_basic_auth)

        event = {"headers": {"X-Forwarded-For": "192.0.2.5"}}
        result = lambda_basic_auth.lambda_handler(event, {})

        assert result["principalId"] == "ip-allowlisted"
        assert result["policyDocument"]["Statement"][0]["Effect"] == "Allow"
