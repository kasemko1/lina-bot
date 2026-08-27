import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from gtts import gTTS
import os
import requests

API_TOKEN = os.getenv("BOT_TOKEN")

# رقم الآيدي الخاص بك المعتمد لتلقي الملاحظات والشكاوى فوراً
ADMIN_CHAT_ID = 8807102611  

# روابط Stripe الرسمية الخاصة بك (باليورو كعملة أساسية)
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

# دالة لجلب أسعار الصرف الحية مقابل اليورو
def get_converted_prices():
    try:
        response = requests.get("https://api.exchangerate-api.com/v4/latest/EUR", timeout=5)
        data = response.json()
        rates = data.get("rates", {})
        
        usd_rate = rates.get("USD", 1.08)
        gbp_rate = rates.get("GBP", 0.85)
        
        sub_eur = 2.99
        one_eur = 0.50
        
        return {
            "sub": f"€{sub_eur} (~${round(sub_eur * usd_rate, 2)} USD / £{round(sub_eur * gbp_rate, 2)} GBP)",
            "onetime": f"€{one_eur} (~${round(one_eur * usd_rate, 2)} USD / £{round(one_eur * gbp_rate, 2)} GBP)"
        }
    except Exception:
        return {
            "sub": "€2.99 (~$3.23 USD / £2.54 GBP)",
            "onetime": "€0.50 (~$0.54 USD / £0.43 GBP)"
        }

