# -*- coding: utf-8 -*-
'''
Module for handling openstack neutron calls.

:optdepends:    - neutronclient Python adapter
:configuration: This module is not usable until the following are specified
    either in a pillar or in the minion's config file::

        keystone.user: admin
        keystone.password: verybadpass
        keystone.tenant: admin
        keystone.tenant_id: f80919baedab48ec8931f200c65a50df
        keystone.insecure: False   #(optional)
        keystone.auth_url: 'http://127.0.0.1:5000/v2.0/'

    If configuration for multiple openstack accounts is required, they can be
    set up as different configuration profiles:
    For example::

        openstack1:
          keystone.user: admin
          keystone.password: verybadpass
          keystone.tenant: admin
          keystone.tenant_id: f80919baedab48ec8931f200c65a50df
          keystone.auth_url: 'http://127.0.0.1:5000/v2.0/'

        openstack2:
          keystone.user: admin
          keystone.password: verybadpass
          keystone.tenant: admin
          keystone.tenant_id: f80919baedab48ec8931f200c65a50df
          keystone.auth_url: 'http://127.0.0.2:5000/v2.0/'

    With this configuration in place, any of the keystone functions can make use
    of a configuration profile by declaring it explicitly.
    For example::

        salt '*' neutron.list_subnets profile=openstack1
'''

import logging
from functools import wraps
LOG = logging.getLogger(__name__)
# Import third party libs
HAS_NEUTRON = False
try:
    from neutronclient.v2_0 import client
    HAS_NEUTRON = True
except ImportError:
    pass

__opts__ = {}
def __virtual__():
    '''
    Only load this module if neutron
    is installed on this minion.
    '''
    if HAS_NEUTRON:
        return 'neutron'
    return False


def auth_decorator(func_name):
    @wraps(func_name)
    def decorator_method(
            profile=None, connection_user=None, connection_password=None,
            connection_tenant=None, connection_endpoint=None,
            conection_token=None, connection_auth_url=None, **kwargs):
        LOG.error('called with '+ str(kwargs))
        kstone = __salt__['keystone.auth'](
            profile=profile, connection_user=connection_user, connection_password=connection_password,
            connection_tenant=connection_tenant, connection_endpoint=connection_endpoint,
            conection_token=conection_token, connection_auth_url=connection_auth_url)
        token = kstone.auth_token
        endpoint = kstone.service_catalog.url_for(
            service_type='network',
            endpoint_type='publicURL')
        neutron_interface = client.Client(
            endpoint_url=endpoint, token=token)
        return_data = func_name(neutron_interface, **kwargs)
        if isinstance(return_data, list):
            return openstack_list_data_formater(return_data)
        return return_data
    return decorator_method


def openstack_list_data_formater(return_data):
    salt_return_data = {}
    for item in return_data:
        if item.get('name', None):
            salt_return_data.update({item['name']: item})
    return salt_return_data
                

@auth_decorator
def list_floatingips(neutron_interface, **kwargs):
    return neutron_interface.list_floatingips(**kwargs)['floatingips']

@auth_decorator
def list_security_groups(neutron_interface, **kwargs):
    return neutron_interface.list_security_groups(**kwargs)['security_groups']

@auth_decorator
def list_subnets(neutron_interface, **kwargs):
    return neutron_interface.list_subnets(**kwargs)['subnets']

@auth_decorator
def list_networks(neutron_interface, **kwargs):
    return neutron_interface.list_networks(**kwargs)['networks']

@auth_decorator
def list_ports(neutron_interface, **kwargs):
    return neutron_interface.list_ports(**kwargs)['ports']

@auth_decorator
def list_routers(neutron_interface, **kwargs):
    return neutron_interface.list_routers(**kwargs)['routers']

@auth_decorator
def update_security_group(neutron_interface, **kwargs):
    neutron_interface.update_security_group({'security_group': kwargs})

@auth_decorator
def update_floating_ip(neutron_interface, fip, port_id):
    neutron_interface.update_floatingip(fip, {"floatingip":
                                        {"port_id": port_id}})

@auth_decorator
def update_subnet(neutron_interface, subnet_id, subnet):
    neutron_interface.update_subnet(subnet_id, {'subnet': subnet})

@auth_decorator
def update_router(neutron_interface, router_id, external_network_id):
    neutron_interface.update_router(router_id,
                              {'router':
                                  {'external_gateway_info':
                                      {'network_id':
                                          external_network_id}}})

@auth_decorator
def create_router(neutron_interface, **kwargs):
    response = neutron_interface.create_router({'router': kwargs})
    if 'router' in response and 'id' in response['router']:
        return response['router']['id']

@auth_decorator
def router_add_interface(neutron_interface, router_id, subnet_id):
    neutron_interface.add_interface_router(router_id, {'subnet_id': subnet_id})

@auth_decorator
def router_rem_interface(neutron_interface, router_id, subnet_id):
    neutron_interface.remove_interface_router(router_id,
                                        {'subnet_id': subnet_id})

@auth_decorator
def create_security_group(neutron_interface, **kwargs):
    response = neutron_interface.create_security_group({'security_group':
                                                 kwargs})
    if 'security_group' in response and 'id' in response['security_group']:
        return response['security_group']['id']

@auth_decorator
def create_security_group_rule(neutron_interface, rule):
    neutron_interface.create_security_group_rule({'security_group_rule':
                                            rule})

@auth_decorator
def create_floatingip(neutron_interface, floatingip):
    response = neutron_interface.create_floatingip({'floatingip': floatingip})
    if 'floatingip' in response and 'id' in response['floatingip']:
        return response['floatingip']['id']

@auth_decorator
def create_subnet(neutron_interface, **kwargs):
    response = neutron_interface.create_subnet({'subnet': kwargs})
    if 'subnet' in response and 'id' in response['subnet']:
        return response['subnet']['id']

@auth_decorator
def create_network(neutron_interface, **kwargs):
    response = neutron_interface.create_network({'network': kwargs})
    if 'network' in response and 'id' in response['network']:
        return response['network']['id']

@auth_decorator
def create_port(neutron_interface, **kwargs):
    response = neutron_interface.create_port({'port': kwargs})
    if 'port' in response and 'id' in response['port']:
        return response['port']['id']

@auth_decorator
def update_port(neutron_interface, port_id, port):
    neutron_interface.update_port(port_id, {'port': port})

@auth_decorator
def delete_floating_ip(neutron_interface, floating_ip_id):
    neutron_interface.delete_floatingip(floating_ip_id)

@auth_decorator
def delete_security_group(neutron_interface, sg_id):
    neutron_interface.delete_security_group(sg_id)

@auth_decorator
def delete_security_group_rule(neutron_interface, rule):
    sg_rules = neutron_interface.list_security_group_rules(
        security_group_id=rule['security_group_id'])
    for sg_rule in sg_rules['security_group_rules']:
        sgr_id = sg_rule.pop('id')
        if sg_rule == rule:
            neutron_interface.delete_security_group_rule(sgr_id)

@auth_decorator
def delete_subnet(neutron_interface, subnet_id):
    neutron_interface.delete_subnet(subnet_id)

@auth_decorator
def delete_network(neutron_interface, network_id):
    neutron_interface.delete_network(network_id)

@auth_decorator
def delete_router(neutron_interface, router_id):
    neutron_interface.delete_router(router_id)
