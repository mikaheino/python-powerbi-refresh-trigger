# Refresh given Power BI dataset using Docker and ADE

This repository contains code to refresh given Power BI dataset using Docker as ADE Load step on Azure

## Getting Started

Start by getting Azure AD account which can be used for automation and with having said that, this is not the most secure and the most beautiful code possible but it works. So if you're really keen on securing everything (this lacks MFA/Service Principal implementation) the solution might not be for you. Once you have that any server used for ADE updates, you are good to go.

![Code](657.jpg)

### Prerequisites

- Azure AD account with MFA disabled and enough access to refresh given Power BI dataset (user must have necessary Power BI Pro license)
- Server with necessary Docker and Azure tools installed. ADE Oracle Virtualbox solution should work, but this example uses ADE Docker tool version on deployment examples https://deus.solita.fi/Solita/projects/ade_community/repositories/ade-docker/tree/master
- Access to ADE Kubernetes cluster(s)
- Access to ADE Azure account(s)

### Obligatory prerequisites

- Modified to CONFIG_ENVIRONMENT_VARIABLES ADE Package which has environment variables for Kubernetes -cluster and Azure ADE accountname

### Installing

1) Create Kubernetes secrets to all necessary Kubernetes cluster in "dagger" namespace

```
root@0ba7075cb8a3:~/ade-installation-binaries/target/dev# sh setup-kubectl.sh
root@0ba7075cb8a3:~/ade-installation-binaries/target/dev# kubectl create secret generic pbi-api-secrets --from-literal=username='*****' --from-literal=password='*****' --namespace=dagger
```
2) Copy this repository
3) Deploy this image to desired to Kubernetes clusters


## Local testing before Kubernetes deployment

Docker container can be tested without Agile Data Engine by running the container directly without Kubernetes interaction.

1) Execute following command

```
docker run -e RUNTIME_ENV=env -e CLIENT_ID=client_id -e DEV_PBI_GROUP_ID=id1 -e DEV_PBI_DATASET_ID=id2 -e USERNAME='xxxx@xxx.com' -e PASSWORD='xxx' python-powerbi-anlasser4
```

## Deployment

1) Copy the given example of ade_load_step.json content into Agile Data Engine Publish -layer package in to Load Steps
2) Modify the contents of load steps to match your Power BI environment and dashboards
3) Change the Load Step type to Docker
4) Commit using normal ADE deployment model

## Checking results

Your can check the end results by 
1) Checking Power BI history
2) Executing following Python code (inside container or without). The end result should print result of latest refresh for given dataset.

```
import adal
import requests
import os

# URL's https://docs.microsoft.com/en-us/power-bi/developer/walkthrough-push-data-get-token
authority_url = 'https://login.windows.net/common'
resource_url = 'https://analysis.windows.net/powerbi/api'

# These values are given as ENV parameters in Kubernetes task description
client_id = os.environ['CLIENT_ID']
group_id = os.environ['PBI_GROUP_ID']
dataset_id = os.environ['PBI_DATASET_ID']
username = os.environ['USERNAME']
password = os.environ['PASSWORD']

context = adal.AuthenticationContext(authority=authority_url,
                                         validate_authority=True,
                                         api_version=None)
token = context.acquire_token_with_username_password(resource=resource_url,
                                                         client_id=client_id,
                                                         username=username,
                                                         password=password)
access_token = token.get('accessToken')

refresh_url = 'https://api.powerbi.com/v1.0/myorg/groups/' + group_id + '/datasets/' + dataset_id + '/refreshes?$top=1'

header = {'Authorization': 'Bearer {}'.format(access_token)}

r = requests.get(url=refresh_url, headers=header)

r.raise_for_status()

print(r.content)

```

## Built With

* Docker
* Python

## Contributing

Please contribute new versions into this code repository

## Versioning

This is version 1.0 with no support from original creator.

## Authors

* **Mika Heino** - *Initial work*

## Acknowledgments

* ADE team & Harri Pylkkänen
* Kaarel Korvemaa
* Omnistream creator for Power BI user requirements https://bitbucket.org/omnistream/powerbi-api-example/src/master/
