# Code to automatically refresh Power BI dataset
#
# Version history
# 1.0 10.10.2019 Mika Heino - First working version using Kubernetes ENV and secrets
# 1.1 12.10.2019 Heino - Added environment parameters
# 1.2 12.10.2019 Heino - Added possibility to wait until refresh is done and send an MS Teams message once done

# This package is for Power BI authentication
import adal
# This package is used for making HTTP REST API calls
import requests
# This package is used to get the environment variables from ADE
import os
# This package is used to connect to Microsoft Teams
import pymsteams

# URL's https://docs.microsoft.com/en-us/power-bi/developer/walkthrough-push-data-get-token
authority_url = 'https://login.windows.net/common'
resource_url = 'https://analysis.windows.net/powerbi/api'

# These values are given as ENV parameters in Kubernetes task description
# runtime_env value is defined by ADE automatically if the CUSTOM_ENVIROMENT_VARIABLES -package is used
# and referenced in the Load Step
runtime_env = os.environ['RUNTIME_ENV']
wait_for_finish = os.environ['WAIT_FOR_FINISH']
client_id = os.environ['CLIENT_ID']
# As we have separate enviroments for DEV, UAT and PROD, we need to have separate environment variables
# for each environment. These are used based on the RUNTIME_ENV parameter e.g. if RUNTIME_ENV is DEV
# then we use DEV_PBI_GROUP_ID and DEV_PBI_DATASET_ID values even if UAT_PBI_GROUP_ID or PROD_PBI_GROUP_ID
# would contain values
dev_group_id = os.environ['DEV_PBI_GROUP_ID']
dev_dataset_id = os.environ['DEV_PBI_DATASET_ID']
uat_group_id = os.environ['UAT_PBI_GROUP_ID']
uat_dataset_id = os.environ['UAT_PBI_DATASET_ID']
prod_group_id = os.environ['PROD_PBI_GROUP_ID']
prod_dataset_id = os.environ['PROD_PBI_DATASET_ID']
# These values define the Webhook for Microsoft Teams
# You can define separate webhooks per environment or channel
dev_ms_teams_webhook = os.environ['DEV_MS_TEAMS_CHANNEL_WEBHOOK']
uat_ms_teams_webhook = os.environ['UAT_MS_TEAMS_CHANNEL_WEBHOOK']
prod_ms_teams_webhook = os.environ['PROD_MS_TEAMS_CHANNEL_WEBHOOK']
# These values define how the Microsoft Teams message looks like.
# You can optionally add weblink for the Power BI dashboard as part of the message in the MS_WEBLINK
ms_teams_title = os.environ['MS_TEAMS_TITLE']
ms_teams_text = os.environ['MS_TEAMS_TEXT']
ms_teams_link_button = os.environ['MS_WEBLINK']
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

# If the user has selected that he want's to wait until Power BI refresh is done, following code is executed
# Code will check first if wait_for_finish value is YES and after that what is the correct runtime where
# to execute the status check
# Status check will check latest status of report refresh (it will give only one value)
# Status check should reply that report refresh is done by ViaApi and status is either "In Progress" or "Done"
if wait_for_finish == 'YES':
       if runtime_env == 'dev':
              status_url = 'https://api.powerbi.com/v1.0/myorg/groups/' + dev_group_id + '/datasets/' + dev_dataset_id + '/refreshes?$top=1'
              TeamsMessage = pymsteams.connectorcard(dev_ms_teams_webhook)
       elif runtime_env == 'uat':
              status_url = 'https://api.powerbi.com/v1.0/myorg/groups/' + uat_group_id + '/datasets/' + uat_dataset_id + '/refreshes?$top=1'
              TeamsMessage = pymsteams.connectorcard(uat_ms_teams_webhook)
       elif runtime_env == 'prod':
              status_url = 'https://api.powerbi.com/v1.0/myorg/groups/' + prod_group_id + '/datasets/' + prod_dataset_id + '/refreshes?$top=1'
              TeamsMessage = pymsteams.connectorcard(prod_ms_teams_webhook)
       else: 
              raise Exception('Environment should be DEV, UAT or PROD')
       
# This loop will check the status check until the reply is "Done". Otherwise it will sleep for 60 seconds
       do while r.request.get(url=status_url, headers=header) != 200
              wait 5 sec
              TeamsMessage.title(ms_teams_title)
              TeamsMessage.text(ms_teams_text)
              TeamsMessage.addLinkButton(ms_teams_link_button)
              TeamsMessage.send()
else:
       r.raise_for_status()