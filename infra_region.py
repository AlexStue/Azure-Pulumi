import pulumi
import pulumi_azure as azure

# ------------------------------------------------------------------

def create_region_resource_group(region):
    resource_group = azure.core.ResourceGroup(
        f"rg-{region}_",  # The resource_name
        location=region
    )
    return resource_group

def create_region_vnet(region, resource_group):
    vnet = azure.network.VirtualNetwork(
        f"vnet-{region}_",  # This is the resource_name
        resource_group_name=resource_group.name,
        location=region,
        address_spaces=["10.0.0.0/16"],
    )
    return vnet


# ------------------------------------------------------------------

def create_network_security_group(region, resource_group):
    nsg = azure.network.NetworkSecurityGroup(
        f"nsg-{region}_",
        resource_group_name=resource_group.name,
        location=resource_group.location,
    )
    return nsg

def create_all_traffic_security_rules(region, resource_group, nsg, rule_name, priority):
    inbound_rule = azure.network.NetworkSecurityRule(
        f"nsg-rule-{rule_name}-inbound-{region}_",
        resource_group_name=resource_group.name,
        network_security_group_name=nsg.name,
        priority=priority,
        access="Allow",
        direction="Inbound",
        protocol="*",
        source_port_range="*",
        destination_port_range="*",
        source_address_prefix="*",
        destination_address_prefix="*",
    )

    outbound_rule = azure.network.NetworkSecurityRule(
        f"nsg-rule-{rule_name}-outbound-{region}_",
        resource_group_name=resource_group.name,
        network_security_group_name=nsg.name,
        priority=priority + 100,
        access="Allow",
        direction="Outbound",
        protocol="*",
        source_port_range="*",
        destination_port_range="*",
        source_address_prefix="*",
        destination_address_prefix="*",
    )
    return inbound_rule, outbound_rule


# ------------------------------------------------------------------

def create_subnet_public(region, resource_group, vnet):
    subnet_public = azure.network.Subnet(
        f"subnet-public-{region}",
        resource_group_name=resource_group.name,
        virtual_network_name=vnet.name,
        address_prefixes=["10.0.1.0/24"]
    )
    return subnet_public

def create_subnet_private(region, resource_group, vnet):
    subnet_private = azure.network.Subnet(
        f"subnet-private-{region}",
        resource_group_name=resource_group.name,
        virtual_network_name=vnet.name,
        address_prefixes=["10.0.2.0/24"]
    )
    return subnet_private

def associate_subnet_public_with_security_group(region, public_subnet, security_rule):
    subnet_public_association_sg = azure.network.SubnetNetworkSecurityGroupAssociation(
        f"sc-as-sb-public-{region[:3]}-",
        subnet_id=public_subnet.id,
        network_security_group_id=security_rule.id
    )
    return subnet_public_association_sg

def associate_subnet_private_with_security_group(region, private_subnet, security_rule):
    subnet_private_association_sg = azure.network.SubnetNetworkSecurityGroupAssociation(
        f"sc-as-sb-private-{region[:3]}-",
        subnet_id=private_subnet.id,
        network_security_group_id=security_rule.id
    )
    return subnet_private_association_sg

# ------------------------------------------------------------------
