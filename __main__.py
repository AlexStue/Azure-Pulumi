import pulumi
import infra_region
import infra_region_az
import infra_vm
import infra_vm_customscript

# Define global variables like regions and AZs
regions = ['germanywestcentral',
           'francecentral']
azs = {
    'germanywestcentral': ['1', '2'],
    'francecentral': ['1', '2']
}

# ------------------------------------------------------------------

for region in regions:

    resource_group  = infra_region.create_region_resource_group(region)
    region_vnet     = infra_region.create_region_vnet(region, resource_group)
    #region_alb      = infra_region.create_region_alb(region, resource_group)

for region in regions:
    for az in azs[region]:
        region_az_subnet_public= infra_region_az.create_az_subnet_public(region, resource_group, az, region_vnet)


# ------------------------------------------------------------------

""" 
# For each region, call the AZ-specific infrastructure
for region in regions:
    for az in azs[region]:
        az_infrastructure.create_az_resources(region, az)

# Create VMs using custom scripts in each AZ
for region in regions:
    for az in azs[region]:
        vm_infrastructure.create_vm(region, az)
        vm_custom_script.deploy_custom_script(region, az)
 """

# ------------------------------------------------------------------

