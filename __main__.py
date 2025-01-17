import pulumi
import infra_region
import infra_az
import infra_vm
import infra_alb

regions = ['germanywestcentral']
#regions = ['germanywestcentral',
#           'francecentral']

azs = {
    'germanywestcentral': ['1']
}
# azs = {
#     'germanywestcentral': ['1', '2'],
#     'francecentral': ['1', '2']
# }

# ------------------------------------------------------------------

for region in regions:

    resource_group              = infra_region.create_region_resource_group(region)
    region_vnet                 = infra_region.create_region_vnet(region, resource_group)

    region_nsg                  = infra_region.create_network_security_group(region, resource_group)
    region_nsg_rule_in_22       = infra_region.create_inbound_security_rule(region, resource_group, region_nsg, "SSH", 22, 100)
    region_nsg_rule_in_80       = infra_region.create_inbound_security_rule(region, resource_group, region_nsg, "HTTP", 80, 200)
    region_nsg_rule_out_22      = infra_region.create_outbound_security_rule(region, resource_group, region_nsg, "SSH-Out", 22, 300)
    region_nsg_rule_out80       = infra_region.create_outbound_security_rule(region, resource_group, region_nsg, "HTTP-Out", 80, 400)

    region_subnet_public        = infra_region.create_subnet_public(region, resource_group, region_vnet)
    region_subnet_private       = infra_region.create_subnet_private(region, resource_group, region_vnet)
    region_subnet_asso_public   = infra_region.associate_subnet_public_with_security_group(region, region_subnet_public, region_nsg)
    region_subnet_asso_private  = infra_region.associate_subnet_private_with_security_group(region, region_subnet_private, region_nsg)

    region_public_ip_alb        = infra_alb.create_public_ip_alb(region, resource_group)
    region_az_alb               = infra_alb.create_alb(region, resource_group, region_public_ip_alb)

# ------------------------------------------------------------------

    for az in azs[region]:
        region_az_public_ip     = infra_az.create_public_ip(region, resource_group, az)
        region_az_nat_gateway   = infra_az.create_nat_gateway(region, resource_group, az)
        region_az_nat_asso_sb   = infra_az.associate_nat_gateway_with_subnet(region, region_subnet_public, region_az_nat_gateway, az)
        region_az_nat_asso_pip  = infra_az.associate_nat_gateway_with_PIP(region, region_az_nat_gateway, region_az_public_ip, az)
        region_az_rt_private    = infra_az.create_route_table_private(region, resource_group, az)
        region_az_asso_public   = infra_az.associate_route_table_with_private_subnet(region, region_subnet_private, region_az_rt_private, az)

        region_az_backend_pool  = infra_alb.create_backend_pool(region, region_az_alb, az)
        region_az_alb_rule      = infra_alb.create_alb_rule(region, region_az_alb, region_az_backend_pool, az)

        region_az_nic           = infra_vm.create_nic_in_az(region, resource_group, region_subnet_private, region_az_backend_pool, az, region_nsg)
        region_az_vm            = infra_vm.create_vm_in_az(region, resource_group, region_az_nic, az)

# ------------------------------------------------------------------
