from pulumi_azure_native import resources, network

def create_az_subnet_public(region, resource_group, az, region_vnet):

    public_subnet = network.Subnet(
        f"publicSubnet-{region}-{az}-",
        resource_group_name=resource_group.name,
        virtual_network_name=region_vnet.name,
        address_prefix="10.0.1.0/24",
    )
    return public_subnet