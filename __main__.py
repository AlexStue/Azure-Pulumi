import pulumi
from pulumi_azure_native import resources, network, compute

# Resource Group
resource_group = resources.ResourceGroup("resourceGroup-pulumi-", location="germanywestcentral")

# Virtual Network
vnet = network.VirtualNetwork("vnet-pulumi-",
    resource_group_name=resource_group.name,
    location=resource_group.location,
    address_space={"addressPrefixes": ["10.0.0.0/16"]})

# Subnet
subnet = network.Subnet("subnet",
    resource_group_name=resource_group.name,
    virtual_network_name=vnet.name,
    address_prefix="10.0.1.0/24")

# Public IP
public_ip = network.PublicIPAddress("publicIp",
    resource_group_name=resource_group.name,
    location=resource_group.location,
    public_ip_allocation_method="Dynamic")

# Network Interface
nic = network.NetworkInterface("nic",
    resource_group_name=resource_group.name,
    location=resource_group.location,
    ip_configurations=[{
        "name": "ipConfig",
        "subnet": {"id": subnet.id},
        "private_ip_allocation_method": "Dynamic",
        "public_ip_address": {"id": public_ip.id},
    }])

"""

# Virtual Machine
vm = compute.VirtualMachine("vm",
    resource_group_name=resource_group.name,
    location=resource_group.location,
    network_profile={"network_interfaces": [{"id": nic.id}]},
    hardware_profile={"vm_size": "Standard_B1ls"},
    os_profile={
        "computer_name": "myVM",
        "admin_username": "azureuser",
        "admin_password": "P@ssw0rd123!"
    },
    storage_profile={
        "image_reference": {
            "publisher": "Canonical",
            "offer": "UbuntuServer",
            "sku": "18.04-LTS",
            "version": "latest",
        },
        "os_disk": {
            "caching": "ReadWrite",
            "managed_disk": {"storage_account_type": "Standard_LRS"},
            "name": "myOsDisk",
            "create_option": "FromImage",
        },
    })

# Custom Script to Deploy Website
script = """#!/bin/bash
# sudo apt update
# sudo apt install -y nginx
# echo "Hi, I am an Azure Instance created with Pulumi" | sudo tee /var/www/html/index.html
# sudo systemctl start nginx
"""

vm_extension = compute.VirtualMachineExtension("vmExtension",
    resource_group_name=resource_group.name,
    vm_name=vm.name,
    location=resource_group.location,
    publisher="Microsoft.Azure.Extensions",
    type="CustomScript",
    type_handler_version="2.0",
    settings={
        "fileUris": [],
        "commandToExecute": script,
    })

# Export the Public IP of the VM
pulumi.export("vm_public_ip", public_ip.ip_address)

"""

