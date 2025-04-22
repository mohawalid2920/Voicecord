import os
import sys
import json
import time
import requests
import websocket
from keep_alive import keep_alive

# قراءة المتغيرات من environment variables
usertoken = os.getenv("TOKEN")
guild_id = os.getenv("GUILD_ID")
channel_id = os.getenv("CHANNEL_ID")
status = os.getenv("STATUS", "online").lower()  # online/dnd/idle
SELF_MUTE = os.getenv("SELF_MUTE", "true").lower() == "true"
SELF_DEAF = os.getenv("SELF_DEAF", "false").lower() == "true"

if not usertoken:
    print("[ERROR] Please add a token inside Secrets.")
    sys.exit()

if not guild_id or not channel_id:
    print("[ERROR] GUILD_ID or CHANNEL_ID is missing.")
    sys.exit()

headers = {"Authorization": usertoken, "Content-Type": "application/json"}

validate = requests.get('https://canary.discordapp.com/api/v9/users/@me', headers=headers)
if validate.status_code != 200:
    print("[ERROR] Your token might be invalid. Please check it again.")
    sys.exit()

userinfo = validate.json()
username = userinfo["username"]
discriminator = userinfo["discriminator"]
userid = userinfo["id"]

def joiner(token, status):
    ws = websocket.create_connection('wss://gateway.discord.gg/?v=9&encoding=json')
    start = json.loads(ws.recv())
    heartbeat = start['d']['heartbeat_interval']

    auth = {
        "op": 2,
        "d": {
            "token": token,
            "properties": {
                "$os": "Windows 10",
                "$browser": "Google Chrome",
                "$device": "Windows"
            },
            "presence": {
                "status": status,
                "afk": False
            }
        }
    }

    vc = {
        "op": 4,
        "d": {
            "guild_id": guild_id,
            "channel_id": channel_id,
            "self_mute": SELF_MUTE,
            "self_deaf": SELF_DEAF
        }
    }

    ws.send(json.dumps(auth))
    ws.send(json.dumps(vc))
    time.sleep(heartbeat / 1000)
    ws.send(json.dumps({"op": 1, "d": None}))

def run_joiner():
    os.system("clear" if os.name == "posix" else "cls")
    print(f"Logged in as {username}#{discriminator} ({userid}).")
    while True:
        joiner(usertoken, status)
        time.sleep(30)

keep_alive()
run_joiner()
