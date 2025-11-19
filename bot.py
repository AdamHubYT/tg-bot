import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters

BOT_TOKEN = os.getenv('8520849474:AAF02BxGpXIFwf2fs5VTtaiwLurPWH-PJ_w')
user_data = {}

async def start(update, context):
    user_id = update.effective_user.id
    user_data[user_id] = {'photos': 0}
    await update.message.reply_text("Чтобы получить заветную ссылку на установку, необходимо:

1. Вам необходимо оставить 5 коментариев под любым видео в TikTok, с указанием нашего канала @fr00ol

2. Затем просто отправь скриншоты выполненных действий в нашего бота которого можно найти в нашем канале!\nПрогресс: 0/5")

async def handle_photo(update, context):
    user_id = update.effective_user.id
    if user_id not in user_data:
        user_data[user_id] = {'photos': 0}
    
    user_data[user_id]['photos'] += 1
    count = user_data[user_id]['photos']
    
    if count >= 5:
        await update.message.reply_text("🎉 Поздравляю! Вот твоя ссылка, для получения отпиши сюда:https://t.me/kattyshechk")
        user_data[user_id]['photos'] = 0
    else:
        await update.message.reply_text(f"✅ Фото {count}/5 получено!")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("🤖 Бот запущен!")
    application.run_polling()

if __name__ == '__main__':
    main()
