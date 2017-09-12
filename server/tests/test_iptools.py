import netifaces

from server import IPTools


# noinspection PyAttributeOutsideInit,PyPep8
class TestIPTools(object):
    """
    Unit tests for IPTools module, mainly checking that it
    extracts the correct IPs from the netifaces package
    and that they are correctly formatted.
    """
    def test_current_ip(self, monkeypatch):
        def mock_netifaces_ifaddrs(_):
            if self.first_mock_netifaces:
                self.first_mock_netifaces = False
                return {netifaces.AF_LINK: [{'addr': u'00:e0:4c:68:01:cc'}],
                 netifaces.AF_INET: [{'broadcast': u'10.0.0.255', 'netmask': u'255.255.255.0', 'addr': u'10.0.0.25'}],
                 netifaces.AF_INET6: [{'netmask': u'ffff:ffff:ffff:ffff::/64', 'flags': 1024, 'addr': u'fe80::81a:bbbb:5899:f449%en4'}]}
            else:
                return {netifaces.AF_LINK: [{'addr': u'00:e0:4c:68:01:cc'}]}

        self.first_mock_netifaces = True
        monkeypatch.setattr('netifaces.ifaddresses', mock_netifaces_ifaddrs)
        ip_list = IPTools.current_ips()
        assert len(ip_list) == 1
        assert ip_list[0] == '10.0.0.25'

    def test_current_ip_for_multiple(self, monkeypatch):
        def mock_netifaces_ifaddrs(_):
            self.mock_netifaces_counter += 1
            return {netifaces.AF_LINK: [{'addr': u'00:e0:4c:68:01:cc'}],
             netifaces.AF_INET: [{'broadcast': u'10.0.0.255', 'netmask': u'255.255.255.0', 'addr': u'10.0.0.{}'.format(self.mock_netifaces_counter)}],
             netifaces.AF_INET6: [{'netmask': u'ffff:ffff:ffff:ffff::/64', 'flags': 1024, 'addr': u'fe80::81a:bbbb:5899:f449%en4'}]}

        self.mock_netifaces_counter = 1
        monkeypatch.setattr('netifaces.ifaddresses', mock_netifaces_ifaddrs)
        ip_list = IPTools.current_ips()
        interface_ip_count = [x+2 for x in range(len(netifaces.interfaces()))]
        zipped = zip(ip_list, interface_ip_count)
        for ip, count in zipped:
            assert ip == '10.0.0.{}'.format(count)

    def test_no_best_candidate_ip_no_gateway(self, monkeypatch):
        def mock_netifaces_ifaddrs(_):
            self.mock_netifaces_counter += 1
            return {netifaces.AF_LINK: [{'addr': u'00:e0:4c:68:01:cc'}],
             netifaces.AF_INET: [{'broadcast': u'10.0.0.255', 'netmask': u'255.255.255.0', 'addr': u'65.23.23.{}'.format(self.mock_netifaces_counter)}],
             netifaces.AF_INET6: [{'netmask': u'ffff:ffff:ffff:ffff::/64', 'flags': 1024, 'addr': u'fe80::81a:bbbb:5899:f449%en4'}]}

        self.mock_netifaces_counter = 1
        monkeypatch.setattr('netifaces.ifaddresses', mock_netifaces_ifaddrs)
        ip_list = IPTools.current_ips()
        interface_ip_count = [x+2 for x in range(len(netifaces.interfaces()))]
        zipped = zip(ip_list, interface_ip_count)
        for ip, count in zipped:
            assert ip == '65.23.23.{}'.format(count)

    def test_no_best_candidate_no_gateway(self, monkeypatch):
        def mock_netifaces_gateways():
            return {}
        def mock_netifaces_ifaddrs(_):
            self.mock_netifaces_counter += 1
            return {netifaces.AF_LINK: [{'addr': u'00:e0:4c:68:01:cc'}],
             netifaces.AF_INET: [{'broadcast': u'10.0.0.255', 'netmask': u'255.255.255.0', 'addr': u'127.0.0.{}'.format(self.mock_netifaces_counter)}],
             netifaces.AF_INET6: [{'netmask': u'ffff:ffff:ffff:ffff::/64', 'flags': 1024, 'addr': u'fe80::81a:bbbb:5899:f449%en4'}]}

        self.mock_netifaces_counter = 1
        monkeypatch.setattr('netifaces.ifaddresses', mock_netifaces_ifaddrs)
        monkeypatch.setattr('netifaces.gateways', mock_netifaces_gateways)
        ip_list = IPTools.current_ips()
        interface_ip_count = [x + 2 for x in range(len(netifaces.interfaces()))]
        zipped = zip(ip_list, interface_ip_count)
        for ip, count in zipped:
            assert ip == '127.0.0.{}'.format(count)

    def test_gateway_ip(self, monkeypatch):
        def mock_netifaces_gateways():
            return {'default': {2: (u'10.0.0.1', u'en4')}, 2: [(u'10.0.0.1', u'en4', True)],
             30: [(u'fe80::%utun0', u'utun0', False)]}

        monkeypatch.setattr('netifaces.gateways', mock_netifaces_gateways)
        gateway_ip = IPTools.gateway_ip()
        assert gateway_ip == '10.0.0.1'

    def test_no_gateway_ip(self, monkeypatch):
        def mock_netifaces_gateways():
            return {}

        monkeypatch.setattr('netifaces.gateways', mock_netifaces_gateways)
        gateway_ip = IPTools.gateway_ip()
        assert not gateway_ip

    def test_current_ips_without_gateway(self, monkeypatch):
        def mock_netifaces_gateways():
            return {}

        def mock_netifaces_ifaddrs(_):
            if self.first_mock_netifaces:
                self.first_mock_netifaces = False
                return {netifaces.AF_LINK: [{'addr': u'00:e0:4c:68:01:cc'}],
                 netifaces.AF_INET: [{'broadcast': u'10.0.0.255', 'netmask': u'255.255.255.0', 'addr': u'127.0.0.1'}],
                 netifaces.AF_INET6: [{'netmask': u'ffff:ffff:ffff:ffff::/64', 'flags': 1024, 'addr': u'fe80::81a:bbbb:5899:f449%en4'}]}
            else:
                self.mock_netifaces_counter += 1
                return {netifaces.AF_LINK: [{'addr': u'00:e0:4c:68:01:cc'}],
                        netifaces.AF_INET: [{'broadcast': u'10.0.0.255', 'netmask': u'255.255.255.0',
                                             'addr': u'10.0.0.{}'.format(self.mock_netifaces_counter)}],
                        netifaces.AF_INET6: [{'netmask': u'ffff:ffff:ffff:ffff::/64', 'flags': 1024,
                                              'addr': u'fe80::81a:bbbb:5899:f449%en4'}]}

        self.first_mock_netifaces = True
        self.mock_netifaces_counter = 1
        monkeypatch.setattr('netifaces.gateways', mock_netifaces_gateways)
        monkeypatch.setattr('netifaces.ifaddresses', mock_netifaces_ifaddrs)
        ip_list = IPTools.current_ips()
        interface_ip_count = [x+2 for x in range(len(netifaces.interfaces()))]

        assert '127.0.0.1' not in ip_list
        zipped = zip(ip_list, interface_ip_count)
        for ip, count in zipped:
            assert ip == '10.0.0.{}'.format(count)

    def test_get_first_digits_from(self):
        test_ip = '10.0.0.0'
        expected = '10.0.0.'
        assert expected == IPTools.get_first_digits_from(test_ip, 3)
        expected = '10.0.0'
        assert expected == IPTools.get_first_digits_from(test_ip, 3, with_dot=False)
        expected = '10'
        assert expected == IPTools.get_first_digits_from(test_ip, 1, with_dot=False)
        expected = '10.0.0.0'
        assert expected == IPTools.get_first_digits_from(test_ip, 10, with_dot=False)

    def test_get_subnet_from(self):
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