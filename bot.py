import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from gtts import gTTS
import os
import requests

API_TOKEN = os.getenv("BOT_TOKEN")

# رقم الآيدي الخاص بك للإدارة وتلقي الملاحظات
ADMIN_CHAT_ID = 8807102611  

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_states = {}
user_data = {}
user_ledger = {}

BLOCKED_COUNTRIES = ["ru", "ir"]

TRANSLATIONS = {
    "ar": {
        "welcome": "🟢 <b>أهلاً بك في بوت لينا (النسخة التجريبية - Test Version)!</b>\n\nاختر الخدمة أدناه لاختبار أداء المنصة:",
        "voice_welcome": "أهلاً بك في النسخة التجريبية لبوت لينا، منصة الأعمال والتنسيق التجاري.",
        "blocked": "عذراً، الخدمة غير متاحة في منطقتك.",
        "real_estate": "🟢 عقارات دولية (تجريبي) 🟢",
        "cars": "🟢 قطاع السيارات (تجريبي) 🟢",
        "services": "🟢 خدمات عامة (تجريبي) 🟢",
        "ledger": "🟢 السجل المحاسبي 🟢",
        "containers": "🟢 الشحن والكونتينرات (تجريبي) 🟢",
        "support": "🟢 الدعم الفني 🟢",
        "feedback": "🟢 ترك ملاحظة أو شكوى 🟢",
        "sub": "🧪 تجربة اشتراك VIP 🧪",
        "web3": "🧪 تجربة دفع ميتاماسك 🧪",
        "bill_elec": "🟢 فاتورة الكهرباء (تجريبي) 🟢",
        "bill_water": "🟢 فاتورة المياه (تجريبي) 🟢",
        "bill_phone": "🟢 فاتورة الاتصالات (تجريبي) 🟢",
        "bill_tax": "🟢 ضريبة المركبات (تجريبي) 🟢",
        "test_notice": "⚠️ <b>ملاحظة تجريبية:</b>\n\nلقد اخترت خدمة: <b>{item}</b>.\nهذا البوت في مرحلة الاختبار التجريبي المجاني (Test-Modus) ولا يتم تقاضي أو دفع أي أموال حقيقية حالياً.",
        "feedback_prompt": "🟢 تفضل يا غالي، اكتب ملاحظتك أو شكواك للإدارة:",
        "feedback_thanks": "🟢 تم إرسال ملاحظتك بنجاح للإدارة!",
        "ledger_report": "🟢 <b>السجل المحاسبي التجريبي:</b> الحركات المسجلة: {count}",
        "test_payment_text": "🧪 <b>بوابة الدفع التجريبية:</b>\n\nالخدمات المالية مغلقة حالياً لأن البوت يخضع للاختبار المجاني وسيتم تفعيلها رسمياً بعد التسجيل النهائي للشركة.",
        "quick_reply": "🟢 مرحباً بك مجدداً. اختر إحدى الخدمات للتجربة:"
    },
    "de": {
        "welcome": "🟢 <b>Willkommen bei Lina Bot (Testversion)!</b>\n\nWählen Sie unten einen Dienst aus, um die Plattform zu testen:",
        "voice_welcome": "Willkommen zur Testversion von Lina Bot.",
        "blocked": "Entschuldigung, dieser Dienst ist in Ihrer Region nicht verfügbar.",
        "real_estate": "🟢 Internationale Immobilien (Test) 🟢",
        "cars": "🟢 Automobilsektor (Test) 🟢",
        "services": "🟢 Allgemeine Dienste (Test) 🟢",
        "ledger": "🟢 Buchhaltungsbuch 🟢",
        "containers": "🟢 Versand & Container (Test) 🟢",
        "support": "🟢 Support 🟢",
        "feedback": "🟢 Feedback / Beschwerde 🟢",
        "sub": "🧪 VIP-Abo (Test) 🧪",
        "web3": "🧪 MetaMask-Zahlung (Test) 🧪",
        "bill_elec": "🟢 Stromrechnung (Test) 🟢",
        "bill_water": "🟢 Wasserrechnung (Test) 🟢",
        "bill_phone": "🟢 Telefonrechnung (Test) 🟢",
        "bill_tax": "🟢 Kfz-Steuer (Test) 🟢",
        "test_notice": "⚠️ <b>Test-Hinweis:</b>\n\nSie haben gewählt: <b>{item}</b>.\nDieser Bot befindet sich in der kostenlosen Testphase. Es werden derzeit keine echten Zahlungen durchgeführt.",
        "feedback_prompt": "🟢 Bitte geben Sie Ihr Feedback ein:",
        "feedback_thanks": "🟢 Vielen Dank! Ihr Feedback wurde gesendet.",
        "ledger_report": "🟢 <b>Test-Buchhaltung:</b> Registrierte Einträge: {count}",
        "test_payment_text": "🧪 <b>Test-Zahlungssystem:</b>\n\nFinanzdienste sind derzeit deaktiviert, da sich der Bot in der kostenlosen Testphase befindet.",
        "quick_reply": "🟢 Willkommen zurück. Wählen Sie eine Option zum Testen:"
    },
    "en": {
        "welcome": "🟢 <b>Welcome to Lina Bot (Test Version)!</b>\n\nSelect a service below to test the platform:",
        "voice_welcome": "Welcome to the test version of Lina bot.",
        "blocked": "Region blocked.",
        "real_estate": "🟢 Real Estate (Test) 🟢",
        "cars": "🟢 Automotive (Test) 🟢",
        "services": "🟢 General Services (Test) 🟢",
        "ledger": "🟢 Accounting Ledger 🟢",
        "containers": "🟢 Containers (Test) 🟢",
        "support": "🟢 Digital Support 🟢",
        "feedback": "🟢 Leave Feedback 🟢",
        "sub": "🧪 VIP Sub (Test) 🧪",
        "web3": "🧪 MetaMask (Test) 🧪",
        "bill_elec": "🟢 Electricity (Test) 🟢",
        "bill_water": "🟢 Water (Test) 🟢",
        "bill_phone": "🟢 Phone (Test) 🟢",
        "bill_tax": "🟢 Car Tax (Test) 🟢",
        "test_notice": "⚠️ <b>Test Notice:</b>\n\nYou selected: <b>{item}</b>.\nThis bot is in a free test mode. No real payments are processed.",
        "feedback_prompt": "🟢 Type your feedback:",
        "feedback_thanks": "🟢 Feedback sent!",
        "ledger_report": "🟢 <b>Test Ledger:</b> {count}",
        "test_payment_text": "🧪 <b>Test Payment:</b>\n\nPayment services are currently disabled during the free testing phase.",
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
            admin_msg = f"🟢 **ملاحظة جديدة في بوت لينا (تجريبي):**\n\n👤 الاسم: {user_name}\n🆔 الآيدي: `{user_id}`\n\n💬 النص:\n_{user_text}_"
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

    if call.data in ["web3", "sub"]:
        user_states[user_id] = "main_menu"
        await call.message.answer(t["test_payment_text"], parse_mode="HTML")
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
        await call.message.answer(t["test_notice"].format(item=item_names[call.data]), parse_mode="HTML")
        return

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
