import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "8443293671:AAFJsd_nIyBlRy_mm-Lj79VCOJL2jX_noPo"  # O'z tokeningni yoz

# aria2c.exe joylashgan joy
ARIA2C_PATH = r"C:\aria2\aria2c.exe"  # ZIP ichidagi .exe shu papkaga ochilgan bo'lishi kerak

async def download_video(url):
    ydl_opts = {
        'outtmpl': 'video.%(ext)s',  # Yuklab olingan fayl nomi
        'format': 'best[ext=mp4]',   # Eng yaxshi MP4 sifat
        'external_downloader': ARIA2C_PATH,  # To'g'ridan-to'g'ri exe manzili
        'external_downloader_args': ['-x16', '-k1M'],  # 16 parallel oqim, 1MB bo‘lak
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 YouTube link yuboring, men videoni tez yuklab beraman!")

# Foydalanuvchi yuborgan linkni qayta ishlash
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("❌ Faqat YouTube link yuboring!")
        return

    await update.message.reply_text("⏳ Yuklanmoqda, biroz kuting...")

    try:
        video_path = await download_video(url)

        # Telegram 50 MB limitni tekshirish
        if os.path.getsize(video_path) > 50 * 1024 * 1024:
            await update.message.reply_text("⚠️ Video hajmi 50 MB dan katta, yuborib bo‘lmaydi!")
            os.remove(video_path)
            return

        await update.message.reply_video(video=open(video_path, "rb"))
        os.remove(video_path)

    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik: {e}")

# Botni ishga tushirish
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
app.run_polling()
