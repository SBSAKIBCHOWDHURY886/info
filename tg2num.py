from flask import Flask, jsonify
from telethon import TelegramClient
from telethon.tl.functions.users import GetFullUserRequest
import asyncio
import requests
import threading

app = Flask(__name__)

# CONFIGURATION
BOT_TOKEN = "8321486632:AAF5vfg0vnIUIlVOLvK1q9cVlK0MRuNgNRI"
API_ID = 25516423
API_HASH = "a86a8202eeb28dd33f3c4d8b5daba3cc"
API_URL = "https://devil.elementfx.com/api.php?key=DEVIL&type=tg_number&term="

# Initialize Client
client = TelegramClient('bot_session', API_ID, API_HASH)

def run_async_task(coro):
    """Flask এর ভেতরে Async ফাংশন রান করার জন্য Helper"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

@app.route('/user/<username>')
def user_data(username):
    try:
        if not username.startswith('@'):
            username = '@' + username
        
        async def fetch_data():
            # Ensure client is connected
            if not client.is_connected():
                await client.start(bot_token=BOT_TOKEN)
            
            entity = await client.get_entity(username)
            full = await client(GetFullUserRequest(entity.id))
            
            data = {
                "success": True,
                "username": f"@{entity.username}",
                "user_id": entity.id,
                "first_name": getattr(entity, 'first_name', 'N/A'),
                "bio": getattr(full.full_user, 'about', 'N/A'),
                "is_bot": entity.bot,
                "status": str(entity.status) if hasattr(entity, 'status') else "N/A"
            }
            
            # API Call
            try:
                api_res = requests.get(API_URL + str(entity.id), timeout=5).json()
                if api_res.get("success"):
                    result = api_res.get("result", {})
                    data.update({"number": result.get("number", "N/A")})
                else:
                    data["number"] = "Not found"
            except:
                data["number"] = "API error"
            
            return data

        final_data = run_async_task(fetch_data())
        return jsonify(final_data)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 404

if __name__ == '__main__':
    print("🚀 Server started on port 40855...")
    app.run(host='0.0.0.0', port=40855)
