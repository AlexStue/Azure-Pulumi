import pulumi
import pulumi_azure as azure
import pulumi_azure_native as azure_native

""" 
- create_public_ip
- create_nat_gateway
- associate_nat_gateway_with_subnet
- associate_nat_gateway_with_PIP
- create_route_table_private
- associate_route_table_with_private_subnet

- create_region_resource_group
- create_region_vnet
- create_network_security_group
- create_inbound_security_rule
- create_outbound_security_rule
- create_subnet_public
- create_subnet_private
- associate_subnet_public_with_security_group
- associate_subnet_private_with_security_group

- create_alb
- create_backend_pool
- create_alb_rule
"""

# Module ------------------------------------------------------------------

def create_region_network(region, resource_group_region, azs):

    region_vnet = create_region_vnet(region, resource_group_region)
    region_nsg  = create_network_security_group(region, resource_group_region)
    
    create_inbound_security_rule(region, resource_group_region, region_nsg, "SSH", 22, 100)
    create_inbound_security_rule(region, resource_group_region, region_nsg, "HTTP", 80, 200)
    create_outbound_security_rule(region, resource_group_region, region_nsg, "SSH-Out", 22, 300)
    create_outbound_security_rule(region, resource_group_region, region_nsg, "HTTP-Out", 80, 400)

    region_az_alb, region_public_ip_alb     = create_alb(region, resource_group_region)
    region_backend_pool                     = create_backend_pool(region, region_az_alb)
    region_rule                             = create_alb_rule_for_az(region, region_az_alb, region_backend_pool)

    region_az_subnets_public = {}
    region_az_subnets_private = {}

    for az in azs[region]:
        region_az_subnets_public[az]    = create_subnet_public(region, resource_group_region, region_vnet, az)
        region_az_subnets_private[az]   = create_subnet_private(region, resource_group_region, region_vnet, az)
        associate_subnet_public_with_security_group(region, region_az_subnets_public[az], region_nsg, az)
        associate_subnet_private_with_security_group(region, region_az_subnets_private[az], region_nsg, az)

        region_az_public_ip     = create_public_ip(region, resource_group_region, az)
        region_az_nat_gateway   = create_nat_gateway(region, resource_group_region, az)
        associate_nat_gateway_with_subnet(region, region_az_subnets_public[az], region_az_nat_gateway, az)
        associate_nat_gateway_with_PIP(region, region_az_nat_gateway, region_az_public_ip, az)

        region_az_rt_private    = create_route_table_private(region, resource_group_region, az)
        associate_route_table_with_private_subnet(region, region_az_subnets_private[az], region_az_rt_private, az)

    return region_vnet, region_nsg, region_az_subnets_private, region_backend_pool

# vNet, NSG ------------------------------------------------------------------

def create_resource_group_region(region):

    resource_group_region = azure.core.ResourceGroup(
        f"1-RsGr-{region[:3]}_",
        location=region,
    )
    return resource_group_region

def create_region_vnet(region, resource_group_region):
    vnet = azure.network.VirtualNetwork(
        f"2-vNet-{region[:3]}_",
        resource_group_name=resource_group_region.name,
        location=region,
        address_spaces=["10.0.0.0/16"],
    )
    return vnet

def create_network_security_group(region, resource_group_region):
    nsg = azure.network.NetworkSecurityGroup(
        f"3-NetSecGroup-{region[:3]}_",
        resource_group_name=resource_group_region.name,
        location=region,
    )
    return nsg

