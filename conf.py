import os


dbhost = os.environ.get('DBHOST')
dbport = int(os.environ.get('DBPORT'))
dbuser = os.environ.get('DBUSER')
dbpass = os.environ.get('DBPASS')
dbname = os.environ.get('DBNAME')
appsecret = os.environ.get('APPSECRET')
twitchClientId = os.environ.get('TWITCHCLIENTID')
twitchSecret = os.environ.get('TWITCHSECRET')
slClientId = os.environ.get('SLCLIENTID')
slSecret = os.environ.get('SLSECRET')
scheme = os.environ.get('SCHEME')
VER = '092521.0242'

