import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from gtts import gTTS
import os
import requests

API_TOKEN = os.getenv("BOT_TOKEN")

# رقم الآيدي الخاص بك المعتمد للإدارة وتلقي الملاحظات
ADMIN_CHAT_ID = 8807102611  

# روابط Stripe والدفع
STRIPE_SUB_URL = "https://buy.stripe.com/eVq9AS98hfsZ7Hu3LadZ600"       
STRIPE_ONETIME_URL = "https://buy.stripe.com/evq8w03NXbcJ9PC3LadZ601" 
METAMASK_WALLET_ADDRESS = "0x0e3c35B1242dB3f7E60E554266eB7be90706f355"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_states = {}
user_data = {}
user_ledger = {}

BLOCKED_COUNTRIES = ["ru", "ir"]

def get_converted_prices():
    try:
        response = requests.get("https://api.exchangerate-api.com/v4/latest/EUR", timeout=5)
        data = response.json()
        rates = data.get("rates", {})
        usd_rate = rates.get("USD", 1.08)
        gbp_rate = rates.get("GBP", 0.85)
        return {
            "sub": f"€2.99 (~${round(2.99 * usd_rate, 2)} USD)",
            "onetime": f"€0.50 (~${round(0.50 * usd_rate, 2)} USD)"
        }
    except Exception:
        return {"sub": "€2.99", "onetime": "€0.50"}

TRANSLATIONS = {
    "ar": {
        "welcome": "🟢 <b>أهلاً بك في بوت لينا الرسمي (منصة الأعمال الذكية)!</b>\n\nاختر الخدمة المطلوبة أدناه:",
        "voice_welcome": "أهلاً بك في بوت لينا، منصة الأعمال والتنسيق التجاري.",
        "blocked": "عذراً، الخدمة غير متاحة في منطقتك.",
        "real_estate": "🟢 عقارات دولية 🟢",
        "cars": "🟢 قطاع السيارات 🟢",
        "services": "🟢 خدمات عامة 🟢",
        "ledger": "🟢 السجل المحاسبي 🟢",
        "containers": "🟢 الشحن والكونتينرات 🟢",
        "support": "🟢 الدعم الفني 🟢",
        "feedback": "🟢 ترك ملاحظة أو شكوى 🟢",
        "sub": "🟢 اشتراك VIP (€2.99) 🟢",
        "web3": "🟢 دفع رقمي (€0.50) 🟢",
        "bill_elec": "🟢 فاتورة الكهرباء 🟢",
        "bill_water": "🟢 فاتورة المياه 🟢",
        "bill_phone": "🟢 فاتورة الاتصالات 🟢",
        "bill_tax": "🟢 ضريبة المركبات 🟢",
        "payment_prompt": "🟢 <b>تأكيد العملية (€0.50):</b>\n\nلقد اخترت: <b>{item}</b>",
        "feedback_prompt": "🟢 تفضل يا غالي، اكتب ملاحظتك أو شكواك للإدارة:",
        "feedback_thanks": "🟢 تم إرسال ملاحظتك بنجاح للإدارة!",
        "ledger_report": "🟢 <b>السجل المحاسبي:</b> الحركات المسجلة: {count}",
        "stripe_text": "🟢 <b>بوابة الدفع (اشتراك شهري €2.99):</b>\n\n🔗 [اضغط هنا للدفع بالبطاقة]({url})",
        "web3_text": "🟢 <b>دفع عبر الكريبتو (€0.50):</b>\n\n`{wallet}`",
        "quick_reply": "🟢 مرحباً بك مجدداً. اختر إحدى الخدمات:"
    },
    "en": {
        "welcome": "🟢 <b>Welcome to Lina's Official Bot (Business Hub)!</b>",
        "voice_welcome": "Welcome to Lina bot.",
        "blocked": "Region blocked.",
        "real_estate": "🟢 Real Estate 🟢",
        "cars": "🟢 Automotive 🟢",
        "services": "🟢 General Services 🟢",
        "ledger": "🟢 Accounting Ledger 🟢",
        "containers": "🟢 Containers 🟢",
        "support": "🟢 Digital Support 🟢",
        "feedback": "🟢 Leave Feedback 🟢",
        "sub": "🟢 VIP Sub (€2.99) 🟢",
        "web3": "🟢 Crypto (€0.50) 🟢",
        "bill_elec": "🟢 Electricity 🟢",
        "bill_water": "🟢 Water 🟢",
        "bill_phone": "🟢 Phone 🟢",
        "bill_tax": "🟢 Car Tax 🟢",
        "payment_prompt": "🟢 <b>Payment (€0.50):</b> <b>{item}</b>",
        "feedback_prompt": "🟢 Type your feedback:",
        "feedback_thanks": "🟢 Feedback sent!",
        "ledger_report": "🟢 <b>Ledger:</b> {count}",
        "stripe_text": "🟢 🔗 [Pay]({url})",
        "web3_text": "🟢 `{wallet}`",
        "quick_reply": "🟢 Welcome back:"
    }
}

