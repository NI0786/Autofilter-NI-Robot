import re
import os
from os import environ, getenv
from Script import script 

id_pattern = re.compile(r'^.\d+$')

def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default


# Bot information
SESSION = environ.get('SESSION', 'NIXBOTZ')
API_ID = int(environ.get('API_ID', "25061703"))
API_HASH = environ.get('API_HASH', "744a017a9c53f3ab489ea0bfa0ffce3f")
BOT_TOKEN = environ.get('BOT_TOKEN', "")
TIMEZONE = environ.get("TIMEZONE", "Asia/Kolkata")

# Bot settings
CACHE_TIME = int(environ.get('CACHE_TIME', 300))
USE_CAPTION_FILTER = is_enabled((environ.get('USE_CAPTION_FILTER', 'True')), True)
PICS = (environ.get('PICS', 'https://telegra.ph/file/0ed351c8605c23e8cae79.jpg https://telegra.ph/file/6524270c008b60f81f30a.jpg https://telegra.ph/file/848ed57090fd5111ce64d.jpg https://telegra.ph/file/5fe959d96fcc33d1b9dc9.jpg https://telegra.ph/file/ec5f5a031b7826e28360c.jpg https://telegra.ph/file/aa4b77441bb41cfce12d7.jpg https://telegra.ph/file/00ed60e2c89d564d850ef.jpg https://telegra.ph/file/a5d518f6020976bc45264.jpg https://telegra.ph/file/650191ad1f813ca8f41cb.jpg https://telegra.ph/file/c6042704a1bc0a2b52996.jpg https://telegra.ph/file/9d68211fa9dcb208200be.jpg')).split()
WELCOME_VID = environ.get("WELCOME_VID", "https://telegra.ph/file/451f038b4e7c2ddd10dc0.mp4")

#premium imag
REFFER_PIC = environ.get('REFFER_PIC', 'https://graph.org/file/f75feb19aece0d4badefd.jpg')
PREMIUM_PIC = environ.get('SUBSCRIPTION', 'https://i.imghippo.com/files/wPdPK1726559453.jpg')
QR_CODE = environ.get('QR_CODE', 'https://graph.org/file/8bc2cc53e47180bc78c10.jpg') # Scanner Code image 
#refer time, or feffer count
REFERAL_TIME = int(environ.get('REFERAL_USER_TIME', "2592000")) # set in seconds | already seted 1 month premium
REFFER_POINT = int(environ.get('USER_POINT', "50")) # Set Referel point Count 
#premium Users Satuts
premium = environ.get('PREMIUM_LOGS', '-1002346559309')
PREMIUM_LOGS = int(premium) if premium and id_pattern.search(premium) else None
# lock file, set file limit 
FILE_LIMITE = int(environ.get('FILE_LIMITE', '100'))
SEND_ALL_LIMITE = int(environ.get('SEND_ALL_LIMITE', '100'))
LIMIT_MODE = is_enabled((environ.get('LIMIT_MODE', 'False')), False)

# Admins, Channels & Users
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '6899946963').split()]
OWNER_USER_NAME = environ.get("OWNER_USER_NAME", "IM_NISHANTT") # widout 👉 @
CHANNELS = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('CHANNELS', '').split()]
# post channel auto post new movie
POST_CHANNELS = list(map(int, (channel.strip() for channel in environ.get('POST_CHANNELS', '').split(','))))
AUTH_CHANNEL = int(environ.get('AUTH_CHANNEL', '-1002386346176'))
AUTH_REQ_CHANNEL = int(environ.get('AUTH_REQ_CHANNEL', '-1002386346176'))
NO_RESULTS_MSG = is_enabled((environ.get("NO_RESULTS_MSG", 'True')), False)