def create_inbound_security_rule(region, resource_group_region, nsg, rule_name, port, priority):
    rule = azure.network.NetworkSecurityRule(
        f"3-NetSecGroup-Rule-{rule_name}-{region[:3]}_",
        resource_group_name=resource_group_region.name,
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

def create_outbound_security_rule(region, resource_group_region, nsg, rule_name, port, priority):
    rule = azure.network.NetworkSecurityRule(
        f"3-NetSecGroup-Rule-{rule_name}-{region[:3]}_",
        resource_group_name=resource_group_region.name,
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

# Subnets ------------------------------------------------------------------

def create_subnet_public(region, resource_group_region, vnet, az):
    az = int(az)
    subnet_public = azure.network.Subnet(
        f"4-SubNetPub-{region[:3]}-AZ{az}_",
        resource_group_name=resource_group_region.name,
        virtual_network_name=vnet.name,
        address_prefixes=[f"10.0.{(az-1)*2}.0/24"]
    )
    return subnet_public

def create_subnet_private(region, resource_group_region, vnet, az):
    az = int(az)
    subnet_private = azure.network.Subnet(
        f"4-SubNetPri-{region[:3]}-AZ{az}_",
        resource_group_name=resource_group_region.name,
        virtual_network_name=vnet.name,
        address_prefixes=[f"10.0.{(az-1)*2+1}.0/24"]
    )
    return subnet_private

def associate_subnet_public_with_security_group(region, public_subnet, security_rule, az):
    subnet_public_association_sg = azure.network.SubnetNetworkSecurityGroupAssociation(
        f"4-SubNetPub-asso-{region[:3]}-AZ{az}_",
        subnet_id=public_subnet.id,
        network_security_group_id=security_rule.id
    )
    return subnet_public_association_sg

def associate_subnet_private_with_security_group(region, private_subnet, security_rule, az):
    subnet_private_association_sg = azure.network.SubnetNetworkSecurityGroupAssociation(
        f"4-SubNetPri-asso-{region[:3]}-AZ{az}_",
        subnet_id=private_subnet.id,
        network_security_group_id=security_rule.id
    )
    return subnet_private_association_sg

# Public ------------------------------------------------------------------

def create_public_ip(region, resource_group_region, az):
    ip_public = azure.network.PublicIp(
        f"5-PuIP-NAT-{region[:3]}-AZ{az}_",
        resource_group_name=resource_group_region.name,
        location=region,
        allocation_method="Static",
        zones=[az],
    )
    return ip_public

def create_nat_gateway(region, resource_group_region, az):
    nat_gateway = azure.network.NatGateway(
        f"5-NATGW-{region[:3]}-AZ{az}_",
        resource_group_name=resource_group_region.name,
        location=region,
        sku_name="Standard",
        zones=[az]
    )
    return nat_gateway

def associate_nat_gateway_with_subnet(region, public_subnet, nat_gateway, az):
    nat_association_sn = azure.network.SubnetNatGatewayAssociation(
        f"5-NATGW-asso-{region[:3]}-AZ{az}_",
        subnet_id=public_subnet.id,
        nat_gateway_id=nat_gateway.id,
    )
    return nat_association_sn

def associate_nat_gateway_with_PIP(region, nat_gateway, public_ip, az):
    nat_association_pip = azure.network.NatGatewayPublicIpAssociation(
        f"5-PuIP-NAT-asso-{region[:3]}-AZ{az}_",
        nat_gateway_id=nat_gateway.id,
        public_ip_address_id=public_ip.id
    )
    return nat_association_pip

# Private ------------------------------------------------------------------

def create_route_table_private(region, resource_group_region, az):
    route_table_private = azure.network.RouteTable(
        f"5-RouTb-{region[:3]}-AZ{az}_",
        resource_group_name=resource_group_region.name,
        location=region,
        routes=[{
            "name": "route1",
            "address_prefix": "0.0.0.0/0",
            "next_hop_type": "Internet"
        }]
    )
    return route_table_private

def associate_route_table_with_private_subnet(region, private_subnet, route_table_private, az):
    private_subnet_association = azure.network.SubnetRouteTableAssociation(
        f"5-RouteTab-asso-{region[:3]}-AZ{az}_",
        subnet_id=private_subnet.id,
        route_table_id=route_table_private.id
    )
    return private_subnet_association

# ALB ------------------------------------------------------------------

def create_alb(region, resource_group_region):
    public_ip_alb = azure_native.network.PublicIPAddress(
        f"7-PIP-ALB-{region[:3]}",
        resource_group_name=resource_group_region.name,
        location=region,
        sku=azure_native.network.PublicIPAddressSkuArgs(
            name="Standard"
        ),
        public_ip_allocation_method="Static"
    )
    
    alb = azure_native.network.LoadBalancer(
        f"7-ALB-{region[:3]}",
        resource_group_name=resource_group_region.name,
        location=region,
        sku=azure_native.network.LoadBalancerSkuArgs(
            name="Standard"
        ),
        frontend_ip_configurations=[{
            "name": "frontend-ip",
            "public_ip_address": {
                "id": public_ip_alb.id
            }
        }]
    )
    return alb, public_ip_alb

def create_backend_pool(region, alb):
    backend_pool = azure.lb.BackendAddressPool(
        f"7-BcEnPo-{region[:3]}_",  
        loadbalancer_id=alb.id,
    )
    return backend_pool

def create_alb_rule_for_az(region, alb, backend_pool):
    alb_rule = azure.lb.Rule(
        f"7-ALB-Ru-{region[:3]}",
        loadbalancer_id=alb.id,
        backend_address_pool_ids=[backend_pool.id],
        frontend_ip_configuration_name="frontend-ip",
        protocol="Tcp",
        frontend_port=80,
        backend_port=80,
        enable_floating_ip=False,
        idle_timeout_in_minutes=4,
        load_distribution="Default"
    )
    return alb_rule

# Front Door------------------------------------------------------------------

# # Replace with your existing ALB's Public IP
# def create_front_door_with_alb(region, resource_group_region, region_public_ip_alb):
#     # Front Door configuration
#     front_door = azure.frontdoor.FrontDoor(
#         f"7-FrontDoor_",
#         resource_group_name=resource_group_region.name,
#         routing_rules=[{
#             "name": "defaultRoute",
#             "accepted_protocols": ["Https"],
#             "patterns_to_match": ["/*"],  # Match all traffic
#             "frontend_endpoints": [{
#                 "name": "frontendEndpoint",
#                 "host_name": "yourapp.azurefd.net",  # Front Door hostname
#             }],
#             "route_configuration": {
#                 "@type": "Microsoft.Azure.FrontDoor.Models.FrontDoorForwardingConfiguration",
#                 "forwarding_protocol": "HttpsOnly",
#                 "backend_pool": {
#                     "name": "myBackendPool",
#                 },
#             },
#         }],
#         frontend_endpoints=[{
#             "name": "frontendEndpoint",
#             "host_name": "yourapp.azurefd.net",  # Front Door hostname
#         }],
#         backend_pools=[{
#             "name": "myBackendPool",
#             "backends": [
#                 {
#                     "address": region_public_ip_alb.ip_address,  # ALB public IP
#                     "http_port": 80,
#                     "https_port": 443,
#                     "priority": 1,
#                     "weight": 50,
#                 },
#             ],
#             "load_balancing_settings": {
#                 "name": "myLoadBalancingSettings",
#                 "sample_size": 4,
#                 "successful_samples_required": 2,
#             },
#             "health_probe_settings": {
#                 "name": "myHealthProbeSettings",
#                 "probe_path": "/health",  # Health check path
#                 "probe_method": "GET",
#                 "interval_in_seconds": 30,
#             },
#         }],
#         load_balancing_settings=[{
#             "name": "myLoadBalancingSettings",
#             "sample_size": 4,
#             "successful_samples_required": 2,
#         }],
#         health_probe_settings=[{
#             "name": "myHealthProbeSettings",
#             "probe_path": "/health",
#             "probe_method": "GET",
#             "interval_in_seconds": 30,
#         }],
#     )
    
#     return front_door

# ------------------------------------------------------------------
