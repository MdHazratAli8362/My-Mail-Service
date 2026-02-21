import asyncio
import re
from fastapi import FastAPI, Request
from pyrogram import Client
from pyrogram.raw.functions.contacts import Block, Unblock
from typing import Optional

app = FastAPI()

SESSIONS = {
    "opporeno5": "BQHf1MIAHbRepmYFQW6qUqyAd1Oc00oZCkBuYRo7KfGRIdlZbjpHgT8ons7ppQVV8L81cxSB3MPjtxqtU58i87xoABOt_Lx8sFPWVU-t8Z4wqwDaPV-cSoseCtdwI04BeM0-xngQndlAdgesY8PxvE5fR1KdwXSVegzbehcgel59Z2RBh6YkIMZ1Bxl9DHZCzIAcM7_HxKtWl4jGOSEG7Rz2mErwaB1vDkaHJ3-hd3xo4M6ixLDAKKpAhYhNXJ2bUnXZWvnT6fsdEV4rGdWl7J0Q5D5RT4cHVKUpLSBvh5TZBpRJnVsqMz7G-4Ft-sgOrSAZKySb69WjYN-H9M6gap3ns2rGXgAAAAHB_aesAA",
    "realme9i": "BQHZbIYAnBTk6nSU367kmw-9MUkpveck7ukSk96v8Xldk02rcjBlDf7cxuWx1z_tMtdCdl71qvFoUD1rAHTQCZ1uzr-cJ-WAQrOEJZMUNUeQaNWUhP_xW-Be4blWZfUmPWvPZY4SznC86cWxNx0Lt0JSMB_VgzGD6YBOc3R2gzHXM4kfvJN5dE3io5zJvlNdSADL09XaC0nSY6QQT_lnhMX2JlZ_7jrj2etyv-u9hC8IIfLLSp8nQNr-HjHW0aQBeROzIsnZY-Qda8ngHk9jstb10XhClV7VfoG8bH8Pib-rRMqh6JBnEOpQDqqt2ZGgwVILhhgrusNKaV1s6aLNIisxcEiC9wAAAAHGSfFsAA",
    "realme12xblack": "BQJeq5cAmXBe7e0JCJ4haAyIXUR0iZhfbeGGJMrqupWODDCpn2W5m-feF98A63WaMLtn3Gnj_nD8D7_35K-QJy7cyT-eY9OoWp1cJbRLghzOk-Rn63EUwAxFzxY4KA7r77xQy54u7YnYtuZyNRI_0Z6pb-4nIxh91G0TOsqmCaaYHkbUJP69T1qU5vRjxSAxKeYYIOa0QzONk97Dnj-jJVK7khMu99EyyxbrhF-GtesoZ6jXPW0begLPB0lctUzR9FV3oqfkdGzXio6oq3wcT87jEs98F9r1XzKdGt4PFLXTZ2En4vdfBVMohRf13uSkgSn5fLRof62GNo8UKDnrmocCI2PD0QAAAAHXiatwAA",
    "realme12xgreen": "BQGe9EQAuxrSnXaK0oXbupifSTcY64EY3rujli4Eeb--_YPf5elEqQK81CWR6k8sHZhWJ8n1pu2VS9XFbZUsz1-wbzivz3cUChx_9etIPaGsZXxjosLEFaIe-ucK8jboAFXv0V-aYj54fZ2Vb5cG5Ws0K50pc81AXr6YvGqtztSqobaHvp9_KOersbxWlGDDfx-oU9jXiEv79r0QSM3qr5v0kQyLg7CVMiOIC3QWJUdGNng__fdHlPDIliO0lkOLMlFyExXpAX5i9dXhSD_26NjDzi4Qzsfp8_d8Ylt1tf7W1aqTDBamNPljM6rewTOOisy76jdQpN0swjID3W_zYQVwyZVNaAAAAAGz3hZHAA",
    "infinix": "BQHq2CUAVOPZtd9pzolN-CBn8HBCyeoPSn-BdwDklApS7WjyXBXc2USjg62FXZ4OK1Hr7XPXInAPGt4hyhoRhA4P_ebQChbXhf6DKvdzUfBiSOk6Ze2U23WGaKeNZnIAyZRJKV6POqTpDHMHTYeRqexIR_qqgWb1bP6j1MR8KMRix2L42pDtkQSaLHu8evNGoShato79zg-JVFS318pZVTINVeVFZLA31IclbxUOojAIIGH1XQkYecLqWpXha6fuq0Y6xFPzl-i-hNbo_Y1B9l5kYr-EAJCGW8QxSrHUJU0nRLFGOhPBf4KDxefvqshR_4bFPn6tIGIqiXaNae5RnW0W1VzjOQAAAAFFkrtfAA"
}

