import pulumi
from pulumi_azure_native import resources, network

def create_region_resource_group(region):
    resource_group = resources.ResourceGroup(
        f"rg-{region}-",
        location=region
    )
    return resource_group

def create_region_vnet(region, resource_group):
    vnet = network.VirtualNetwork(
        f"vnet-{region}-",
        resource_group_name=resource_group.name,
        location=region,
        #address_space=["10.0.0.0/16"],
        address_space={"addressPrefixes": ["10.0.0.0/16"]},

    )
    return vnet

def create_region_alb(region, resource_group):
    alb = network.ApplicationGateway(
        f"ALB-{region}-",
        resource_group_name=resource_group.name,
        location=region,
        # other ALB parameters
    )
    return alb
