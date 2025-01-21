import pulumi
import pulumi_azure as azure
import infra_dev_network
import infra_dev_app

# ------------------------------------------------------------------

regions = ['germanywestcentral',
           'francecentral']

azs = {
    'germanywestcentral': ['1', '2'],
    'francecentral': ['1', '2']
    }

# ------------------------------------------------------------------

resource_groups = {}

for region in regions:
    resource_groups[region] = infra_dev_network.create_resource_group_region(region)

# ------------------------------------------------------------------

for region in regions:
    resource_group_region = resource_groups[region]

    # (region_vnet, region_nsg, region_az_subnets_private, region_backend_pool) = \
    #     infra_dev_network.create_region_network(region, resource_group_region, azs)

    #infra_dev_app.create_region_app(region, resource_group_region, region_az_subnets_private,region_nsg,region_backend_pool, azs[region])

# ------------------------------------------------------------------
