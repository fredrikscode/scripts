import sys
import requests
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

ntfy_url = config.get('ntfy','url')
ntfy_token = config.get('ntfy','token')

requests.post(ntfy_url,
    data=f"{sys.argv[2]}",
    headers={
        "Authorization": f"Bearer {ntfy_token}",
        "Title": "Deluge added a torrent",
        "Priority": "default",
        "Tags": "file_folder"
    }
)