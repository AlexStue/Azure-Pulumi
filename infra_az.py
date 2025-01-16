import pulumi
import pulumi_azure as azure

# Public ------------------------------------------------------------------

def create_public_ip(region, resource_group, az):
    ip_public = azure.network.PublicIp(
        f"ip-public-{region}-AZ{az}_",
        resource_group_name=resource_group.name,
        location=resource_group.location,
        allocation_method="Static",
        zones=[az],
    )
    return ip_public

def create_nat_gateway(region, resource_group, az):
    nat_gateway = azure.network.NatGateway(
        f"nat-{region[:3]}-AZ{az}_",
        resource_group_name=resource_group.name,
        location=resource_group.location,
        sku_name="Standard",
        zones=[az]
    )
    return nat_gateway

def associate_nat_gateway_with_subnet(region, public_subnet, nat_gateway, az):
    nat_association_sn = azure.network.SubnetNatGatewayAssociation(
        f"nat-asso-sn-{region}-AZ{az}_",
        subnet_id=public_subnet.id,
        nat_gateway_id=nat_gateway.id,
    )
    return nat_association_sn

def associate_nat_gateway_with_PIP(region, nat_gateway, public_ip, az):
    nat_association_pip = azure.network.NatGatewayPublicIpAssociation(
        f"nat-asso-pip-{region}-AZ{az}_",
        nat_gateway_id=nat_gateway.id,
        public_ip_address_id=public_ip.id
    )
    return nat_association_pip

# Private ------------------------------------------------------------------

def create_route_table_private(region, resource_group, az):
    route_table_private = azure.network.RouteTable(
        f"rt-pr-{region[:3]}-AZ{az}_",
        resource_group_name=resource_group.name,
        location=resource_group.location,
        routes=[{
            "name": "route1",
            "address_prefix": "0.0.0.0/0",
            "next_hop_type": "Internet"
        }]
    )
    return route_table_private

def associate_route_table_with_private_subnet(region, private_subnet, route_table_private, az):
    private_subnet_association = azure.network.SubnetRouteTableAssociation(
        f"rt-pr-as-{region[:3]}-AZ{az}-",
        subnet_id=private_subnet.id,
        route_table_id=route_table_private.id
    )
    return private_subnet_association

# ------------------------------------------------------------------
