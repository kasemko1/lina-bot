import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from gtts import gTTS
import os

API_TOKEN = os.getenv("BOT_TOKEN")

# روابط Stripe الرسمية الخاصة بك
STRIPE_SUB_URL = "https://buy.stripe.com/eVq9AS98hfsZ7Hu3LadZ600"       # اشتراك شهري (€2.99)
STRIPE_ONETIME_URL = "https://buy.stripe.com/evq8w03NXbcJ9PC3LadZ601" # خدمة فردية (€0.50)

# عنوان محفظة ميتا ماسك الخاصة بك (Polygon/Web3)
METAMASK_WALLET_ADDRESS = "0x0e3c35B1242dB3f7E60E554266eB7be90706f355"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_states = {}
user_data = {}
user_ledger = {}

BLOCKED_COUNTRIES = ["ru", "ir"]

TRANSLATIONS = {
    "ar": {
        "welcome": "هلا والله يا كاسم! أنا لينا. شو أمورنا اليوم؟ شو حابب نخلص ونسجل؟",
        "voice_welcome": "هلا فيك، شو الخدمة المطلوبة اليوم؟",
        "blocked": "عذراً، الخدمة مش شغالة بدلتك.",
        "real_estate": "عقارات",
        "cars": "سيارات",
        "services": "خدمات عامة",
        "ledger": "📊 السجل المحاسبي",
        "containers": "كونتينرات",
        "support": "📞 الدعم الفني",
        "sub": "اشتراكي €2.99",
        "web3": "دفع كريبتو €0.50",
        "bill_elec": "⚡ فاتورة الكهرباء",
        "bill_water": "💧 فاتورة المياه",
        "bill_phone": "📱 فاتورة الهاتف",
        "bill_tax": "🚗 ضريبة السيارة",
        "payment_prompt": "تمام، اخترت: **{item}**.\n\nلإتمام الدفع بشكل قانوني وآمن عبر بوابة الدفع الإلكترونية، يرجى الضغط على الزر أدناه:",
        "payment_received_success": "كفو! ✅ تم التحقق من الدفع وتوثيق ({item}) بالدفتر عنا رسمياً.",
        "ledger_report": "📊 **السجل المحاسبي:**\n\n- العمليات المسجلة: {count}\n- الوضع تمام وموثق 100%.",
        "stripe_text": "💳 **بوابة الدفع الإلكتروني الآمنة (Stripe):**\n\nاضغط على الرابط أدناه لإتمام الدفع بالبطاقة البنكية بشكل آمن ومطابق للقوانين:\n\n🔗 [اضغط هنا للدفع بالبطاقة]({url})\n\nبعد إتمام الدفع، سيتم تسجيل العملية وتحديث حسابك تلقائياً.",
        "web3_text": "🪙 **دفع عبر Web3 (كريبتو):**\n\nلإتمام الدفع، يرجى تحويل المبلغ مباشرة إلى عنوان محفظتك في ميتا ماسك على شبكة Polygon:\n\n`{wallet}`\n\n*(تأكد من إرسال المبلغ الصحيح للعنوان أعلاه)*",
        "quick_reply": "معك، شو عنا شغل تاني؟ اختار من تحت:"
    },
    "en": {
        "welcome": "Hey Kassem! I'm Lina. What are we working on today?",
        "voice_welcome": "Hey, what service do you need?",
        "blocked": "Sorry, not available in your region.",
        "real_estate": "Real Estate",
        "cars": "Cars",
        "services": "General Services",
        "ledger": "📊 Accounting Ledger",
        "containers": "Containers",
        "support": "📞 Digital Support",
        "sub": "Monthly Sub €2.99",
        "web3": "Crypto €0.50",
        "bill_elec": "⚡ Electricity",
        "bill_water": "💧 Water",
        "bill_phone": "📱 Phone",
        "bill_tax": "🚗 Car Tax",
        "payment_prompt": "Got it, selected: **{item}**.\n\nTo pay securely via our certified payment gateway, please click the button below:",
        "payment_received_success": "Done! ✅ Payment verified and ({item}) logged successfully.",
        "ledger_report": "📊 **Ledger:**\n\n- Logged items: {count}\n- All clean and compliant.",
        "stripe_text": "💳 **Secure Payment Gateway (Stripe):**\n\nClick the link below to pay securely with your card:\n\n🔗 [Click here for Secure Checkout]({url})\n\nOnce paid, your transaction will be logged automatically.",
        "web3_text": "🪙 **Web3 Crypto Payment:**\n\nTo pay, please send the funds directly to your MetaMask wallet address below (Polygon/EVM):\n\n`{wallet}`",
        "quick_reply": "I'm here. What's next?"
    }
}

