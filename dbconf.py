import os

dbhost = os.environ.get('DBHOST')
dbport = int(os.environ.get('DBPORT'))
dbuser = os.environ.get('DBUSER')
dbpass = os.environ.get('DBPASS')
dbname = os.environ.get('DBNAME')
appsecret = os.environ.get('APPSECRET')
twitchClientId = os.environ.get('TWITCHCLIENTID')
twitchSecret = os.environ.get('TWITCHSECRET')