# MongoDB information
DATABASE_URI = environ.get('DATABASE_URI', "mongodb+srv://bipinmfp07:OmodwqrRcvV6lrV4@cluster0.2t7so.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DATABASE_NAME = environ.get('DATABASE_NAME', "Cluster0")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'telegram_files')

#stream link shortner
STREAM_SITE = (environ.get('STREAM_SITE', ''))
STREAM_API = (environ.get('STREAM_API', ''))
STREAM_HTO = (environ.get('STREAMHTO', 'https://t.me/'))
STREAM_MODE = is_enabled((environ.get('STREAM_MODE', "False")), False)


#verify site api and url
IS_VERIFY = is_enabled((environ.get('IS_VERIFY', 'False')), False)
VERIFY_IMG = environ.get("VERIFY_IMG", "")
VERIFY_URL = environ.get('VERIFY_URL', '')
VERIFY_API = (environ.get('VERIFY_API', ''))

TWO_VERIFY_GAP = int(environ.get('TWO_VERIFY_GAP', "600"))
VERIFY_URL2 = environ.get('VERIFY_URL2', '')
VERIFY_API2 = (environ.get('VERIFY_API2', ''))
 
THIRD_VERIFY_GAP = int(environ.get('THIRD_VERIFY_GAP', "600"))
VERIFY_URL3 = environ.get('VERIFY_URL3', '')
VERIFY_API3 = (environ.get('VERIFY_API3', ''))
 
TUTORIAL = environ.get('TUTORIAL', 'https://t.me/')
TUTORIAL2 = environ.get('TUTORIAL2', 'https://t.me/')
TUTORIAL3 = environ.get('TUTORIAL3', 'https://t.me/')

# auto files delete
AUTO_FILE_DELETE = is_enabled((environ.get('AUTO_FILE_DELETE', "True")), False)

DELETE_CHANNELS = [int(dch) if id_pattern.search(dch) else dch for dch in environ.get('DELETE_CHANNELS', '').split()]
MAX_B_TN = environ.get("MAX_B_TN", "7")
MAX_BTN = is_enabled((environ.get('MAX_BTN', "True")), True)
PORT = environ.get("PORT", "8080")
GRP_LNK = environ.get('GRP_LNK', 'https://t.me/Ni_Movie_Request_Group')
CHNL_LNK = environ.get('CHNL_LNK', 'https://t.me/Ni_Movies')
MSG_ALRT = environ.get('MSG_ALRT', 'Wʜᴀᴛ Aʀᴇ Yᴏᴜ Lᴏᴏᴋɪɴɢ Aᴛ ?')
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', "-1002377076025"))
GROUP_VERIFY_LOGS = int(environ.get('GROUP_VERIFY_LOGS', "-1002377076025")) # Group verify stats 
REQ_CHANNEL = int(environ.get('REQ_CHANNEL', "-1002377076025")) # movies request channel, else log channel
SUPPORT_CHAT = environ.get('SUPPORT_CHAT', 'Ni_Movies')
IMDB = is_enabled((environ.get('IMDB', "True")), True)
AUTO_FFILTER = is_enabled((environ.get('AUTO_FFILTER', "True")), True)
AUTO_DELETE = is_enabled((environ.get('AUTO_DELETE', "True")), True)
PM_FILTER = is_enabled((environ.get('PM_FILTER', "True")), False)

BUTTON_MODE = is_enabled((environ.get('BUTTON_MODE', "True")), True)
CUSTOM_FILE_CAPTION = environ.get("CUSTOM_FILE_CAPTION", f"{script.CAPTION}")
IMDB_TEMPLATE = environ.get("IMDB_TEMPLATE", f"{script.IMDB_TEMPLATE_TXT}")
LONG_IMDB_DESCRIPTION = is_enabled(environ.get("LONG_IMDB_DESCRIPTION", "False"), False)
SPELL_CHECK_REPLY = is_enabled(environ.get("SPELL_CHECK_REPLY", "True"), True)
MAX_LIST_ELM = environ.get("MAX_LIST_ELM", None)
INDEX_REQ_CHANNEL = int(environ.get('INDEX_REQ_CHANNEL', LOG_CHANNEL))
MELCOW_NEW_USERS = is_enabled((environ.get('MELCOW_NEW_USERS', "True")), True)

REACTION = ["🔥", "❤️", "😍", "⚡", "👍", "❤", "🔥", "🥰", "👏", "😁", "🎉", "🤩", "🙏", "👌", "🕊", "❤‍🔥", "⚡", "😇", "🤗", "😘", "🙊", "😎"]

# Online Stream and Download
STREAM_MODE = bool(environ.get('STREAM_MODE', True)) # Set True or False

# If Stream Mode Is True Then Fill All Required Variable, If False Then Don't Fill.
MULTI_CLIENT = False
SLEEP_THRESHOLD = int(environ.get('SLEEP_THRESHOLD', '60'))
PING_INTERVAL = int(environ.get("PING_INTERVAL", "1200"))  # 20 minutes
if 'DYNO' in environ:
    ON_HEROKU = True
else:
    ON_HEROKU = False
URL = environ.get("URL", "")

#----------------------------------------------------------------------👻👻👻👻👻👻👻---------------------------------------------------------------------------

# THANKS TO NISHANT
# CREDIT @IM_NISHANTT
# PLZ.. DON'T REMOVE THIS CREDIT
# CONTACT FOR DOUBTS ON TG - @IM_NISHANT

#--------------------------------------------------------------------------👻👻👻👻👻👻--------------------------------------------------------------------------
