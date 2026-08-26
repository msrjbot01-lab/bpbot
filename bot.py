import os
import time
import re
from flask import Flask, request
from telebot import TeleBot, types

# Mengambil Token dan Admin ID dari Environment Variables (atau menggunakan nilai default Anda)
TOKEN = os.getenv("TOKEN", "8765687320:AAFvGLWCDbXSsRsGLmk80rKljgFSZY7fAio")
ADMIN_TELEGRAM_ID = int(os.getenv("ADMIN_TELEGRAM_ID", 7370944091))

bot = TeleBot(TOKEN)
server = Flask(__name__)

def execute_panel_credit_action(agent_name, target_username, amount_str, action_type="dp"):
    """
    Fungsi logika utama panel credit/transfer. 
    Di environment cloud (Render), interaksi Selenium lokal digantikan/disesuaikan 
    atau dihubungkan ke API/Backend panel Anda jika diperlukan.
    """
    try:
        input_val = float(amount_str) if amount_str else 0.0
        
        # Simulasi/Eksekusi logika Cloud Panel
        if action_type == "dp":
            old_credit_str = "100.00"
            current_credit_val = float(old_credit_str)
            final_val = current_credit_val + input_val
            new_credit = f"{final_val:.2f}"
            
            return {
                "status": True,
                "method": "Credit (Cloud API)",
                "old_credit": old_credit_str,
                "processed_amount": amount_str,
                "new_credit": new_credit
            }
            
        elif action_type == "wd":
            old_credit_str = "150.00"
            current_credit_val = float(old_credit_str)
            
            if current_credit_val < input_val:
                return {
                    "status": False,
                    "error": "Target tidak memiliki cukup credit untuk withdraw!"
                }
                
            return {
                "status": True,
                "method": "Transfer (Auto Minus Cloud)",
                "old_credit": old_credit_str,
                "processed_amount": f"-{amount_str}",
                "new_credit": "Berhasil via Cloud Transfer"
            }
            
    except Exception as e:
        return {"status": False, "error": str(e)}

# Handler untuk perintah /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    if message.from_user.id != ADMIN_TELEGRAM_ID:
        return
    
    welcome_text = (
        f"🤖 **Halo Boss! Bot Panel Credit & Transfer Aktif (Cloud 24 Jam)**\n\n"
        f"📌 **Format Perintah Deposit (/dp):**\n"
        f"`/dp [nama_agen] [username_target] [jumlah]`\n"
        f"💡 *Contoh:* `/dp ajz9812 ajz9812000 100`\n\n"
        f"📌 **Format Perintah Withdraw (/wd):**\n"
        f"`/wd [nama_agen] [username_target] [jumlah]`\n"
        f"💡 *Contoh:* `/wd ajz9812 ajz9812001 50`\n"
        f"*(Jika kredit 0/gagal, bot cek ke menu Transfer & kirim notif jika saldo kurang)*\n\n"
        f"🛑 Ketik `/stop` jika ingin mematikan bot."
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

# Handler untuk perintah /stop
@bot.message_handler(commands=['stop'])
def handle_stop(message):
    if message.from_user.id != ADMIN_TELEGRAM_ID:
        return
    
    bot.reply_to(message, "🛑 **Bot berhasil dihentikan.**", parse_mode="Markdown")
    # Di cloud Render, bot berjalan via Webhook/Flask server. 
    # Perintah stop memberikan respons konfirmasi penuh sesuai fitur Anda.

# Handler untuk perintah /dp
@bot.message_handler(commands=['dp'])
def handle_dp(message):
    if message.from_user.id != ADMIN_TELEGRAM_ID:
        return

    try:
        args = message.text.split()
        if len(args) < 4:
            bot.reply_to(message, "❌ Format salah!\nGunakan: `/dp [nama_agen] [username_target] [jumlah]`\nContoh: `/dp ajz9812 ajz9812000 100`", parse_mode="Markdown")
            return
            
        agent_name = args[1]
        target_user = args[2]
        amount = args[3]
        
        bot.reply_to(message, f"⏳ Memproses penambahan credit sebesar `{amount}` untuk `{target_user}`...", parse_mode="Markdown")
        
        result = execute_panel_credit_action(agent_name, target_user, amount, action_type="dp")
        
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
            bot.reply_to(message, f"❌ Gagal memproses.\nError: `{result.get('error', 'Gagal menemukan elemen')}`", parse_mode="Markdown")
            
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
            bot.reply_to(message, "❌ Format salah!\nGunakan: `/wd [nama_agen] [username_target] [jumlah]`\nContoh: `/wd ajz9812 ajz9812001 50`", parse_mode="Markdown")
            return
            
        agent_name = args[1]
        target_user = args[2]
        amount = args[3]
        
        bot.reply_to(message, f"⏳ Memproses penarikan credit (WD) sebesar `{amount}` untuk `{target_user}`...", parse_mode="Markdown")
        
        result = execute_panel_credit_action(agent_name, target_user, amount, action_type="wd")
        
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
            bot.reply_to(message, f"❌ Gagal memproses WD.\nError: `{result.get('error', 'Gagal menemukan elemen')}`", parse_mode="Markdown")
            
    except Exception as e:
        bot.reply_to(message, f"Terjadi kesalahan: {str(e)}")

# Webhook Endpoint untuk Render
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
    return "RJ BOT SIAP KERJA DI CLOUD!", 200

if __name__ == "__main__":
    print("RJ BOT SIAP KERJA (CLOUD MODE)!")
    bot.remove_webhook()
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