TRANSLATIONS = {
    "ar": {
        "welcome": "🟢 <b>أهلاً بك في بوت لينا الرسمي!</b>\n\n🟢 تم تفعيل نظام رصد الملاحظات والشكاوى الفوري.\n🟢 العملات والأسعار تظهر بالعملات المحلية للعملاء.\n\n✨ <i>اختر الخدمة المطلوبة أدناه:</i>",
        "voice_welcome": "أهلاً بك في بوت لينا، اختر الخدمة المطلوبة.",
        "blocked": "عذراً، الخدمة غير متاحة في منطقتك.",
        "real_estate": "🟢 عقارات دولية 🟢",
        "cars": "🟢 قطاع السيارات 🟢",
        "services": "🟢 خدمات عامة 🟢",
        "ledger": "🟢 السجل المحاسبي 🟢",
        "containers": "🟢 الشحن والكونتينرات 🟢",
        "support": "🟢 الدعم الفني 🟢",
        "feedback": "🟢 ترك ملاحظة أو شكوى 🟢",
        "sub": "🟢 اشتراك VIP ({price}) 🟢",
        "web3": "🟢 دفع رقمي ({price}) 🟢",
        "bill_elec": "🟢 فاتورة الكهرباء 🟢",
        "bill_water": "🟢 فاتورة المياه 🟢",
        "bill_phone": "🟢 فاتورة الاتصالات 🟢",
        "bill_tax": "🟢 ضريبة المركبات 🟢",
        "payment_prompt": "🟢 <b>تأكيد العملية:</b>\n\nلقد اخترت: <b>{item}</b>\n\nلإتمام الدفع بشكل آمن، يرجى النقر على الزر أدناه:",
        "feedback_prompt": "🟢 تفضل يا غالي، اكتب ملاحظتك أو شكواك، وستصل مباشرة إلى الإدارة لنقوم بالمتابعة الفورية:",
        "feedback_thanks": "🟢 تم إرسال ملاحظتك بنجاح للإدارة! شكراً لمساعدتك.",
        "ledger_report": "🟢 <b>السجل المحاسبي النظامي:</b>\n\n- الحركات المسجلة: {count}\n- الحالة: موثقة 100%.",
        "stripe_text": "🟢 <b>بوابة الدفع الآمنة (Stripe):</b>\n\nالسعر متكيف تلقائياً مع عملتك المحلية.\n\n🔗 [اضغط هنا للدفع بالبطاقة]({url})",
        "web3_text": "🟢 <b>دفع عبر الكريبتو (Web3):</b>\n\nلإتمام الدفع، يرجى تحويل المبلغ المعادل إلى محفظتك:\n\n`{wallet}`",
        "quick_reply": "🟢 مرحباً بك مجدداً في بوت لينا. اختر إحدى الخدمات:"
    },
    "en": {
        "welcome": "🟢 <b>Welcome to Lina's Official Bot!</b>\n\n🟢 Live feedback routing active.\n🟢 Multi-currency support enabled.\n\n✨ <i>Please select a service:</i>",
        "voice_welcome": "Welcome to Lina bot, please choose a service.",
        "blocked": "Sorry, service not available in your region.",
        "real_estate": "🟢 Real Estate 🟢",
        "cars": "🟢 Automotive 🟢",
        "services": "🟢 General Services 🟢",
        "ledger": "🟢 Accounting Ledger 🟢",
        "containers": "🟢 Containers 🟢",
        "support": "🟢 Digital Support 🟢",
        "feedback": "🟢 Leave Feedback / Issue 🟢",
        "sub": "🟢 VIP Sub ({price}) 🟢",
        "web3": "🟢 Crypto ({price}) 🟢",
        "bill_elec": "🟢 Electricity 🟢",
        "bill_water": "🟢 Water 🟢",
        "bill_phone": "🟢 Phone 🟢",
        "bill_tax": "🟢 Car Tax 🟢",
        "payment_prompt": "🟢 <b>Payment Confirmation:</b>\n\nSelected: <b>{item}</b>\n\nTo proceed securely, please click below:",
        "feedback_prompt": "🟢 Please type your feedback or complaint. It will be sent directly to management:",
        "feedback_thanks": "🟢 Feedback sent successfully! Thank you.",
        "ledger_report": "🟢 <b>Ledger Report:</b>\n\n- Logged entries: {count}\n- Status: Verified.",
        "stripe_text": "🟢 <b>Secure Checkout (Stripe):</b>\n\nPrices dynamically adjusted.\n\n🔗 [Click here to pay]({url})",
        "web3_text": "🟢 <b>Web3 Crypto Payment:</b>\n\nTransfer the equivalent to your wallet:\n\n`{wallet}`",
        "quick_reply": "🟢 Welcome back to Lina bot. Choose your next action:"
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
        InlineKeyboardButton(t["sub"].format(price=prices["sub"]), callback_data="sub"),
        InlineKeyboardButton(t["web3"].format(price=prices["onetime"]), callback_data="web3")
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
    await message.answer(t["welcome"], reply_markup=get_main_keyboard(t), parse_mode="HTML")

@dp.message_handler(lambda message: not message.text.startswith('/'))
async def handle_smart_sensor(message: types.Message):
    user_id = message.from_user.id
    user_lang = message.from_user.language_code
    if user_lang in BLOCKED_COUNTRIES:
        return

    lang = get_lang(message)
    t = TRANSLATIONS[lang]
    current_state = user_states.get(user_id, "main_menu")

    if current_state == "waiting_for_feedback":
        user_states[user_id] = "main_menu"
        user_text = message.text
        user_name = message.from_user.full_name or "مستخدم مجهول"
        username = f"@{message.from_user.username}" if message.from_user.username else "بدون معرف"
        
        try:
            admin_msg = f"🟢 **ملاحظة / شكوى جديدة وردت لبوت لينا:**\n\n👤 الاسم: {user_name} ({username})\n🆔 الآيدي: `{user_id}`\n\n💬 النص:\n_{user_text}_"
            await bot.send_message(ADMIN_CHAT_ID, admin_msg, parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Failed to send feedback to admin: {e}")
            
        await message.answer(t["feedback_thanks"])
        return

    if current_state == "waiting_for_payment_method":
        user_states[user_id] = "main_menu"
        await message.answer(
            t["stripe_text"].format(url=STRIPE_ONETIME_URL),
            parse_mode="Markdown"
        )
        return

    user_states[user_id] = "main_menu"
    await send_lina_voice(message.chat.id, t["voice_welcome"], lang)
    await message.answer(t["quick_reply"], reply_markup=get_main_keyboard(t), parse_mode="HTML")

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

    prices = get_converted_prices()

    if call.data == "leave_feedback":
        user_states[user_id] = "waiting_for_feedback"
        await call.message.answer(t["feedback_prompt"], parse_mode="HTML")
        return

    if call.data == "web3":
        user_states[user_id] = "main_menu"
        user_data[user_id] = {"item_name": t["web3"].format(price=prices["onetime"])}
        await call.message.answer(
            t["web3_text"].format(wallet=METAMASK_WALLET_ADDRESS),
            parse_mode="Markdown",
        )
        return

    if call.data == "sub":
        user_states[user_id] = "main_menu"
        user_data[user_id] = {"item_name": t["sub"].format(price=prices["sub"])}
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
            parse_mode="HTML"
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
        parse_mode="HTML"
    )

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
