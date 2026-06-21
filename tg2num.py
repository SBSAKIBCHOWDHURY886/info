from flask import Flask, jsonify
from telethon import TelegramClient
from telethon.tl.functions.users import GetFullUserRequest
import asyncio
import requests

app = Flask(__name__)

# DETAILS
BOT_TOKEN = "8321486632:AAF5vfg0vnIUIlVOLvK1q9cVlK0MRuNgNRI"
API_ID = 25516423
API_HASH = "a86a8202eeb28dd33f3c4d8b5daba3cc"

API_URL = "https://devil.elementfx.com/api.php?key=DEVIL&type=tg_number&term="

print("⏳ Bot start ho raha hai...")

async def start_bot():
    client = TelegramClient('bot_session', API_ID, API_HASH)
    await client.start(bot_token=BOT_TOKEN)
    print("✅ Bot ready!")
    return client

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
bot = loop.run_until_complete(start_bot())


@app.route('/user/<path:username>')
def user_data(username):
    try:
        if not username.startswith('@'):
            username = '@' + username

        async def get_all():
            entity = await bot.get_entity(username)
            full = await bot(GetFullUserRequest(entity.id))

            # 🔥 TELETHON DATA
            data = {
                "success": True,
                "username": f"@{entity.username}",
                "user_id": entity.id,  # 👈 chat id included
                "access_hash": entity.access_hash,
                "first_name": getattr(entity, 'first_name', 'N/A'),
                "last_name": getattr(entity, 'last_name', 'N/A'),
                "phone": getattr(entity, 'phone', 'N/A'),
                "bio": getattr(full.full_user, 'about', 'N/A') if full else "N/A",
                "common_chats": getattr(full.full_user, 'common_chats_count', 0) if full else 0,
                "is_bot": entity.bot,
                "is_verified": entity.verified,
                "is_scam": entity.scam,
                "is_fake": entity.fake,
                "is_support": entity.support,
                "status": str(entity.status) if hasattr(entity, 'status') else "N/A"
            }

            # 🔥 API CALL (number fetch using chat_id)
            try:
                api_res = requests.get(API_URL + str(entity.id), timeout=5).json()

                if api_res.get("success"):
                    result = api_res.get("result", {})

                    data.update({
                        "number": result.get("number"),
                        "country": result.get("country"),
                        "country_code": result.get("country_code"),
                        "api_msg": api_res.get("msg", "ok")
                    })
                else:
                    data["number"] = "Not found"

            except Exception as e:
                data["number"] = "API error"

            return data

        final = loop.run_until_complete(get_all())
        return jsonify(final)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)