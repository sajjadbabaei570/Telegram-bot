import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# 🔑 توکن ربات از BotFather
TOKEN = "6944863469:AAH4TKEA6ScsPAa7b3Qr8x_Fa2oD_WpYxio"

# 🌐 تابع جست‌وجو در وب با DuckDuckGo
def search_web(query):
    url = f"https://duckduckgo.com/html/?q={query}"
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    for link in soup.select('.result__a')[:5]:
        title = link.get_text()
        href = link.get('href')
        results.append(f"🔹 [{title}]({href})")

    if not results:
        return None
    return "\n\n".join(results)

# 🌍 تشخیص زبان ساده (فارسی، عربی یا انگلیسی)
def detect_language(text):
    arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
    english_chars = sum(1 for c in text if ('a' <= c.lower() <= 'z'))
    if arabic_chars > english_chars:
        if any('ك' in text or 'ل' in text):  # احتمال عربی
            return "ar"
        return "fa"
    return "en"

# 🟢 دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_fa = "سلام! 👋\nمن *Telegram Explorer* هستم 🌐\nعبارتی برای جست‌وجو بفرست تا نتایج را برایت بیاورم."
    message_ar = "مرحباً! 👋\nأنا *Telegram Explorer* 🌐\nأرسل عبارة للبحث وسأعرض النتائج لك."
    message_en = "Hello! 👋\nI'm *Telegram Explorer* 🌐\nSend me a search term and I'll show you the results."

    user_lang = detect_language(update.effective_user.language_code or "en")

    if user_lang == "fa":
        msg = message_fa
    elif user_lang == "ar":
        msg = message_ar
    else:
        msg = message_en

    await update.message.reply_text(msg, parse_mode="Markdown")

# 🔎 پاسخ به پیام‌های جست‌وجو
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    lang = detect_language(query)

    # پیام شروع جست‌وجو
    if lang == "fa":
        waiting_msg = f"🔎 در حال جست‌وجو برای: *{query}*"
    elif lang == "ar":
        waiting_msg = f"🔎 جاري البحث عن: *{query}*"
    else:
        waiting_msg = f"🔎 Searching for: *{query}*"

    await update.message.reply_text(waiting_msg, parse_mode="Markdown")

    results = search_web(query)

    # پاسخ نتایج
    if not results:
        if lang == "fa":
            text = "❌ نتیجه‌ای یافت نشد."
        elif lang == "ar":
            text = "❌ لم يتم العثور على نتائج."
        else:
            text = "❌ No results found."
    else:
        text = results

    await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)

# 🧿 دستور /logo — نمایش لوگو
async def logo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if os.path.exists("logo.png"):
        with open("logo.png", "rb") as photo:
            await update.message.reply_photo(photo, caption="🌐 Telegram Explorer")
    else:
        await update.message.reply_text("📷 لوگو هنوز آپلود نشده است.")

# 🚀 اجرای ربات
app = ApplicationBuilder().token(6944863469:AAH4TKEA6ScsPAa7b3Qr8x_Fa2oD_WpYxio).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("logo", logo))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🤖 Telegram Explorer Bot is running (FA/AR/EN)...")
app.run_polling()
