import pulumi
import infra_region
import infra_az
#import infra_vm

regions = ['germanywestcentral',
           'francecentral']
azs = {
    'germanywestcentral': ['1', '2'],
    'francecentral': ['1', '2']
}

# ------------------------------------------------------------------

for region in regions:

    resource_group              = infra_region.create_region_resource_group(region)
    region_vnet                 = infra_region.create_region_vnet(region, resource_group)

    region_nsg                  = infra_region.create_network_security_group(region, resource_group)
    region_nsg_rule             = infra_region.create_security_rule(region, resource_group, region_nsg, "Http", 80, 100)

    region_subnet_public        = infra_region.create_subnet_public(region, resource_group, region_vnet, region_nsg)
    region_subnet_private       = infra_region.create_subnet_private(region, resource_group, region_vnet, region_nsg)

# ------------------------------------------------------------------

    # with variables of actual loop
    for az in azs[region]:
        region_az_public_ip     = infra_az.create_public_ip(region, resource_group, az)
        region_az_nat_gateway   = infra_az.create_nat_gateway(region, resource_group, region_az_public_ip, az)
        region_az_rt_private    = infra_az.create_route_table_private(region, resource_group, region_az_nat_gateway, az)
        region_az_asso_public   = infra_az.associate_route_table_with_private_subnet(region, region_subnet_private, region_az_rt_private, az)

# ------------------------------------------------------------------