TARGET_BOT = "easyfarmerbux_bot"
clients = {}


# --- ১. বটের মুখ বন্ধ/খোলার মাস্টার ফাংশন ---
async def set_bot_status(client, status: str):
    try:
        peer = await client.resolve_peer(TARGET_BOT)
        if status == "block":
            await client.invoke(Block(id=peer))
        else:
            await client.invoke(Unblock(id=peer))
    except Exception as e:
        print(f"Status Error: {e}")


async def get_client(phone_name: str):
    if phone_name not in SESSIONS:
        return None
    if phone_name not in clients:
        client = Client(f"account_{phone_name}", session_string=SESSIONS[phone_name], in_memory=True)
        await client.start()
        clients[phone_name] = client
    return clients[phone_name]


async def click_or_send(client, partial_text):
    # ইন্টারফেস চেক করার সময় লিমিট ১-ই যথেষ্ট
    async for message in client.get_chat_history(TARGET_BOT, limit=1):
        if message.reply_markup:
            if hasattr(message.reply_markup, 'inline_keyboard'):
                for row in message.reply_markup.inline_keyboard:
                    for button in row:
                        if partial_text in getattr(button, 'text', ""):
                            await message.click(button.text)
                            return message.id
            elif hasattr(message.reply_markup, 'keyboard'):
                for row in message.reply_markup.keyboard:
                    for button in row:
                        btn_label = button if isinstance(button, str) else getattr(button, 'text', "")
                        if partial_text in btn_label:
                            sent = await client.send_message(TARGET_BOT, btn_label)
                            return sent.id
    sent = await client.send_message(TARGET_BOT, partial_text)
    return sent.id


async def reset_state(client):
    await set_bot_status(client, "unblock")  # রিসেট করার সময় আগে আনব্লক
    max_tries = 2
    for i in range(max_tries):
        async for message in client.get_chat_history(TARGET_BOT, limit=1):
            all_buttons = []
            if message.reply_markup:
                if hasattr(message.reply_markup, 'inline_keyboard'):
                    for row in message.reply_markup.inline_keyboard:
                        for btn in row: all_buttons.append(btn.text)
                elif hasattr(message.reply_markup, 'keyboard'):
                    for row in message.reply_markup.keyboard:
                        for btn in row:
                            all_buttons.append(btn if isinstance(btn, str) else btn.text)

            if any("Tasks" in b for b in all_buttons): return
            if any("Cancel" in b for b in all_buttons):
                await click_or_send(client, "❌ Cancel")
                await asyncio.sleep(1.5)
                continue
            if any("Return to main menu" in b for b in all_buttons):
                await click_or_send(client, "⬅️ Return to main menu")
                await asyncio.sleep(1.5)
                continue

            text = (message.text or message.caption or "").lower()
            if "invalid" in text or "time's up" in text or "searching" in text or not message.reply_markup:
                await client.send_message(TARGET_BOT, "/start")
                await asyncio.sleep(1.5)

    await client.send_message(TARGET_BOT, "/start")
    await asyncio.sleep(1.5)


