import os
import logging
from telegram import Update, ChatMember
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Загрузка переменных
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
REWARD_LINK = os.getenv('REWARD_LINK', '@kattyshechk')
CHANNEL_USERNAME = os.getenv('CHANNEL_USERNAME', 'https://t.me/+DHCCC5FoftlmNmUx')  # Например: @my_channel

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

user_data = {}

async def check_subscription(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Проверяет, подписан ли пользователь на канал"""
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in [ChatMember.OWNER, ChatMember.ADMINISTRATOR, ChatMember.MEMBER]
    except Exception as e:
        logger.error(f"Ошибка проверки подписки: {e}")
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверяем подписку
    is_subscribed = await check_subscription(user_id, context)
    
    if not is_subscribed:
        keyboard = [
            [{"text": "📢 Подписаться на канал", "url": f"https://t.me/{CHANNEL_USERNAME[1:]}"}],
            [{"text": "✅ Я подписался", "callback_data": "check_subscription"}]
        ]
        reply_markup = {"inline_keyboard": keyboard}
        
        await update.message.reply_text(
            "📢 *Для использования бота необходимо подписаться на наш канал!*\n\n"
            f"Канал: {CHANNEL_USERNAME}\n\n"
            "После подписки нажми кнопку '✅ Я подписался'",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return
    
    # Если подписан - продолжаем
    user_data[user_id] = {'photos': 0}
    await update.message.reply_text(
        "📸 *Привет! Отправь 5 фотографий и получи ссылку!*\n\n"
        "Прогресс: 0/5 фото\n"
        "Просто отправь первую фотографию...",
        parse_mode='Markdown'
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий кнопок"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if query.data == "check_subscription":
        is_subscribed = await check_subscription(user_id, context)
        
        if is_subscribed:
            user_data[user_id] = {'photos': 0}
            await query.edit_message_text(
                "✅ *Отлично! Ты подписан на канал!*\n\n"
                "📸 Теперь отправь 5 фотографий и получи ссылку!\n"
                "Прогресс: 0/5 фото\n"
                "Просто отправь первую фотографию...",
                parse_mode='Markdown'
            )
        else:
            keyboard = [
                [{"text": "📢 Подписаться на канал", "url": f"https://t.me/{CHANNEL_USERNAME[1:]}"}],
                [{"text": "✅ Я подписался", "callback_data": "check_subscription"}]
            ]
            reply_markup = {"inline_keyboard": keyboard}
            
            await query.edit_message_text(
                "❌ *Ты еще не подписан на канал!*\n\n"
                f"Канал: {CHANNEL_USERNAME}\n\n"
                "Подпишись и нажми кнопку '✅ Я подписался'",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверяем подписку перед обработкой фото
    is_subscribed = await check_subscription(user_id, context)
    
    if not is_subscribed:
        keyboard = [
            [{"text": "📢 Подписаться на канал", "url": f"https://t.me/{CHANNEL_USERNAME[1:]}"}],
            [{"text": "✅ Я подписался", "callback_data": "check_subscription"}]
        ]
        reply_markup = {"inline_keyboard": keyboard}
        
        await update.message.reply_text(
            "❌ *Для отправки фото необходимо подписаться на канал!*\n\n"
            f"Канал: {CHANNEL_USERNAME}",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return
    
    # Если подписан - обрабатываем фото
    if user_id not in user_data:
        user_data[user_id] = {'photos': 0}
    
    user_data[user_id]['photos'] += 1
    count = user_data[user_id]['photos']
    
    if count >= 5:
        user_data[user_id]['photos'] = 0
        await update.message.reply_text(
            f"🎉 *Поздравляю! Ты отправил 5 фото!*\n\n"
            f"Вот твоя награда:\n{REWARD_LINK}",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            f"✅ *Фото {count}/5 получено!*\n"
            f"Осталось отправить {5 - count} фотографий",
            parse_mode='Markdown'
        )

async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для проверки подписки"""
    user_id = update.effective_user.id
    is_subscribed = await check_subscription(user_id, context)
    
    if is_subscribed:
        await update.message.reply_text("✅ Ты подписан на канал! Можешь использовать бота.")
    else:
        keyboard = [
            [{"text": "📢 Подписаться на канал", "url": f"https://t.me/{CHANNEL_USERNAME[1:]}"}],
            [{"text": "✅ Я подписался", "callback_data": "check_subscription"}]
        ]
        reply_markup = {"inline_keyboard": keyboard}
        
        await update.message.reply_text(
            "❌ Ты не подписан на канал!",
            reply_markup=reply_markup
        )

def main():
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN не найден! Проверь файл .env")
        return
    
    if not CHANNEL_USERNAME or CHANNEL_USERNAME == '@your_channel':
        logger.error("❌ CHANNEL_USERNAME не настроен! Проверь файл .env")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("check", check_command))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    logger.info("🤖 Бот запущен с проверкой подписки!")
    print("✅ Бот работает! Для остановки нажми Ctrl+C")
    
    application.run_polling()

if __name__ == '__main__':
    main()
