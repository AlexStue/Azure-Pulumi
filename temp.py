import pulumi
from pulumi_azure_native import network, resources

# Azure region
region = "germanywestcentral"

# Create a Resource Group
resource_group = resources.ResourceGroup("resourceGroup", location=region)

# Create a Virtual Network
vnet = network.VirtualNetwork(
    "vNet",
    resource_group_name=resource_group.name,
    location=resource_group.location,
    address_space={"addressPrefixes": ["10.0.0.0/16"]},
)

# Public Subnets
public_subnet_az1 = network.Subnet(
    "publicSubnetAz1",
    resource_group_name=resource_group.name,
    virtual_network_name=vnet.name,
    address_prefix="10.0.1.0/24",
)

public_subnet_az2 = network.Subnet(
    "publicSubnetAz2",
    resource_group_name=resource_group.name,
    virtual_network_name=vnet.name,
    address_prefix="10.0.2.0/24",
)

# Private Subnets
private_subnet_az1 = network.Subnet(
    "privateSubnetAz1",
    resource_group_name=resource_group.name,
    virtual_network_name=vnet.name,
    address_prefix="10.0.3.0/24",
)

private_subnet_az2 = network.Subnet(
    "privateSubnetAz2",
    resource_group_name=resource_group.name,
    virtual_network_name=vnet.name,
    address_prefix="10.0.4.0/24",
)

# Internet Gateway equivalent in Azure is handled automatically for public IPs.

# Public IPs for NAT Gateways
public_ip_az1 = network.PublicIPAddress(
    "publicIpAz1",
    resource_group_name=resource_group.name,
    location=resource_group.location,
    sku={"name": "Standard"},
    allocation_method="Static",
)

public_ip_az2 = network.PublicIPAddress(
    "publicIpAz2",
    resource_group_name=resource_group.name,
    location=resource_group.location,
    sku={"name": "Standard"},
    allocation_method="Static",
)

# NAT Gateways
nat_gateway_az1 = network.NatGateway(
    "natGatewayAz1",
    resource_group_name=resource_group.name,
    location=resource_group.location,
    public_ip_addresses=[{"id": public_ip_az1.id}],
    sku={"name": "Standard"},
)

nat_gateway_az2 = network.NatGateway(
    "natGatewayAz2",
    resource_group_name=resource_group.name,
    location=resource_group.location,
    public_ip_addresses=[{"id": public_ip_az2.id}],
    sku={"name": "Standard"},
)

# Associate NAT Gateways with Public Subnets
nat_association_az1 = network.SubnetNatGatewayAssociation(
    "natAssociationAz1",
    subnet_id=public_subnet_az1.id,
    nat_gateway_id=nat_gateway_az1.id,
)

nat_association_az2 = network.SubnetNatGatewayAssociation(
    "natAssociationAz2",
    subnet_id=public_subnet_az2.id,
    nat_gateway_id=nat_gateway_az2.id,
)

# Route Tables
route_table_private_az1 = network.RouteTable(
    "routeTablePrivateAz1",
    resource_group_name=resource_group.name,
    location=resource_group.location,
)

route_table_private_az2 = network.RouteTable(
    "routeTablePrivateAz2",
    resource_group_name=resource_group.name,
    location=resource_group.location,
)

# Associate Route Tables with Private Subnets
private_subnet_rt_association_az1 = network.SubnetRouteTableAssociation(
    "privateSubnetRouteTableAssociationAz1",
    subnet_id=private_subnet_az1.id,
    route_table_id=route_table_private_az1.id,
)

private_subnet_rt_association_az2 = network.SubnetRouteTableAssociation(
    "privateSubnetRouteTableAssociationAz2",
    subnet_id=private_subnet_az2.id,
    route_table_id=route_table_private_az2.id,
)

# Network Security Groups (NSGs)
nsg_public = network.NetworkSecurityGroup(
    "nsgPublic",
    resource_group_name=resource_group.name,
    location=resource_group.location,
)

nsg_private = network.NetworkSecurityGroup(
    "nsgPrivate",
    resource_group_name=resource_group.name,
    location=resource_group.location,
)

# NSG Rules for Port 80
nsg_rule_http = network.SecurityRule(
    "nsgRuleHttp",
    resource_group_name=resource_group.name,
    network_security_group_name=nsg_public.name,
    priority=100,
    access="Allow",
    direction="Inbound",
    protocol="Tcp",
    source_port_range="*",
    destination_port_range="80",
    source_address_prefix="*",
    destination_address_prefix="*",
)

# Associate NSGs with Subnets
public_nsg_association_az1 = network.SubnetNetworkSecurityGroupAssociation(
    "publicNsgAssociationAz1",
    subnet_id=public_subnet_az1.id,
    network_security_group_id=nsg_public.id,
)

public_nsg_association_az2 = network.SubnetNetworkSecurityGroupAssociation(
    "publicNsgAssociationAz2",
    subnet_id=public_subnet_az2.id,
    network_security_group_id=nsg_public.id,
)

private_nsg_association_az1 = network.SubnetNetworkSecurityGroupAssociation(
    "privateNsgAssociationAz1",
    subnet_id=private_subnet_az1.id,
    network_security_group_id=nsg_private.id,
)

private_nsg_association_az2 = network.SubnetNetworkSecurityGroupAssociation(
    "privateNsgAssociationAz2",
    subnet_id=private_subnet_az2.id,
    network_security_group_id=nsg_private.id,
)

# Outputs
pulumi.export("vnet_name", vnet.name)
pulumi.export("public_subnet_az1_id", public_subnet_az1.id)
pulumi.export("public_subnet_az2_id", public_subnet_az2.id)
pulumi.export("private_subnet_az1_id", private_subnet_az1.id)
pulumi.export("private_subnet_az2_id", private_subnet_az2.id)
