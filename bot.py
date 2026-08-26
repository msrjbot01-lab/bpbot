import os
import time
import telebot
from flask import Flask, request

# Mengambil Token dan Admin ID dari Environment Variables Render (Lebih Aman)
TOKEN = os.getenv("TOKEN", "8765687320:AAFvGLWCDbXSsRsGLmk80rKljgFSZY7fAio")
ADMIN_TELEGRAM_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "7370944091"))

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

# Fungsi tiruan / logika pemrosesan yang bisa Anda hubungkan ke Database/API Panel Anda
def process_cloud_credit_action(agent_name, target_username, amount_str, action_type="dp"):
    try:
        # TODO: Masukkan logika API panel Anda di sini (misal menggunakan requests ke backend panel Anda)
        # Contoh simulasi sukses:
        input_val = float(amount_str)
        
        if action_type == "dp":
            return {
                "status": True,
                "method": "Cloud API Credit",
                "old_credit": "100.00",
                "processed_amount": amount_str,
                "new_credit": str(100.00 + input_val)
            }
        elif action_type == "wd":
            return {
                "status": True,
                "method": "Cloud API Transfer",
                "old_credit": "150.00",
                "processed_amount": f"-{amount_str}",
                "new_credit": "Berhasil via Cloud API"
            }
    except Exception as e:
        return {"status": False, "error": str(e)}

# Handler untuk perintah /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    if message.from_user.id != ADMIN_TELEGRAM_ID:
        return
    
    welcome_text = (
        f"🤖 **Halo Boss! Bot Cloud Panel 24 Jam Aktif**\n\n"
        f"📌 **Format Perintah Deposit (/dp):**\n"
        f"`/dp [nama_agen] [username_target] [jumlah]`\n\n"
        f"📌 **Format Perintah Withdraw (/wd):**\n"
        f"`/wd [nama_agen] [username_target] [jumlah]`\n\n"
        f"🚀 Bot ini berjalan secara cloud (Render/GitHub)."
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

# Handler untuk perintah /dp
@bot.message_handler(commands=['dp'])
def handle_dp(message):
    if message.from_user.id != ADMIN_TELEGRAM_ID:
        return

    try:
        args = message.text.split()
        if len(args) < 4:
            bot.reply_to(message, "❌ Format salah!\nGunakan: `/dp [nama_agen] [username_target] [jumlah]`", parse_mode="Markdown")
            return
            
        agent_name = args[1]
        target_user = args[2]
        amount = args[3]
        
        bot.reply_to(message, f"⏳ Memproses penambahan credit cloud sebesar `{amount}` untuk `{target_user}`...", parse_mode="Markdown")
        
        result = process_cloud_credit_action(agent_name, target_user, amount, action_type="dp")
        
        if isinstance(result, dict) and result.get("status") == True:
            reply_text = (
                f"✅ **Berhasil Menambahkan Credit (DP)!**\n\n"
                f"👤 **Agen:** `{agent_name}`\n"
                f"🎯 **Target:** `{target_user}`\n"
                f"📊 **Credit Sebelum:** `{result['old_credit']}`\n"
                f"➕ **Jumlah DP:** `{result['processed_amount']}`\n"
                f"💰 **Credit Sesudah:** `{result['new_credit']}`"
            )
            bot.reply_to(message, reply_text, parse_mode="Markdown")
        else:
            bot.reply_to(message, f"❌ Gagal memproses.\nError: `{result.get('error', 'Gagal')}`", parse_mode="Markdown")
            
    except Exception as e:
        bot.reply_to(message, f"Terjadi kesalahan: {str(e)}")

# Handler untuk perintah /wd
@bot.message_handler(commands=['wd'])
def handle_wd(message):
    if message.from_user.id != ADMIN_TELEGRAM_ID:
        return

    try:
        args = message.text.split()
        if len(args) < 4:
            bot.reply_to(message, "❌ Format salah!\nGunakan: `/wd [nama_agen] [username_target] [jumlah]`", parse_mode="Markdown")
            return
            
        agent_name = args[1]
        target_user = args[2]
        amount = args[3]
        
        bot.reply_to(message, f"⏳ Memproses penarikan credit (WD) cloud sebesar `{amount}` untuk `{target_user}`...", parse_mode="Markdown")
        
        result = process_cloud_credit_action(agent_name, target_user, amount, action_type="wd")
        
        if isinstance(result, dict) and result.get("status") == True:
            reply_text = (
                f"✅ **Berhasil Melakukan Withdraw (WD)!**\n\n"
                f"👤 **Agen:** `{agent_name}`\n"
                f"🎯 **Target:** `{target_user}`\n"
                f"⚙️ **Metode:** `{result['method']}`\n"
                f"📊 **Credit Sebelum:** `{result['old_credit']}`\n"
                f"➖ **Jumlah WD:** `{result['processed_amount']}`\n"
                f"💰 **Status Akhir:** `{result['new_credit']}`"
            )
            bot.reply_to(message, reply_text, parse_mode="Markdown")
        else:
            bot.reply_to(message, f"❌ Gagal memproses WD.\nError: `{result.get('error', 'Gagal')}`", parse_mode="Markdown")
            
    except Exception as e:
        bot.reply_to(message, f"Terjadi kesalahan: {str(e)}")

# Webhook Flask Route untuk Render (Agar Render mendeteksi aplikasi web yang aktif)
@server.route(f"/{TOKEN}", methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@server.route("/")
def webhook():
    bot.remove_webhook()
    # Menggunakan Webhook URL dari Render (ganti 'nama-app-anda.onrender.com' dengan domain Render Anda nanti)
    # Atau biarkan menggunakan polling biasa jika tipe websitenya Background Worker di Render.
    bot.set_webhook(url=f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}")
    return "Bot Telegram 24 Jam Berjalan!", 200

if __name__ == "__main__":
    # Jalankan Flask server untuk Render, atau jalankan polling biasa jika dijalankan manual
    bot.remove_webhook()
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
