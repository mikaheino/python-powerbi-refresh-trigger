# Code to automatically refresh Power BI dataset
#
# Takes environment variables as inputs
# Meant to be triggered as Kubernetes task
#
#
# Version history
# 1.0 10.10.2019 Mika Heino - First working version using Kubernetes ENV and secrets
# 1.1 12.10.2019 Heino - Added environment parameters This package is for Power BI authentication
# 1.2 28.10.2019 Heino - Added URL and env validations, modified refresh logic


# This package is used for making the authentication
import adal
# This package is used for making HTTP REST API calls
import requests
# This package is used to get the environment variables from ADE
import os
# These packages are used to validate URL's
import urllib.request, urllib.error
# These packages are used for logging
import logging
logging.basicConfig(level=logging.WARNING)

def env_validator(env):
  # Check that the env exist
    if not isinstance(env, str):
      raise Exception("ADE environment variable is missing")
      logging.log_exception(error)
    if len(env) < 2:
      raise Exception("ADE environment variable is not correct")
      logging.log_exception(exception)
    else:
      pass

# URL's https://docs.microsoft.com/en-us/power-bi/developer/walkthrough-push-data-get-token
authority_url = 'https://login.windows.net/common'
resource_url = 'https://analysis.windows.net/powerbi/api'
env_validator(authority_url)
env_validator(resource_url)

# These values are given as ENV parameters in Kubernetes task description runtime_env value is defined by ADE automatically
# if the CUSTOM_ENVIROMENT_VARIABLES -package is used and referenced in the Load Step
runtime_env = os.getenv('RUNTIME_ENV')
client_id = os.getenv('CLIENT_ID')
env_validator(runtime_env)
env_validator(client_id)

# These username and password variables are stored in Kubernetes secrets store in Dagger namespace and they contain the password for user which has enough rights to make Power BI dataset refreshes in the CLIENT$
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
env_validator(username)
env_validator(password)

# As we have separate enviroments for DEV, UAT and PROD, we need to have separate environment variables for each environment.
# These are used based on the RUNTIME_ENV parameter e.g. if RUNTIME_ENV is DEV then we use DEV_PBI_GROUP_ID and DEV_PBI_DATASET_ID values even if UAT_PBI_GROUP_ID or PROD_PBI_GROUP_ID
# would contain values
dev_group_id = os.getenv('DEV_PBI_GROUP_ID')
dev_dataset_id = os.getenv('DEV_PBI_DATASET_ID')

uat_group_id = os.getenv('UAT_PBI_GROUP_ID')
uat_dataset_id = os.getenv('UAT_PBI_DATASET_ID')

prod_group_id = os.getenv('PROD_PBI_GROUP_ID')
prod_dataset_id = os.getenv('PROD_PBI_DATASET_ID')

context = adal.AuthenticationContext(authority=authority_url,
                                         validate_authority=True,
                                         api_version=None)

token = context.acquire_token_with_username_password(resource=resource_url,
                                                         client_id=client_id,
                                                         username=username,
                                                         password=password)

access_token = token.get('accessToken')


def refresh_pbi(group_id, dataset_id, access_token):
  refresh_url = 'https://api.powerbi.com/v1.0/myorg/groups/' + group_id + '/datasets/' + dataset_id + '/refreshes'
  header = {'Authorization': 'Bearer {}'.format(access_token)}
  r = requests.post(url=refresh_url, headers=header)
  r.raise_for_status()

# Depending on the ADE runtime environment, a separate refresh URL is used
if runtime_env == 'dev':
   if len(dev_group_id) < 2:
     # Do not do anything
     # ...
     pass
   else:
     refresh_pbi(group_id=dev_group_id,dataset_id=dev_dataset_id,access_token=access_token)
elif runtime_env == 'uat':
       if len(uat_group_id) < 2:
         # Do not do anything
         # ...
         pass
       else:
         refresh_pbi(group_id=uat_group_id,dataset_id=uat_dataset_id,access_token=access_token)
elif runtime_env == 'prod':
       if len(prod_group_id) < 2:
         # Do not do anything
         # ...
         pass
       else:
         refresh_pbi(group_id=prod_group_id,dataset_id=prod_dataset_id,access_token=access_token)
else:
       raise Exception('Environment should be DEV, UAT or PROD')
