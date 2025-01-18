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
        location=region,
        opts=pulumi.ResourceOptions(protect=True)
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
