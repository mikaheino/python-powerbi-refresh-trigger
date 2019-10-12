# Code to automatically refresh Power BI dataset
#
# Version history
# 1.0 10.10.2019  Mika Heino - First working version using Kubernetes ENV and secrets
# 1.1 12.10.2019 Heino - Added environment parameters

# This package is for Power BI authentication
import adal
# This package is used for making HTTP REST API calls
import requests
# This package is used to get the environment variables from ADE
import os

# URL's https://docs.microsoft.com/en-us/power-bi/developer/walkthrough-push-data-get-token
authority_url = 'https://login.windows.net/common'
resource_url = 'https://analysis.windows.net/powerbi/api'

# These values are given as ENV parameters in Kubernetes task description
# runtime_env value is defined by ADE automatically if the CUSTOM_ENVIROMENT_VARIABLES -package is used
# and referenced in the Load Step
runtime_env = os.environ['RUNTIME_ENV']
client_id = os.environ['CLIENT_ID']
# As we have separate enviroments for DEV, UAT and PROD, we need to have separate environment variables
# for each environment. These are used based on the RUNTIME_ENV parameter e.g. if RUNTIME_ENV is DEV
# then we use DEV_PBI_GROUP_ID and DEV_PBI_DATASET_ID values even if UAT_PBI_GROUP_ID or PROD_PBI_GROUP_ID
# would contain values
dev_group_id = os.environ['DEV_PBI_GROUP_ID']
dev_dataset_id = os.environ['DEV_PBI_DATASET_ID']
uat_group_id = os.environ['UAT_PBI_GROUP_ID']
uat_dataset_id = os.environ['UAT_PBI_DATASET_ID']
prod_dataset_id = os.environ['PROD_PBI_GROUP_ID']
prod_dataset_id = os.environ['PROD_PBI_DATASET_ID']
# These username and password variables are stored in Kubernetes secrets store in Dagger namespace
# and they contain the password for user which has enough rights to make Power BI dataset refreshes
# in the CLIENT_ID environment
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

# Depending on the ADE runtime environment, a separate refresh URL is used
if runtime_env == 'dev':
       refresh_url = 'https://api.powerbi.com/v1.0/myorg/groups/' + dev_group_id + '/datasets/' + dev_dataset_id + '/refreshes'
elif runtime_env == 'uat':
       refresh_url = 'https://api.powerbi.com/v1.0/myorg/groups/' + uat_group_id + '/datasets/' + uat_dataset_id + '/refreshes'
elif runtime_env == 'prod':
       refresh_url = 'https://api.powerbi.com/v1.0/myorg/groups/' + prod_group_id + '/datasets/' + prod_dataset_id + '/refreshes'
else: 
       raise Exception('Environment should be DEV, UAT or PROD')

header = {'Authorization': 'Bearer {}'.format(access_token)}

# Send the request with access token to Power BI
r = requests.post(url=refresh_url, headers=header)

r.raise_for_status()
