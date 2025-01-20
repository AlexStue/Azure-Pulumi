
DRAFT


Structure:

Subscription: My-Cloud  
├── Stack dev
│  ├── RG: dev-network  
│  │     ├── VNet  
│  │     ├── Subnets  
│  │     ├── Public IPs, Load Balancers  
│  ├── RG: dev-app  
│  │     ├── VMs  
│  │     ├── App Services  
│  │     ├── Databases  
├──Stack staging
│  ├── RG: stage-network  
│  ├── RG: stage-app  
├──Stack prod
│  ├── RG: prod-network  
│  ├── RG: prod-app  


First Start:

- read SubId:
- Create ResourceGroups:
  - 
  - 
- Build: Pulumi up


az group create --name MyResourceGroup --location germanywestcentral # francecentral
pulumi import azure-native:resources:ResourceGroup myResourceGroup /subscriptions/{subId}/resourceGroups/MyResourceGroup

-

pulumi login s3://my-bucket
pulumi login azblob://my-container
pulumi config set databasePassword mySuperSecretPassword --secret


pulumi stack init dev
pulumi stack init staging
pulumi stack init prod
pulumi stack ls
pulumi stack select dev
pulumi stack select staging
pulumi stack select prod

pulumi preview
pulumi up --yes
pulumi destroy --yes

pulumi stack rm dev

-
