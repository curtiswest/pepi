from server import IPTools
import pytest

def test_current_ip():
    ip_list = IPTools.current_ip()
    assert isinstance(ip_list, list)
    if len(ip_list) > 0:
        for ip in ip_list:
            parts = ip.split('.')
            assert len(parts) == 4
            for part in parts:
                assert 0 < len(part) <= 3


def test_gateway_ip():
    gateway_ip = IPTools.gateway_ip()
    if gateway_ip is not None:
        assert isinstance(gateway_ip, (str, unicode))
        parts = gateway_ip.split('.')
        assert len(parts) == 4
        for part in parts:
            assert 0 < len(part) <= 3


def test_get_first_digits_from():
    test_ip = '10.0.0.0'
    expected = '10.0.0.'
    assert expected == IPTools.get_first_digits_from(test_ip, 3)
    expected = '10.0.0'
    assert expected == IPTools.get_first_digits_from(test_ip, 3, with_dot=False)
    expected = '10'
    assert expected == IPTools.get_first_digits_from(test_ip, 1, with_dot=False)
    expected = '10.0.0.0'
    assert expected == IPTools.get_first_digits_from(test_ip, 10, with_dot=False)

def test_get_subnet_from():
    test_ip = '127.0.0.1'
    expected = '127.0.0.'
    assert expected == IPTools.get_subnet_from(test_ip)
    expected = '127.0.0.'
    assert expected == IPTools.get_subnet_from(test_ip, with_dot=True)
    expected = '127.0.0'
    assert expected == IPTools.get_subnet_from(test_ip, with_dot=False)
    test_ip = '127.0.0.0.0.0.0.0'
    assert expected == IPTools.get_subnet_from(test_ip, with_dot=False)
    test_ip = '127.0.'
    expected = '127.0'
    assert expected == IPTools.get_subnet_from(test_ip, with_dot=False)
    expected = '127.0.'
    assert expected == IPTools.get_subnet_from(test_ip, with_dot=True)