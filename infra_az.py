import pulumi
from pulumi_azure_native import resources, network

# Public ------------------------------------------------------------------

def create_public_ip(region, resource_group, az):
    ip_public = network.PublicIPAddress(
        f"ip_public-{region}-AZ{az}-",
        resource_group_name=resource_group.name,
        location=resource_group.location,
        sku={"name": "Standard"},
        public_ip_allocation_method="Static",
        zones=[az],  # Specify the AZ for the public IP
    )
    return ip_public

# # Public Route Table with Target public IP
# def create_route_table_public(region, resource_group, az):
#     route_table_public = network.RouteTable(
#         f"RouteTablePublic-{region}-AZ{az}-",
#         resource_group_name=resource_group.name,
#         location=resource_group.location,
#     )
#     return route_table_public

# NAT Gateway in public Subnet
def create_nat_gateway(region, resource_group, public_ip, az):
    nat_gateway = network.NatGateway(
        f"nat_gateway-{region}-AZ{az}-",
        resource_group_name=resource_group.name,
        location=resource_group.location,
        public_ip_addresses=[{"id": public_ip.id}],
        sku={"name": "Standard"},
    )
    return nat_gateway

# # Associate NAT Gateway with public Route Table
# def associate_nat_gateway_with_route_table(region, public_subnet, nat_gateway, az):
#     nat_association = network.SubnetNatGatewayAssociation(
#         f"natAssociation-{region}-AZ{az}-",
#         subnet_id=public_subnet.id,
#         nat_gateway_id=nat_gateway.id,
#     )
#     return nat_association

# Private ------------------------------------------------------------------

# Private Route Table with Target NAT Gateway
def create_route_table_private(region, resource_group, region_az_nat_gateway, az):
    route_table_private = network.RouteTable(
        f"RouteTablePrivate-{region}-AZ{az}-",
        resource_group_name=resource_group.name,
        location=resource_group.location,
        routes=[  # Directly define the routes as part of the constructor
            network.RouteArgs(
                name="default-route",
                address_prefix="0.0.0.0/0",  # Default route
                next_hop_type="NatGateway",
                next_hop_ip_address=region_az_nat_gateway.id,  # Use the NAT Gateway's ID directly
            )
        ],
    )

    return route_table_private


# Associate Route Table with private Subnet
def associate_route_table_with_private_subnet(region, private_subnet, route_table_private, az):
    private_subnet_association = network.Subnet(
        f"privateSubnet-{region}-AZ{az}-",
        resource_group_name=private_subnet.resource_group_name,
        virtual_network_name=private_subnet.virtual_network_name,
        name=private_subnet.name,
        address_prefix=private_subnet.address_prefix,
        route_table=network.RouteTableArgs(
            id=route_table_private.id,  # Associate the route table here
        ),
    )
    return private_subnet_association

# ------------------------------------------------------------------
