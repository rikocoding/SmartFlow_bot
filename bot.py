import os
import datetime
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler

# Load token dari .env
load_dotenv()
bot_token = os.getenv('BOT_TOKEN')

# Variabel global
setpoint = 1000  # Default setpoint volume air dalam mL (1000 mL = 1 Liter)
solenoid_status = "Tertutup "  # Default kondisi solenoid tertutup
WAITING_FOR_SETPOINT = 1  # Status untuk menunggu input angka

# Fungsi untuk mendapatkan data debit air dari sensor
def get_debit_air():
    return 500  # Gantilah dengan kode membaca sensor (dalam mL/min)

# Fungsi untuk mendapatkan data volume air dari sensor
def get_volume_air():
    return 5000  # Gantilah dengan kode membaca sensor (dalam mL)

# Fungsi untuk mendapatkan waktu sekarang dalam format yang mudah dibaca
def get_waktu_pengukuran():
    return datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

# Fungsi untuk mengontrol solenoid valve
def kontrol_solenoid(status: str):
    global solenoid_status
    if status == "open":
        solenoid_status = "Terbuka "
        return " Solenoid valve dibuka "
    elif status == "close":
        solenoid_status = "Tertutup "
        return " Solenoid valve ditutup "
    return "Perintah tidak dikenali"

# Fungsi untuk menampilkan keyboard menu
def get_main_menu():
    keyboard = [
        ["/data", "/setpoint"],
        ["/open", "/close"],
        ["/hide"]  # Tombol untuk menyembunyikan keyboard
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Fungsi untuk menangani perintah /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Halo! Ini adalah bot monitoring air. Pilih menu di bawah ini:",
        reply_markup=get_main_menu()
    )

# Fungsi untuk menampilkan data debit & volume air
async def data(update: Update, context: CallbackContext):
    global setpoint, solenoid_status
    debit_air = get_debit_air()
    volume_air = get_volume_air()
    waktu_pengukuran = get_waktu_pengukuran()

    pesan = (
        f" **Data Pengukuran Air** \n"
        f" Waktu Pengukuran: {waktu_pengukuran}\n"
        f" Debit Air: {debit_air} mL/min\n"
        f" Volume Air: {volume_air} mL\n"
        f" Setpoint: {setpoint} mL\n"
        f" Kondisi Solenoid: {solenoid_status}"
    )
    await update.message.reply_text(pesan)

# Fungsi untuk memulai proses setpoint (MENAMPILKAN PLACEHOLDER)
async def start_setpoint(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Silakan masukkan angka untuk setpoint volume air dalam mL:",
        reply_markup=ForceReply(input_field_placeholder="Masukkan angka dalam mL...")
    )
    return WAITING_FOR_SETPOINT  # Masuk ke mode menunggu input angka

# Fungsi untuk menyimpan angka setpoint yang dikirim pengguna
async def save_setpoint(update: Update, context: CallbackContext):
    global setpoint
    try:
        setpoint = int(update.message.text)  # Coba konversi ke angka
        await update.message.reply_text(f" Setpoint diperbarui: {setpoint} mL")
        return ConversationHandler.END  # Selesai
    except ValueError:
        await update.message.reply_text(" Masukkan angka yang valid! Coba lagi.")
        return WAITING_FOR_SETPOINT  # Tetap dalam mode menunggu angka

# Fungsi untuk membatalkan setpoint
async def cancel_setpoint(update: Update, context: CallbackContext):
    await update.message.reply_text(" Pengaturan setpoint dibatalkan.")
    return ConversationHandler.END  # Keluar dari mode input angka

# Fungsi untuk membuka solenoid valve
async def open_valve(update: Update, context: CallbackContext):
    pesan = kontrol_solenoid("open")
    await update.message.reply_text(pesan)

# Fungsi untuk menutup solenoid valve
async def close_valve(update: Update, context: CallbackContext):
    pesan = kontrol_solenoid("close")
    await update.message.reply_text(pesan)

# Fungsi untuk menyembunyikan keyboard menu
async def hide_keyboard(update: Update, context: CallbackContext):
    await update.message.reply_text("Keyboard disembunyikan.", reply_markup=ReplyKeyboardRemove())

# Fungsi utama untuk menjalankan bot
def main():
    app = Application.builder().token(bot_token).build()

    # Menangani perintah /setpoint sebagai percakapan
    setpoint_handler = ConversationHandler(
        entry_points=[CommandHandler("setpoint", start_setpoint)],
        states={WAITING_FOR_SETPOINT: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_setpoint)]},
        fallbacks=[CommandHandler("cancel", cancel_setpoint)]
    )

    # Menambahkan handler untuk command
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("data", data))
    app.add_handler(setpoint_handler)
    app.add_handler(CommandHandler("open", open_valve))
    app.add_handler(CommandHandler("close", close_valve))
    app.add_handler(CommandHandler("hide", hide_keyboard))  # Menambahkan handler untuk /hide

    print("Bot sedang berjalan...")
    app.run_polling()

# Menjalankan bot
if __name__ == "__main__":
    main()
