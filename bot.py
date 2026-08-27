import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from gtts import gTTS
import os

API_TOKEN = os.getenv("BOT_TOKEN")
WEB3_WALLET = os.getenv("WEB3_WALLET", "0xYourWalletAddressHere")
WEB3_NETWORK = os.getenv("WEB3_NETWORK", "BSC / ERC20")
BANK_IBAN = os.getenv("BANK_IBAN", "DE89 3704 0044 0532 2013 00")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# قواميس التتبع السياقي والحالات (الحساسات البرمجية)
user_states = {}
user_data = {}
user_ledger = {}  # السجل المحاسبي الرقمي للعمليات

BLOCKED_COUNTRIES = ["ru", "ir"]

TRANSLATIONS = {
    "ar": {
        "welcome": "أهلاً وسهلاً! أنا لينا\nرسوم العملية 0.50€ - الاشتراك الشهري €2.99\nنظام محاسبي رقمي موثق للشركات (بدون عمل أسود).\nشو بتحب أساعدك اليوم؟",
        "voice_welcome": "أهلاً وسهلاً بك، اختر الخدمة المطلوبة أو استعرض سجلك المحاسبي.",
        "blocked": "عذراً، هذا البوت غير متاح في دولتك بناءً على القيود والحظر الدولي المفروض.",
        "real_estate": "عقارات",
        "cars": "سيارات",
        "services": "خدمات عامة",
        "bills": "💳 دفع الفواتير والضرائب",
        "ledger": "📊 السجل المحاسبي والفواتير",
        "containers": "كونتينرات",
        "support": "📞 الدعم الفني الرقمي",
        "sub": "اشتراكي €2.99",
        "web3": "دفع العملات الرقمية 0.50€",
        "bills_menu": "💳 **خدمة دفع الفواتير والضرائب الموثقة:**\n\nيرجى اختيار نوع الفاتورة المراد دفعها وسجيلها محاسبياً:",
        "bill_elec": "⚡ فاتورة الكهرباء",
        "bill_water": "💧 فاتورة المياه",
        "bill_phone": "📱 فاتورة الهاتف",
        "bill_tax": "🚗 ضريبة السيارة",
        "bill_selected": "✅ **تم توثيق طلب دفع {bill_type} رقمياً بنجاح.**\n\nتم تسجيل العملية في السجل المحاسبي للشركة. يرجى إرسال تفاصيل الحساب لاستكمال السداد الآلي.",
        "ledger_report": "📊 **السجل المحاسبي الرقمي والتقارير:**\n\n- إجمالي المعاملات المسجلة: {count}\n- الحالة القانونية: موثق رقمياً (أبيض 100%)\n- جاهز لاستخراج التقارير الضريبية للشركة.",
        "web3_voice": "لإتمام الطلب، يرجى دفع رسوم فتح الطلب وقدرها خمسين سنت فقط عبر العملات الرقمية.",
        "web3_text": "💳 **الدفع عبر العملات الرقمية (Web3):**\n\n📍 **العنوان:** `{wallet}`\n🌐 **الشبكة:** {network}\n💰 **المبلغ المطلوب:** 0.50 USDT\n\nبعد الدفع، يرجى إرسال رقم العملية (Tx Hash) الذي يبدأ بـ (0x...).",
        "bank_text": "🏦 **الدفع عبر التحويل البنكي أو الآيبان:**\n\n📍 **IBAN:** `{iban}`\n💰 **المبلغ:** 0.50€\n\nيرجى إرسال إيصال التحويل بعد الإتمام.",
        "selected": "لقد اخترت: **{category}**.\n\nيرجى المتابعة لاختيار طريقة الدفع (اكتب: عملة رقمية، أو تحويل بنكي):",
        "quick_reply": "أهلاً بك! كيف يمكنني مساعدتك اليوم؟ اختر من الأزرار أدناه:"
    },
    "en": {
        "welcome": "Welcome! I am Lina\nOrder Fee €0.50 - Monthly Subscription €2.99\nDigital accounting & automated billing system.\nHow can I help you today?",
        "voice_welcome": "Welcome, please choose a service or check your ledger.",
        "blocked": "Sorry, this bot is not available in your country due to international sanctions.",
        "real_estate": "Real Estate",
        "cars": "Cars",
        "services": "General Services",
        "bills": "💳 Bills & Taxes",
        "ledger": "📊 Accounting Ledger",
        "containers": "Containers",
        "support": "📞 Digital Support",
        "sub": "Monthly Subscription €2.99",
        "web3": "Crypto Payment €0.50",
        "bills_menu": "💳 **Verified Bills & Taxes Service:**\n\nPlease select the type of bill to process:",
        "bill_elec": "⚡ Electricity Bill",
        "bill_water": "💧 Water Bill",
        "bill_phone": "📱 Phone Bill",
        "bill_tax": "🚗 Car Tax",
        "bill_selected": "✅ **{bill_type} payment request logged digitally.**\n\nRecorded in the company's ledger.",
        "ledger_report": "📊 **Digital Accounting Ledger:**\n\n- Total Logged Transactions: {count}\n- Status: Fully Verified (100% White)\n- Ready for tax reports.",
        "web3_voice": "To complete the order, please pay the opening fee of only fifty cents via cryptocurrencies.",
        "web3_text": "💳 **Payment via Crypto (Web3):**\n\n📍 **Address:** `{wallet}`\n🌐 **Network:** {network}\n💰 **Amount Required:** 0.50 USDT\n\nAfter payment, please send the transaction hash (Tx Hash) starting with (0x...).",
        "bank_text": "🏦 **Bank Transfer / IBAN Payment:**\n\n📍 **IBAN:** `{iban}`\n💰 **Amount:** 0.50€\n\nPlease send the receipt after transfer.",
        "selected": "You have selected: **{category}**.\n\nPlease proceed by choosing the payment method (Type: crypto, or bank transfer):",
        "quick_reply": "Hello! How can I help you today? Choose from the buttons below:"
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

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    user_lang = message.from_user.language_code
    if user_lang in BLOCKED_COUNTRIES:
        lang = "en" if user_lang not in TRANSLATIONS else user_lang
        await message.answer(TRANSLATIONS[lang]["blocked"])
        return

    # إعادة ضبط الحالة عند بدء محادثة جديدة
    user_states[user_id] = "main_menu"

    lang = get_lang(message)
    t = TRANSLATIONS[lang]
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(t["real_estate"], callback_data="real_estate"),
        InlineKeyboardButton(t["cars"], callback_data="cars"),
        InlineKeyboardButton(t["bills"], callback_data="bills_main"),
        InlineKeyboardButton(t["ledger"], callback_data="view_ledger"),
        InlineKeyboardButton(t["services"], callback_data="services"),
        InlineKeyboardButton(t["containers"], callback_data="containers"),
        InlineKeyboardButton(t["sub"], callback_data="sub"),
        InlineKeyboardButton(t["web3"], callback_data="web3")
    )
    
    await send_lina_voice(message.chat.id, t["voice_welcome"], lang)
    await message.answer(t["welcome"], reply_markup=keyboard)

# معالج الرسائل الذكي المزود بحساسات سياقية تتبع خطوات المستخدم
@dp.message_handler(lambda message: not message.text.startswith('/'))
async def handle_smart_sensor(message: types.Message):
    user_id = message.from_user.id
    user_lang = message.from_user.language_code
    if user_lang in BLOCKED_COUNTRIES:
        return

    lang = get_lang(message)
    t = TRANSLATIONS[lang]
    text = message.text.lower()

    # استشعار الحالة الحالية للمستخدم
    current_state = user_states.get(user_id, "main_menu")

    # إذا كان المستخدم في حالة انتظار اختيار طريقة الدفع (مثلاً بعد أن اختار عقارات أو سيارات)
    if current_state == "waiting_for_payment":
        if any(w in text for w in ["عملة", "رقمية", "crypto", "usdt", "كريبتو", "عمله"]):
            user_states[user_id] = "main_menu"  # إعادة تعيين الحالة
            await send_lina_voice(message.chat.id, t["web3_voice"], lang)
            await message.answer(
                t["web3_text"].format(wallet=WEB3_WALLET, network=WEB3_NETWORK),
                parse_mode="Markdown",
            )
            return
        elif any(w in text for w in ["تحويل", "بنك", "آيبان", "iban", "bank"]):
            user_states[user_id] = "main_menu"  # إعادة تعيين الحالة
            await message.answer(
                t["bank_text"].format(iban=BANK_IBAN),
                parse_mode="Markdown",
            )
            return

    # إذا كانت رسالة عادية جداً وليست ضمن سياق انتظار دفع
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(t["real_estate"], callback_data="real_estate"),
        InlineKeyboardButton(t["cars"], callback_data="cars"),
        InlineKeyboardButton(t["bills"], callback_data="bills_main"),
        InlineKeyboardButton(t["ledger"], callback_data="view_ledger"),
        InlineKeyboardButton(t["services"], callback_data="services"),
        InlineKeyboardButton(t["containers"], callback_data="containers"),
        InlineKeyboardButton(t["sub"], callback_data="sub"),
        InlineKeyboardButton(t["web3"], callback_data="web3")
    )
    
    await send_lina_voice(message.chat.id, t["voice_welcome"], lang)
    await message.answer(t["quick_reply"], reply_markup=keyboard)

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
        await send_lina_voice(call.message.chat.id, t["web3_voice"], lang)
        await call.message.answer(
            t["web3_text"].format(wallet=WEB3_WALLET, network=WEB3_NETWORK),
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

    if call.data == "bills_main":
        user_states[user_id] = "main_menu"
        bills_keyboard = InlineKeyboardMarkup(row_width=2)
        bills_keyboard.add(
            InlineKeyboardButton(t["bill_elec"], callback_data="bill_elec"),
            InlineKeyboardButton(t["bill_water"], callback_data="bill_water"),
            InlineKeyboardButton(t["bill_phone"], callback_data="bill_phone"),
            InlineKeyboardButton(t["bill_tax"], callback_data="bill_tax")
        )
        await call.message.answer(t["bills_menu"], reply_markup=bills_keyboard, parse_mode="Markdown")
        return

    if call.data.startswith("bill_"):
        user_states[user_id] = "main_menu"
        bill_names = {
            "bill_elec": t["bill_elec"],
            "bill_water": t["bill_water"],
            "bill_phone": t["bill_phone"],
            "bill_tax": t["bill_tax"]
        }
        b_name = bill_names.get(call.data, "Bill")
        
        if user_id not in user_ledger:
            user_ledger[user_id] = []
        user_ledger[user_id].append(b_name)

        await call.message.answer(
            t["bill_selected"].format(bill_type=b_name),
            parse_mode="Markdown"
        )
        return

    # عندما يختار المستخدم قسماً (مثل عقارات، سيارات، إلخ)
    user_data[user_id] = {"type": call.data}
    user_states[user_id] = "waiting_for_payment"  # تعيين الحساس السياقي بانتظار طريقة الدفع
    
    category_names = {
        "real_estate": t["real_estate"],
        "cars": t["cars"],
        "services": t["services"],
        "containers": t["containers"],
        "sub": t["sub"]
    }
    
    cat_name = category_names.get(call.data, "Section")

    await call.message.answer(
        t["selected"].format(category=cat_name),
        parse_mode="Markdown"
    )

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
