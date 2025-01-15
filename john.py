import math
import requests
#https://www.thebluealliance.com/api/v3/event/2025nyro/teams
#uTHeEfPigDp9huQCpLNkWK7FBQIb01Qrzvt4MAjh9z2WQDkrsvNE77ch6bOPvPb6

r = requests.get('https://www.thebluealliance.com/api/v3/event/2025nyro/teams', headers={'X-TBA-Auth-Key': 'uTHeEfPigDp9huQCpLNkWK7FBQIb01Qrzvt4MAjh9z2WQDkrsvNE77ch6bOPvPb6'})
print(r.json)