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

# الدول المحظورة عالمياً
BLOCKED_COUNTRIES = ["ru", "ir"]

TRANSLATIONS = {
    "ar": {
        "welcome": "أهلاً وسهلاً! أنا لينا\nرسوم العملية 0.50€ - الاشتراك الشهري €2.99\nمتاحة لدفع فواتيركم (كهرباء، ماء، هاتف، ضرائب).\nشو بتحب أساعدك اليوم؟",
        "voice_welcome": "أهلاً وسهلاً بك، اختر القسم المناسب أو اطلب دفع فاتورتك.",
        "blocked": "عذراً، هذا البوت غير متاح في دولتك بناءً على القيود والحظر الدولي المفروض.",
        "real_estate": "عقارات",
        "cars": "سيارات",
        "services": "خدمات عامة",
        "bills": "💳 دفع الفواتير والضرائب",
        "containers": "كونتينرات",
        "sub": "اشتراكي €2.99",
        "web3": "دفع العملات الرقمية 0.50€",
        "bills_menu": "💳 **خدمة دفع الفواتير والضرائب:**\n\nيرجى اختيار نوع الفاتورة المراد دفعها ليقوم النظام بمساعدتك:",
        "bill_elec": "⚡ فاتورة الكهرباء",
        "bill_water": "💧 فاتورة المياه",
        "bill_phone": "📱 فاتورة الهاتف",
        "bill_tax": "🚗 ضريبة السيارة",
        "bill_selected": "لقد اخترت دفع **{bill_type}**.\n\nيرجى تزويدي برقم الحساب أو تفاصيل الفاتورة مع رسوم الخدمة لتنفيذ الطلب بعد موافقتك.",
        "web3_voice": "لإتمام الطلب، يرجى دفع رسوم فتح الطلب وقدرها خمسين سنت فقط عبر العملات الرقمية.",
        "web3_text": "💳 **الدفع عبر العملات الرقمية (Web3):**\n\n📍 **العنوان:** `{wallet}`\n🌐 **الشبكة:** {network}\n💰 **المبلغ المطلوب:** 0.50 USDT\n\nبعد الدفع، يرجى إرسال رقم العملية (Tx Hash) الذي يبدأ بـ (0x...).",
        "selected": "لقد اخترت: **{category}**.\n\nيرجى المتابعة لاختيار طريقة الدفع:"
    },
    "en": {
        "welcome": "Welcome! I am Lina\nOrder Fee €0.50 - Monthly Subscription €2.99\nAvailable to pay your bills (electricity, water, phone, taxes).\nHow can I help you today?",
        "voice_welcome": "Welcome, please choose the appropriate category or bill payment.",
        "blocked": "Sorry, this bot is not available in your country due to international sanctions and restrictions.",
        "real_estate": "Real Estate",
        "cars": "Cars",
        "services": "General Services",
        "bills": "💳 Bills & Taxes",
        "containers": "Containers",
        "sub": "Monthly Subscription €2.99",
        "web3": "Crypto Payment €0.50",
        "bills_menu": "💳 **Bills & Taxes Payment Service:**\n\nPlease select the type of bill you want to pay:",
        "bill_elec": "⚡ Electricity Bill",
        "bill_water": "💧 Water Bill",
        "bill_phone": "📱 Phone Bill",
        "bill_tax": "🚗 Car Tax",
        "bill_selected": "You have chosen to pay **{bill_type}**.\n\nPlease provide your account number or bill details along with the service fee to proceed upon your approval.",
        "web3_voice": "To complete the order, please pay the opening fee of only fifty cents via cryptocurrencies.",
        "web3_text": "💳 **Payment via Crypto (Web3):**\n\n📍 **Address:** `{wallet}`\n🌐 **Network:** {network}\n💰 **Amount Required:** 0.50 USDT\n\nAfter payment, please send the transaction hash (Tx Hash) starting with (0x...).",
        "selected": "You have selected: **{category}**.\n\nPlease proceed by choosing the payment method:"
    },
    "fr": {
        "welcome": "Bienvenue! Je suis Lina\nFrais 0,50€ - Abonnement 2,99€",
        "voice_welcome": "Bienvenue, veuillez choisir une catégorie.",
        "blocked": "Désolé, ce bot n'est pas disponible dans votre pays en raison de sanctions internationales.",
        "real_estate": "Immobilier",
        "cars": "Voitures",
        "services": "Services généraux",
        "bills": "💳 Paiement des factures",
        "containers": "Conteneurs",
        "sub": "Abonnement 2,99€",
        "web3": "Paiement Crypto 0,50€",
        "bills_menu": "💳 **Service de paiement des factures:**",
        "bill_elec": "⚡ Électricité",
        "bill_water": "💧 Eau",
        "bill_phone": "📱 Téléphone",
        "bill_tax": "🚗 Taxe",
        "bill_selected": "Vous avez choisi **{bill_type}**.",
        "web3_voice": "Veuillez payer les frais de 50 centimes.",
        "web3_text": "💳 **Paiement Crypto:** `{wallet}`",
        "selected": "Vous avez sélectionné: **{category}**."
    },
    "es": {
        "welcome": "¡Bienvenido! Soy Lina\nTarifa 0.50€ - Suscripción 2.99€",
        "voice_welcome": "Bienvenido, elija una categoría.",
        "blocked": "Lo siento, este bot no está disponible en tu país debido a sanciones internacionales.",
        "real_estate": "Inmobiliaria",
        "cars": "Coches",
        "services": "Servicios generales",
        "bills": "💳 Pago de Facturas",
        "containers": "Contenedores",
        "sub": "Suscripción 2.99€",
        "web3": "Pago Cripto 0.50€",
        "bills_menu": "💳 **Servicio de pago de facturas:**",
        "bill_elec": "⚡ Luz",
        "bill_water": "💧 Agua",
        "bill_phone": "📱 Teléfono",
        "bill_tax": "🚗 Impuesto",
        "bill_selected": "Has elegido **{bill_type}**.",
        "web3_voice": "Pague la tarifa.",
        "web3_text": "💳 **Pago Cripto:** `{wallet}`",
        "selected": "Has seleccionado: **{category}**."
    },
    "it": {
        "welcome": "Benvenuto! Sono Lina\nCommissione 0,50€ - Abbonamento 2,99€",
        "voice_welcome": "Benvenuto, scegli una categoria.",
        "blocked": "Spiacenti, questo bot non è disponibile nel tuo paese a causa di sanzioni internazionali.",
        "real_estate": "Immobiliare",
        "cars": "Auto",
        "services": "Servizi generali",
        "bills": "💳 Pagamento Bollette",
        "containers": "Contenitori",
        "sub": "Abbonamento 2,99€",
        "web3": "Pagamento Cripto 0,50€",
        "bills_menu": "💳 **Servizio bollette:**",
        "bill_elec": "⚡ Luce",
        "bill_water": "💧 Acqua",
        "bill_phone": "📱 Telefono",
        "bill_tax": "🚗 Tassa",
        "bill_selected": "Hai scelto **{bill_type}**.",
        "web3_voice": "Paga la commissione.",
        "web3_text": "💳 **Pagamento Cripto:** `{wallet}`",
        "selected": "Hai selezionato: **{category}**."
    },
    "de": {
        "welcome": "Willkommen! Ich bin Lina\nGebühr 0,50€ - Abo 2,99€",
        "voice_welcome": "Willkommen, wählen Sie eine Kategorie.",
        "blocked": "Entschuldigung, dieser Bot ist aufgrund internationaler Sanktionen in Ihrem Land nicht verfügbar.",
        "real_estate": "Immobilien",
        "cars": "Autos",
        "services": "Allgemeine Dienste",
        "bills": "💳 Rechnungszahlung",
        "containers": "Container",
        "sub": "Abo 2,99€",
        "web3": "Krypto-Zahlung 0,50€",
        "bills_menu": "💳 **Rechnungsdienst:**",
        "bill_elec": "⚡ Strom",
        "bill_water": "💧 Wasser",
        "bill_phone": "📱 Telefon",
        "bill_tax": "🚗 Steuer",
        "bill_selected": "Sie haben **{bill_type}** gewählt.",
        "web3_voice": "Zahlen Sie die Gebühr.",
        "web3_text": "💳 **Krypto-Zahlung:** `{wallet}`",
        "selected": "Sie haben ausgewählt: **{category}**."
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
    # فحص الحظر للدول المستهدفة (روسيا وإيران)
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
        InlineKeyboardButton(t["services"], callback_data="services"),
        InlineKeyboardButton(t["containers"], callback_data="containers"),
        InlineKeyboardButton(t["sub"], callback_data="sub"),
        InlineKeyboardButton(t["web3"], callback_data="web3")
    )
    
    await send_lina_voice(message.chat.id, t["voice_welcome"], lang)
    await message.answer(t["welcome"], reply_markup=keyboard)

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
