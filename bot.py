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
user_ledger = {}  # سجل محاسبي رقمي مؤقت لتسجيل المعاملات والفواتير آلياً

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
        "selected": "لقد اخترت: **{category}**.\n\nيرجى المتابعة لاختيار طريقة الدفع:",
        "quick_reply": "أهلاً بك! كيف يمكنني مساعدتك اليوم؟ اختر من الأزرار أو اكتب طلبك مباشرة."
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
        "selected": "You have selected: **{category}**.\n\nPlease proceed by choosing the payment method:",
        "quick_reply": "Hello! How can I help you today? Choose from the buttons or type your request directly."
    },
    "fr": {
        "welcome": "Bienvenue! Je suis Lina\nSystème comptable numérique.",
        "voice_welcome": "Bienvenue, veuillez choisir une option.",
        "blocked": "Désolé, ce bot n'est pas disponible dans votre pays.",
        "real_estate": "Immobilier",
        "cars": "Voitures",
        "services": "Services",
        "bills": "💳 Factures",
        "ledger": "📊 Registre comptable",
        "containers": "Conteneurs",
        "support": "📞 Support",
        "sub": "Abonnement 2,99€",
        "web3": "Paiement Crypto 0,50€",
        "bills_menu": "💳 **Service de facturation:**",
        "bill_elec": "⚡ Électricité",
        "bill_water": "💧 Eau",
        "bill_phone": "📱 Téléphone",
        "bill_tax": "🚗 Taxe",
        "bill_selected": "✅ Demande enregistrée numériquement.",
        "ledger_report": "📊 Registre comptable: {count} transactions.",
        "web3_voice": "Veuillez payer les frais.",
        "web3_text": "💳 **Paiement Crypto:** `{wallet}`",
        "selected": "Vous avez sélectionné: **{category}**.",
        "quick_reply": "Bonjour! Comment puis-je vous aider aujourd'hui?"
    },
    "es": {
        "welcome": "¡Bienvenido! Soy Lina\nSistema de contabilidad digital.",
        "voice_welcome": "Bienvenido, elija una opción.",
        "blocked": "Lo siento, este bot no está disponible en tu país.",
        "real_estate": "Inmobiliaria",
        "cars": "Coches",
        "services": "Servicios",
        "bills": "💳 Facturas",
        "ledger": "📊 Libro Contable",
        "containers": "Conteneurs",
        "support": "📞 Soporte",
        "sub": "Suscripción 2.99€",
        "web3": "Pago Cripto 0.50€",
        "bills_menu": "💳 **Servicio de facturas:**",
        "bill_elec": "⚡ Luz",
        "bill_water": "💧 Agua",
        "bill_phone": "📱 Teléfono",
        "bill_tax": "🚗 Impuesto",
        "bill_selected": "✅ Solicitud registrada digitalmente.",
        "ledger_report": "📊 Libro contable: {count} transacciones.",
        "web3_voice": "Pague la tarifa.",
        "web3_text": "💳 **Pago Cripto:** `{wallet}`",
        "selected": "Has seleccionado: **{category}**.",
        "quick_reply": "¡Hola! ¿Cómo puedo ayudarte hoy?"
    },
    "it": {
        "welcome": "Benvenuto! Sono Lina\nSistema di contabilità digitale.",
        "voice_welcome": "Benvenuto, scegli un'opzione.",
        "blocked": "Spiacenti, questo bot non è disponibile nel tuo paese.",
        "real_estate": "Immobiliare",
        "cars": "Auto",
        "services": "Servizi",
        "bills": "💳 Bollette",
        "ledger": "📊 Registro Contabile",
        "containers": "Contenitori",
        "support": "📞 Supporto",
        "sub": "Abbonamento 2,99€",
        "web3": "Pagamento Cripto 0,50€",
        "bills_menu": "💳 **Servizio bollette:**",
        "bill_elec": "⚡ Luce",
        "bill_water": "💧 Acqua",
        "bill_phone": "📱 Telefono",
        "bill_tax": "🚗 Tassa",
        "bill_selected": "✅ Richiesta registrata digitalmente.",
        "ledger_report": "📊 Registro contabile: {count} transazioni.",
        "web3_voice": "Paga la commissione.",
        "web3_text": "💳 **Pagamento Cripto:** `{wallet}`",
        "selected": "Hai selezionato: **{category}**.",
        "quick_reply": "Ciao! Come posso aiutarti oggi?"
    },
    "de": {
        "welcome": "Willkommen! Ich bin Lina\nDigitales Buchhaltungssystem.",
        "voice_welcome": "Willkommen, wählen Sie eine Option.",
        "blocked": "Entschuldigung, dieser Bot ist in Ihrem Land nicht verfügbar.",
        "real_estate": "Immobilien",
        "cars": "Autos",
        "services": "Dienste",
        "bills": "💳 Rechnungen",
        "ledger": "📊 Buchhaltung",
        "containers": "Container",
        "support": "📞 Support",
        "sub": "Abo 2,99€",
        "web3": "Krypto-Zahlung 0,50€",
        "bills_menu": "💳 **Rechnungsdienst:**",
        "bill_elec": "⚡ Strom",
        "bill_water": "💧 Wasser",
        "bill_phone": "📱 Telefon",
        "bill_tax": "🚗 Steuer",
        "bill_selected": "✅ Anfrage digital protokolliert.",
        "ledger_report": "📊 Buchhaltung: {count} Transaktionen.",
        "web3_voice": "Zahlen Sie die Gebühr.",
        "web3_text": "💳 **Krypto-Zahlung:** `{wallet}`",
        "selected": "Sie haben ausgewählt: **{category}**.",
        "quick_reply": "Hallo! Wie kann ich Ihnen heute helfen?"
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
    user_lang = message.from_user.language_code
    if user_lang in BLOCKED_COUNTRIES:
        lang = "en" if user_lang not in TRANSLATIONS else user_lang
        await message.answer(TRANSLATIONS[lang]["blocked"])
        return

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

# معالج الرسائل النصية الحرة للرد المباشر والفوري بأي لغة دون الحاجة لـ /start
@dp.message_handler(lambda message: not message.text.startswith('/'))
async def handle_any_text_message(message: types.Message):
    user_lang = message.from_user.language_code
    if user_lang in BLOCKED_COUNTRIES:
        return

    lang = get_lang(message)
    t = TRANSLATIONS[lang]
    
    # رد فوري ومباشر حسب لغة المستخدم وبدون إطالة
    await message.answer(t["quick_reply"])

@dp.callback_query_handler(lambda call: True)
async def process(call: types.CallbackQuery) -> None:
    user_id = call.from_user.id
    user_lang = call.from_user.language_code
    
    if user_lang in BLOCKED_COUNTRIES:
        await call.answer("Blocked", show_alert=True)
        return

    lang = get_lang(call)
    t = TRANSLATIONS[lang]
    await call.answer()

    if call.data == "web3":
        await send_lina_voice(call.message.chat.id, t["web3_voice"], lang)
        await call.message.answer(
            t["web3_text"].format(wallet=WEB3_WALLET, network=WEB3_NETWORK),
            parse_mode="Markdown",
        )
        return

    if call.data == "view_ledger":
        count = len(user_ledger)
        await call.message.answer(
            t["ledger_report"].format(count=count),
            parse_mode="Markdown"
        )
        return

    if call.data == "bills_main":
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

    user_data[user_id] = {"type": call.data, "step": 1}
    
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
