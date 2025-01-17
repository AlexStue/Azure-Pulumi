import pulumi
import pulumi_azure as azure

""" 
- create_public_ip_alb
- create_alb
- create_backend_pool
- create_alb_rule
"""

# ------------------------------------------------------------------

def create_public_ip_alb(region, resource_group,):
    public_ip_alb = azure.network.PublicIp(
        f"7-PIP-ALB-{region[:3]}_",
        resource_group_name=resource_group.name,
        location=region,
        sku="Standard",
        allocation_method="Static"
    )
    return public_ip_alb

def create_alb(region, resource_group, region_public_ip_alb):
    alb = azure.lb.LoadBalancer(
        f"7-ALB-{region[:3]}_",
        resource_group_name=resource_group.name,
        location=region,
        sku="Standard",
        frontend_ip_configurations=[{
            "name": "frontend-ip",
            "public_ip_address_id": region_public_ip_alb.id,
        }]
    )
    return alb

def create_backend_pool(region, alb, az):
    backend_pool = azure.lb.BackendAddressPool(
        f"7-BcEnPo-{region[:3]}-AZ{az}_",
        loadbalancer_id=alb.id
    )
    return backend_pool

def create_alb_rule(region, alb, backend_pool, az):
    alb_rule = azure.lb.Rule(
        f"7-ALB-Ru-{region[:3]}-AZ{az}_",
        loadbalancer_id=alb.id,
        backend_address_pool_ids=[backend_pool.id],
        frontend_ip_configuration_name="frontend-ip",
        protocol="Tcp",
        frontend_port=80,
        backend_port=80,
        enable_floating_ip=False
    )
    return alb_rule

# ------------------------------------------------------------------