def get_lang(message_or_call):
    code = message_or_call.from_user.language_code
    if code in TRANSLATIONS:
        return code
    return "en"

async def send_lina_voice(chat_id, text, lang='ar'):
    try:
        voice_lang = 'ar' if lang == 'ar' else 'en'
        tts = gTTS(text=text, lang=voice_lang, slow=False)
        voice_path = "lina_voice.mp3"
        tts.save(voice_path)
        with open(voice_path, 'rb') as voice:
            await bot.send_voice(chat_id, voice)
        os.remove(voice_path)
    except Exception as e:
        logging.error(f"Voice error: {e}")

def get_main_keyboard(t):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(t["real_estate"], callback_data="real_estate"),
        InlineKeyboardButton(t["cars"], callback_data="cars"),
        InlineKeyboardButton(t["bill_elec"], callback_data="bill_elec"),
        InlineKeyboardButton(t["bill_water"], callback_data="bill_water"),
        InlineKeyboardButton(t["bill_phone"], callback_data="bill_phone"),
        InlineKeyboardButton(t["bill_tax"], callback_data="bill_tax"),
        InlineKeyboardButton(t["ledger"], callback_data="view_ledger"),
        InlineKeyboardButton(t["services"], callback_data="services"),
        InlineKeyboardButton(t["containers"], callback_data="containers"),
        InlineKeyboardButton(t["sub"], callback_data="sub"),
        InlineKeyboardButton(t["web3"], callback_data="web3")
    )
    return keyboard

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    user_lang = message.from_user.language_code
    if user_lang in BLOCKED_COUNTRIES:
        lang = "en" if user_lang not in TRANSLATIONS else user_lang
        await message.answer(TRANSLATIONS[lang]["blocked"])
        return

    user_states[user_id] = "main_menu"
    lang = get_lang(message)
    t = TRANSLATIONS[lang]
    
    await send_lina_voice(message.chat.id, t["voice_welcome"], lang)
    await message.answer(t["welcome"], reply_markup=get_main_keyboard(t))

@dp.message_handler(lambda message: not message.text.startswith('/'))
async def handle_smart_sensor(message: types.Message):
    user_id = message.from_user.id
    user_lang = message.from_user.language_code
    if user_lang in BLOCKED_COUNTRIES:
        return

    lang = get_lang(message)
    t = TRANSLATIONS[lang]
    current_state = user_states.get(user_id, "main_menu")

    if current_state == "waiting_for_payment_method":
        user_states[user_id] = "main_menu"
        await message.answer(
            t["stripe_text"].format(url=STRIPE_ONETIME_URL),
            parse_mode="Markdown"
        )
        return

    user_states[user_id] = "main_menu"
    await send_lina_voice(message.chat.id, t["voice_welcome"], lang)
    await message.answer(t["quick_reply"], reply_markup=get_main_keyboard(t))

@dp.callback_query_handler(lambda call: True)
async def process_callbacks(call: types.CallbackQuery) -> None:
    user_id = call.from_user.id
    user_lang = call.from_user.language_code
    
    if user_lang in BLOCKED_COUNTRIES:
        await call.answer("Blocked", show_alert=True)
        return

    lang = get_lang(call)
    t = TRANSLATIONS[lang]
    await call.answer()

    if call.data == "web3":
        user_states[user_id] = "main_menu"
        user_data[user_id] = {"item_name": t["web3"]}
        await call.message.answer(
            t["web3_text"].format(wallet=METAMASK_WALLET_ADDRESS),
            parse_mode="Markdown",
        )
        return

    if call.data == "sub":
        user_states[user_id] = "main_menu"
        user_data[user_id] = {"item_name": t["sub"]}
        await call.message.answer(
            t["stripe_text"].format(url=STRIPE_SUB_URL),
            parse_mode="Markdown",
        )
        return

    if call.data == "view_ledger":
        user_states[user_id] = "main_menu"
        count = len(user_ledger.get(user_id, []))
        await call.message.answer(
            t["ledger_report"].format(count=count),
            parse_mode="Markdown"
        )
        return

    item_names = {
        "bill_elec": t["bill_elec"],
        "bill_water": t["bill_water"],
        "bill_phone": t["bill_phone"],
        "bill_tax": t["bill_tax"],
        "real_estate": t["real_estate"],
        "cars": t["cars"],
        "services": t["services"],
        "containers": t["containers"]
    }
    
    item_name = item_names.get(call.data, "Service")
    user_data[user_id] = {"item_name": item_name}
    user_states[user_id] = "waiting_for_payment_method"

    await call.message.answer(
        t["payment_prompt"].format(item=item_name),
        parse_mode="Markdown"
    )

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
