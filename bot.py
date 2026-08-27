import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from gtts import gTTS
import os

API_TOKEN = os.getenv("BOT_TOKEN")
WEB3_WALLET = os.getenv("WEB3_WALLET", "0xYourWalletAddressHere")
WEB3_NETWORK = os.getenv("WEB3_NETWORK", "BSC / ERC20")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_data = {}

async def send_lina_voice(chat_id, text):
    try:
        tts = gTTS(text=text, lang='ar', slow=False)
        voice_path = "lina_voice.mp3"
        tts.save(voice_path)
        with open(voice_path, 'rb') as voice:
            await bot.send_voice(chat_id, voice)
        os.remove(voice_path)
    except Exception as e:
        logging.error(f"Voice error: {e}")

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("Real Estate", callback_data="real_estate"),
        InlineKeyboardButton("Cars", callback_data="cars"),
        InlineKeyboardButton("Services", callback_data="services"),
        InlineKeyboardButton("Containers", callback_data="containers"),
        InlineKeyboardButton("Monthly Subscription (2.99€)", callback_data="sub"),
        InlineKeyboardButton("Crypto Payment (0.50€)", callback_data="web3")
    )
    
    welcome_text = "Welcome! I am Lina.\nMonthly Subscription is €2.99, and Order Opening Fee is €0.50.\nHow can I help you today?"
    await send_lina_voice(message.chat.id, welcome_text)
    await message.answer(welcome_text, reply_markup=keyboard)

@dp.callback_query_handler(lambda call: True)
async def process(call: types.CallbackQuery) -> None:
    user_id = call.from_user.id
    await call.answer()

    if call.data == "web3":
        voice_text = "To complete the order, please pay the opening fee of only fifty cents via cryptocurrencies."
        await send_lina_voice(call.message.chat.id, voice_text)
        await call.message.answer(
            f"💳 **Payment via Crypto (Web3):**\n\n"
            f"📍 **Address:** `{WEB3_WALLET}`\n"
            f"🌐 **Network:** {WEB3_NETWORK}\n"
            f"💰 **Amount Required:** 0.50 USDT\n\n"
            f"After payment, please send the transaction hash (Tx Hash) starting with (0x...).",
            parse_mode="Markdown",
        )
        return

    user_data[user_id] = {"type": call.data, "step": 1}
    
    if call.data == "real_estate":
        category_name = "Real Estate"
    elif call.data == "cars":
        category_name = "Cars"
    elif call.data == "services":
        category_name = "Services"
    elif call.data == "containers":
        category_name = "Containers"
    elif call.data == "sub":
        category_name = "Monthly Subscription"
    else:
        category_name = "Selected Section"

    await call.message.answer(
        f"You have selected: **{category_name}**.\n\nPlease proceed by choosing the payment method:",
        parse_mode="Markdown"
    )

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
