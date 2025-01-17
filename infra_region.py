import pulumi
import pulumi_azure as azure

""" 
- create_region_resource_group
- create_region_vnet
- create_network_security_group
- create_inbound_security_rule
- create_outbound_security_rule
- create_subnet_public
- create_subnet_private
- associate_subnet_public_with_security_group
- associate_subnet_private_with_security_group
"""

# ------------------------------------------------------------------

def create_region_resource_group(region):
    resource_group = azure.core.ResourceGroup(
        f"1-RsGr-{region[:3]}_",
        location=region
    )
    return resource_group

def create_region_vnet(region, resource_group):
    vnet = azure.network.VirtualNetwork(
        f"2-vNet-{region[:3]}_",
        resource_group_name=resource_group.name,
        location=region,
        address_spaces=["10.0.0.0/16"],
    )
    return vnet

# ------------------------------------------------------------------

def create_network_security_group(region, resource_group):
    nsg = azure.network.NetworkSecurityGroup(
        f"3-NetSecGroup-{region[:3]}_",
        resource_group_name=resource_group.name,
        location=resource_group.location,
    )
    return nsg

def create_inbound_security_rule(region, resource_group, nsg, rule_name, port, priority):
    rule = azure.network.NetworkSecurityRule(
        f"3-NetSecGroup-Rule-{rule_name}-{region[:3]}_",
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

def create_outbound_security_rule(region, resource_group, nsg, rule_name, port, priority):
    rule = azure.network.NetworkSecurityRule(
        f"3-NetSecGroup-Rule-{rule_name}-{region[:3]}_",
        resource_group_name=resource_group.name,
        network_security_group_name=nsg.name,
        priority=priority,
        access="Allow",
        direction="Outbound",
        protocol="Tcp",
        source_port_range="*",
        destination_port_range=str(port),
        source_address_prefix="*",
        destination_address_prefix="*",
    )
    return rule

# ------------------------------------------------------------------

def create_subnet_public(region, resource_group, vnet):
    subnet_public = azure.network.Subnet(
        f"4-SubNetPub-{region[:3]}_",
        resource_group_name=resource_group.name,
        virtual_network_name=vnet.name,
        address_prefixes=["10.0.1.0/24"]
    )
    return subnet_public

def create_subnet_private(region, resource_group, vnet):
    subnet_private = azure.network.Subnet(
        f"4-SubNetPri-{region[:3]}_",
        resource_group_name=resource_group.name,
        virtual_network_name=vnet.name,
        address_prefixes=["10.0.2.0/24"]
    )
    return subnet_private

def associate_subnet_public_with_security_group(region, public_subnet, security_rule):
    subnet_public_association_sg = azure.network.SubnetNetworkSecurityGroupAssociation(
        f"4-SubNetPub-asso-{region[:3]}_",
        subnet_id=public_subnet.id,
        network_security_group_id=security_rule.id
    )
    return subnet_public_association_sg

def associate_subnet_private_with_security_group(region, private_subnet, security_rule):
    subnet_private_association_sg = azure.network.SubnetNetworkSecurityGroupAssociation(
        f"4-SubNetPri-asso-{region[:3]}_",
        subnet_id=private_subnet.id,
        network_security_group_id=security_rule.id
    )
    return subnet_private_association_sg

# ------------------------------------------------------------------
