import base64
import pulumi
import pulumi_azure_native as azure_native
from pulumi_azure_native import compute, network


# ------------------------------------------------------------------

def create_nic_in_az(region, resource_group, region_subnet_private, backend_pool, az, nsg):
    nic = azure_native.network.NetworkInterface(
        f"nic-{region}-AZ{az}-",
        resource_group_name=resource_group.name,
        location=region,
        #availability_zone=az,
        ip_configurations=[{
            "name": "ipconfig1",
            "subnet": {
                "id": region_subnet_private
            },
            "private_ip_address_allocation": "Dynamic",
                        "loadBalancerBackendAddressPools": [{
                "id": backend_pool.id
            }]
        }],
        network_security_group={
            "id": nsg.id
        }
    )
    return nic
def create_vm_in_az(region, resource_group, region_az_nic, az):
    script = f"""#!/bin/bash
exec > /tmp/startup.log 2>&1
set -x
sudo apt update
sudo apt install apache2 -y
echo "Hi, I'm an Azure Instance in Region {region} in AZ {az}" | sudo tee /var/www/html/index.html
sudo systemctl start apache2
sudo systemctl enable apache2
"""

    # ✅ Base64 encode the script (Azure requires this format for `custom_data`)
    encoded_script = base64.b64encode(script.encode("utf-8")).decode("utf-8")

    virtual_machine = azure_native.compute.VirtualMachine(
        f"vm-{region}-{az}",
        resource_group_name=resource_group.name,
        location=region,
        zones=[az],  # Ensure it's a list
        hardware_profile={"vm_size": "Standard_B1s"},
        network_profile={
            "network_interfaces": [{"id": region_az_nic.id}]
        },
        storage_profile={
            "image_reference": {
                "publisher": "Canonical",
                "offer": "0001-com-ubuntu-server-jammy",
                "sku": "22_04-lts",
                "version": "latest",
            },
            "os_disk": {
                "name": "myosdisk1",
                "caching": "ReadWrite",
                "create_option": "FromImage",
                "managed_disk": {"storage_account_type": "Standard_LRS"},
                "disk_size_gb": 30,
            }
        },
        os_profile={
            "computer_name": f"vm-{region}-{az}",
            "admin_username": "testadmin",
            "admin_password": "Password1234!",
            "custom_data": encoded_script,  # ✅ Base64-encoded script
            "linux_configuration": {  # ✅ Corrected key name
                "disable_password_authentication": False,
            }
        }
    )

    return virtual_machine
# ------------------------------------------------------------------
