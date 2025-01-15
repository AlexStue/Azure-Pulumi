import pulumi
from pulumi_azure_native import resources, network

# ------------------------------------------------------------------

def create_region_resource_group(region):
    resource_group = resources.ResourceGroup(
        f"rg-{region}",
        location=region
    )
    return resource_group

def create_region_vnet(region, resource_group):
    vnet = network.VirtualNetwork(
        f"vnet-{region}",
        resource_group_name=resource_group.name,
        location=region,
        address_space={"addressPrefixes": ["10.0.0.0/16"]},
    )
    return vnet

# ------------------------------------------------------------------

def create_subnet_public(region, resource_group, vnet, nsg):
    subnet_public = network.Subnet(
        f"SubnetPublic-{region}",
        resource_group_name=resource_group.name,
        virtual_network_name=vnet.name,
        address_prefix="10.0.1.0/24",
        network_security_group=nsg,  # Directly reference the NSG here
    )
    return subnet_public

def create_subnet_private(region, resource_group, vnet, nsg):
    subnet_private = network.Subnet(
        f"SubnetPrivate-{region}",
        resource_group_name=resource_group.name,
        virtual_network_name=vnet.name,
        address_prefix="10.0.2.0/24",
        network_security_group=nsg,  # Directly reference the NSG here
    )
    return subnet_private

# ------------------------------------------------------------------

def create_network_security_group(region, resource_group):
    nsg = network.NetworkSecurityGroup(
        f"nsg-{region}",
        resource_group_name=resource_group.name,
        location=resource_group.location,
    )
    return nsg

def create_security_rule(region, resource_group, nsg, rule_name, port, priority):
    rule = network.SecurityRule(
        f"nsgRule-{rule_name}-{region}",
        resource_group_name=resource_group.name,
        network_security_group_name=nsg.name,
        priority=priority,
        access="Allow",
        direction="Inbound",
        protocol="Tcp",
        source_port_range="*",
        destination_port_range=str(port),
        source_address_prefix="*",
        destination_address_prefix="*",
    )
    return rule

# ------------------------------------------------------------------
