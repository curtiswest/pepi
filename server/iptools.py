"""
Tools related to IP operations, mainly getting IP's and checking if servers exist at a certain IP:port combination.
"""
import netifaces

__author__ = 'Curtis West'
__copyright__ = 'Copyright 2017, Curtis West'
__version__ = '2.0a'
__maintainer__ = 'Curtis West'
__email__ = 'curtis@curtiswest.net'
__status__ = 'Development'


class IPTools(object):
    """
    Static methods that work on IP-based connections, such as getting current IP, gateway IP, etc.
    """

    @staticmethod
    def current_ip():
        candidates = []
        gateway = None
        for interface in netifaces.interfaces():
            try:
                candidates.append(netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr'])
                gateway = IPTools.gateway_ip()
            except (KeyError, IndexError):
                pass

        if gateway:
            gateway_subnet = IPTools.get_first_digits_from(gateway, 1)
            if any(c.startswith(gateway_subnet) for c in candidates):
                candidates = (c for c in candidates if c.startswith(gateway_subnet))
                return list(candidates)
        else:
            if any(not c.startswith('127') for c in candidates):
                candidates = (c for c in candidates if not c.startswith('127'))  # Remove any localhost 127.x.x.x IPs
        return list(candidates)

    @staticmethod
    def gateway_ip():
        try:
            return netifaces.gateways()['default'][netifaces.AF_INET][0]
        except (KeyError, IndexError):  # pragma: no cover
            return None

    @staticmethod
    def get_first_digits_from(ip, num_digits, with_dot=True):
        return ".".join(ip.split('.')[0:num_digits]) + ('.' if with_dot else '')

    @staticmethod
    def get_subnet_from(ip, with_dot=True):
        return ".".join(ip.split('.')[0:-1]) + ('.' if with_dot else '')