@app.api_route("/exec", methods=["GET", "POST"])
async def execute_command(cmd: str, phone: str, request: Request):
    try:
        client = await get_client(phone)
        if not client: return f"Device : '{phone}' Not Found!"

        body_bytes = await request.body()
        extra = body_bytes.decode("utf-8") if body_bytes else None

        # --- ২. মেইল/ডাটা পাওয়ার পর ব্লক করা ---
        if cmd == "get_mail" or cmd == "get_full_data":
            await reset_state(client)
            await click_or_send(client, "📋 Tasks")
            await asyncio.sleep(1.5)
            await click_or_send(client, "Create Inst")
            await asyncio.sleep(1.5)
            marker_id = await click_or_send(client, "▶️ Start")

            start_time = asyncio.get_event_loop().time()
            res = None
            while (asyncio.get_event_loop().time() - start_time) < 40:
                # ডাইনামিক চেক: marker_id এর পরের সব মেসেজ দেখবে
                async for m in client.get_chat_history(TARGET_BOT, limit=50):
                    if m.id > marker_id:
                        text = m.text or m.caption or ""
                        if cmd == "get_mail":
                            match = re.search(r"Email:\s*([\w\.-]+@[\w\.-]+)", text)
                            if match: res = match.group(1); break
                        else:
                            if "First name:" in text:
                                res = {
                                    "full_name": re.search(r"First name:\s*(.*)", text).group(1).strip() if re.search(
                                        r"First name:\s*(.*)", text) else "",
                                    "username": re.search(r"Login:\s*(.*)", text).group(1).strip() if re.search(
                                        r"Login:\s*(.*)", text) else "",
                                    "password": re.search(r"Password:\s*(.*)", text).group(1).strip() if re.search(
                                        r"Password:\s*(.*)", text) else "",
                                    "email": re.search(r"Email:\s*([\w\.-]+@[\w\.-]+)", text).group(
                                        1).strip() if re.search(r"Email:\s*([\w\.-]+@[\w\.-]+)", text) else ""
                                }
                                break
                if res: break
                await asyncio.sleep(4)

            if res:
                await set_bot_status(client, "block")  # ডাটা পেলেই সালা ব্লক
                return res
            return "Data Not Found"

        # --- ৩. ওটিপি এবং টু-এফএ লজিক (Dynamic Tracking + Unblock/Block) ---
        elif cmd in ["get_otp", "get_just_otp", "get_two_fa"]:
            await set_bot_status(client, "unblock")  # আগে মুখ খোল সালা
            await asyncio.sleep(1)

            if cmd == "get_two_fa":
                if not extra: return "Error: Two-FA Key Missing!"
                msg_sent = await client.send_message(TARGET_BOT, extra)
                marker_id = msg_sent.id
            else:
                marker_id = await click_or_send(client, "📥 Get code")

            start_time = asyncio.get_event_loop().time()
            otp_res = None
            while (asyncio.get_event_loop().time() - start_time) < 60:
                # লিমিট ৫০ করে দিলাম যাতে জমে থাকা মেসেজ মিস না হয়
                async for m in client.get_chat_history(TARGET_BOT, limit=50):
                    if m.id > marker_id:
                        text = m.text or m.caption or ""
                        # ওটিপি অথবা টু-এফএ কন্ডিশন চেক
                        if cmd == "get_two_fa":
                            if "Your one-time code is:" in text:
                                match = re.search(r"(\d{6})", text)
                                if match: otp_res = match.group(1); break
                        else:
                            match = re.search(r"(\d{6})", text)
                            if match: otp_res = match.group(1); break
                if otp_res: break
                await asyncio.sleep(4)

            if otp_res:
                if cmd == "get_otp":
                    await asyncio.sleep(1);
                    await click_or_send(client, "❌ Cancel")
                await set_bot_status(client, "block")  # ওটিপি পাওয়ার পর আবার ব্লক
                return otp_res
            return "Timeout"

        elif cmd == "account_done":
            await set_bot_status(client, "unblock")
            await asyncio.sleep(1)
            await click_or_send(client, "✅ Account registered")
            # একাউন্ট ডান হলে আর ব্লক করার দরকার নাই, পরের বার কাজ শুরুর সময় অটো হবে
            return "Account Done"

        else:
            await click_or_send(client, cmd)
            return f"Command Sent: {cmd}"

    except Exception as e:
        return f"Error: {str(e)}"


@app.on_event("shutdown")
async def shutdown():
    for client in clients.values():
        await client.stop()
