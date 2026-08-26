import os
import requests
from flask import Flask, request
from telebot import TeleBot, types

TOKEN = os.getenv("TOKEN", "8765687320:AAFvGLWCDbXSsRsGLmk80rKljgFSZY7fAio")
ADMIN_TELEGRAM_ID = int(os.getenv("ADMIN_TELEGRAM_ID", 7370944091))
# URL Tunnel dari Komputer Lokal Anda (akan diisi setelah Cloudflare Tunnel aktif di PC lokal)
LOCAL_AGENT_URL = os.getenv("LOCAL_AGENT_URL", "https://URL_TUNNEL_LOKAL_ANDA.trycloudflare.com")

bot = TeleBot(TOKEN)
server = Flask(__name__)

@bot.message_handler(commands=['start'])
def handle_start(message):
    if message.from_user.id != ADMIN_TELEGRAM_ID:
        return
    welcome_text = (
        f"🤖 **Halo Boss! Bot Cloud (Opsi 1) Aktif 24 Jam**\n\n"
        f"📌 **Format DP:** `/dp [nama_agen] [username_target] [jumlah]`\n"
        f"📌 **Format WD:** `/wd [nama_agen] [username_target] [jumlah]`\n\n"
        f"🚀 Perintah akan diteruskan otomatis ke Komputer Lokal."
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(commands=['stop'])
def handle_stop(message):
    if message.from_user.id != ADMIN_TELEGRAM_ID:
        return
    bot.reply_to(message, "🛑 **Bot cloud dihentikan.**", parse_mode="Markdown")

@bot.message_handler(commands=['dp', 'wd'])
def handle_actions(message):
    if message.from_user.id != ADMIN_TELEGRAM_ID:
        return

    try:
        command = message.text.split()[0].replace('/', '') # 'dp' atau 'wd'
        args = message.text.split()
        if len(args) < 4:
            bot.reply_to(message, f"❌ Format salah!\nGunakan: `/{command} [nama_agen] [username_target] [jumlah]`", parse_mode="Markdown")
            return
            
        agent_name = args[1]
        target_user = args[2]
        amount = args[3]
        
        bot.reply_to(message, f"⏳ Meneruskan perintah `{command.upper()}` ke komputer lokal...", parse_mode="Markdown")
        
        # Kirim data instruksi ke Komputer Lokal Anda via HTTP POST
        payload = {
            "action_type": command,
            "agent_name": agent_name,
            "target_username": target_user,
            "amount": amount
        }
        
        response = requests.post(f"{LOCAL_AGENT_URL}/run-selenium", json=payload, timeout=30)
        res_data = response.json()
        
        if res_data.get("status") == True:
            if command == "dp":
                reply_text = (
                    f"✅ **Berhasil Menambahkan Credit (DP)!**\n\n"
                    f"👤 **Agen:** `{agent_name}`\n"
                    f"🎯 **Target:** `{target_user}`\n"
                    f"📊 **Credit Sebelum:** `{res_data['old_credit']}`\n"
                    f"➕ **Jumlah DP:** `{res_data['processed_amount']}`\n"
                    f"💰 **Credit Sesudah:** `{res_data['new_credit']}`"
                )
            else:
                reply_text = (
                    f"✅ **Berhasil Melakukan Withdraw (WD)!**\n\n"
                    f"👤 **Agen:** `{agent_name}`\n"
                    f"🎯 **Target:** `{target_user}`\n"
                    f"⚙️ **Metode:** `{res_data['method']}`\n"
                    f"📊 **Credit Sebelum:** `{res_data['old_credit']}`\n"
                    f"➖ **Jumlah WD:** `{res_data['processed_amount']}`\n"
                    f"💰 **Status Akhir:** `{res_data['new_credit']}`"
                )
            bot.reply_to(message, reply_text, parse_node="Markdown")
        else:
            bot.reply_to(message, f"❌ Gagal di Komputer Lokal.\nError: `{res_data.get('error', 'Unknown error')}`", parse_mode="Markdown")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Gagal menghubungi Komputer Lokal: Koneksi terputus/Komputer mati.\nError: `{str(e)}`", parse_mode="Markdown")

@server.route(f"/{TOKEN}", methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@server.route("/")
def webhook():
    bot.remove_webhook()
    render_url = os.getenv('RENDER_EXTERNAL_HOSTNAME')
    if render_url:
        bot.set_webhook(url=f"https://{render_url}/{TOKEN}")
    return "BPBOT CLOUD CONNECTOR LIVE!", 200

if __name__ == "__main__":
    bot.remove_webhook()
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