def get_lang(message_or_call):
    code = message_or_call.from_user.language_code
    if code:
        code = code.lower()
        for lang in TRANSLATIONS:
            if code.startswith(lang):
                return lang
    return "en"

async def send_lina_voice(chat_id, text, lang='ar'):
    try:
        voice_lang = lang if lang in ['ar', 'en', 'de', 'fr', 'es', 'it'] else 'en'
        tts = gTTS(text=text, lang=voice_lang, slow=False)
        voice_path = "lina_voice.mp3"
        tts.save(voice_path)
        with open(voice_path, 'rb') as voice:
            await bot.send_voice(chat_id, voice)
        os.remove(voice_path)
    except Exception as e:
        logging.error(f"Voice error: {e}")

def get_main_keyboard(t):
    prices = get_converted_prices()
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(t["real_estate"], callback_data="real_estate"),
        InlineKeyboardButton(t["cars"], callback_data="cars"),
        InlineKeyboardButton(t["bill_elec"], callback_data="bill_elec"),
        InlineKeyboardButton(t["bill_water"], callback_data="bill_water"),
        InlineKeyboardButton(t["bill_phone"], callback_data="bill_phone"),
        InlineKeyboardButton(t["bill_tax"], callback_data="bill_tax"),
        InlineKeyboardButton(t["ledger"], callback_data="view_ledger"),
        InlineKeyboardButton(t["feedback"], callback_data="leave_feedback"),
        InlineKeyboardButton(t["services"], callback_data="services"),
        InlineKeyboardButton(t["containers"], callback_data="containers"),
        InlineKeyboardButton(t["sub"], callback_data="sub"),
        InlineKeyboardButton(t["web3"], callback_data="web3")
    )
    return keyboard

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    if message.from_user.language_code in BLOCKED_COUNTRIES:
        await message.answer(TRANSLATIONS[get_lang(message)]["blocked"])
        return

    user_states[user_id] = "main_menu"
    lang = get_lang(message)
    t = TRANSLATIONS[lang]
    
    await send_lina_voice(message.chat.id, t["voice_welcome"], lang)
    await message.answer(t["welcome"], reply_markup=get_main_keyboard(t), parse_mode="HTML")

@dp.message_handler(lambda message: not message.text.startswith('/'))
async def handle_smart_sensor(message: types.Message):
    user_id = message.from_user.id
    if message.from_user.language_code in BLOCKED_COUNTRIES:
        return

    lang = get_lang(message)
    t = TRANSLATIONS[lang]
    current_state = user_states.get(user_id, "main_menu")

    if current_state == "waiting_for_feedback":
        user_states[user_id] = "main_menu"
        user_text = message.text
        user_name = message.from_user.full_name or "مستخدم مجهول"
        try:
            admin_msg = f"🟢 **ملاحظة جديدة في بوت لينا:**\n\n👤 الاسم: {user_name}\n🆔 الآيدي: `{user_id}`\n\n💬 النص:\n_{user_text}_"
            await bot.send_message(ADMIN_CHAT_ID, admin_msg, parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Error: {e}")
        await message.answer(t["feedback_thanks"])
        return

    user_states[user_id] = "main_menu"
    await message.answer(t["quick_reply"], reply_markup=get_main_keyboard(t), parse_mode="HTML")

@dp.callback_query_handler(lambda call: True)
async def process_callbacks(call: types.CallbackQuery) -> None:
    user_id = call.from_user.id
    if call.from_user.language_code in BLOCKED_COUNTRIES:
        await call.answer("Blocked", show_alert=True)
        return

    lang = get_lang(call)
    t = TRANSLATIONS[lang]
    await call.answer()

    if call.data == "leave_feedback":
        user_states[user_id] = "waiting_for_feedback"
        await call.message.answer(t["feedback_prompt"], parse_mode="HTML")
        return

    if call.data == "web3":
        user_states[user_id] = "main_menu"
        await call.message.answer(t["web3_text"].format(wallet=METAMASK_WALLET_ADDRESS), parse_mode="Markdown")
        return

    if call.data == "sub":
        user_states[user_id] = "main_menu"
        await call.message.answer(t["stripe_text"].format(url=STRIPE_SUB_URL), parse_mode="Markdown")
        return

    if call.data == "view_ledger":
        user_states[user_id] = "main_menu"
        count = len(user_ledger.get(user_id, []))
        await call.message.answer(t["ledger_report"].format(count=count), parse_mode="HTML")
        return

    item_names = {
        "bill_elec": t["bill_elec"], "bill_water": t["bill_water"],
        "bill_phone": t["bill_phone"], "bill_tax": t["bill_tax"],
        "real_estate": t["real_estate"], "cars": t["cars"],
        "services": t["services"], "containers": t["containers"]
    }
    
    if call.data in item_names:
        pay_keyboard = InlineKeyboardMarkup()
        pay_keyboard.add(InlineKeyboardButton("🔗 اضغط هنا لإتمام الدفع (€0.50)", url=STRIPE_ONETIME_URL))
        await call.message.answer(t["payment_prompt"].format(item=item_names[call.data]), reply_markup=pay_keyboard, parse_mode="HTML")
        return

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
