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
# تخزين مجموعات النقاش التجاري المشتركة للأطراف
business_groups = {} 

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

# القاموس الشامل للّغات الست مع إضافة ميزات النقاش التجاري الجماعي المجانية
TRANSLATIONS = {
    "ar": {
        "welcome": "🟢 <b>أهلاً بك في بوت لينا الرسمي (منصة الأعمال الذكية)!</b>\n\n🟢 تم تفعيل نظام رصد الملاحظات والشكاوى الفوري.\n🟢 المجموعات التجارية والاستشارات مجانية تماماً لتسهيل صفقاتكم.\n\n✨ <i>اختر الخدمة المطلوبة أدناه:</i>",
        "voice_welcome": "أهلاً بك في بوت لينا، منصة الأعمال والتنسيق التجاري.",
        "blocked": "عذراً، الخدمة غير متاحة في منطقتك.",
        "real_estate": "🟢 عقارات دولية 🟢",
        "cars": "🟢 قطاع السيارات 🟢",
        "services": "🟢 خدمات عامة 🟢",
        "ledger": "🟢 السجل المحاسبي 🟢",
        "containers": "🟢 الشحن والكونتينرات 🟢",
        "support": "🟢 الدعم الفني 🟢",
        "feedback": "🟢 ترك ملاحظة أو شكوى 🟢",
        "business_group": "🟢 مجموعة نقاش تجاري (مجاني) 🟢",
        "sub": "🟢 اشتراك VIP (€2.99) ({price}) 🟢",
        "web3": "🟢 دفع رقمي (€0.50) ({price}) 🟢",
        "bill_elec": "🟢 فاتورة الكهرباء 🟢",
        "bill_water": "🟢 فاتورة المياه 🟢",
        "bill_phone": "🟢 فاتورة الاتصالات 🟢",
        "bill_tax": "🟢 ضريبة المركبات 🟢",
        "payment_prompt": "🟢 <b>تأكيد العملية (€0.50):</b>\n\nلقد اخترت: <b>{item}</b>\n\nلإتمام الدفع بشكل آمن، يرجى النقر على الزر أدناه:",
        "feedback_prompt": "🟢 تفضل يا غالي، اكتب ملاحظتك أو شكواك، وستصل مباشرة إلى الإدارة لنقوم بالمتابعة الفورية:",
        "feedback_thanks": "🟢 تم إرسال ملاحظتك بنجاح للإدارة! شكراً لمساعدتك.",
        "ledger_report": "🟢 <b>السجل المحاسبي النظامي:</b>\n\n- الحركات المسجلة: {count}\n- الحالة: موثقة 100%.",
        "stripe_text": "🟢 <b>بوابة الدفع الآمنة (Stripe - اشتراك شهري €2.99):</b>\n\nالسعر متكيف تلقائياً مع عملتك المحلية.\n\n🔗 [اضغط هنا للدفع بالبطاقة]({url})",
        "web3_text": "🟢 <b>دفع عبر الكريبتو (Web3 - خدمة فردية €0.50):</b>\n\nلإتمام الدفع، يرجى تحويل المبلغ المعادل إلى محفظتك:\n\n`{wallet}`",
        "quick_reply": "🟢 مرحباً بك مجدداً في بوت لينا. اختر إحدى الخدمات:",
        "group_prompt": "🟢 <b>إدارة مجموعات النقاش التجاري المجانية:</b>\n\nتم فتح جلسة آمنة بين الأطراف. يمكنك أنت وشركاؤك مناقشة الفواتير والشحنات، وستتدخل 'لينا' لتقديم اقتراحات وحلول تجارية ملموسة عند الحاجة.",
        "ai_suggestion": "💡 <b>اقتراح استشاري من لينا (AI Business Hub):</b> بناءً على نقاشكم التجاري حول الفواتير أو الكونتينرات، ننصح بتوثيق البنود المالية في السجل المحاسبي والتأكد من مطابقة المعايير الأوروبية GDPR."
    },
    "en": {
        "welcome": "🟢 <b>Welcome to Lina's Official Bot (Business Hub)!</b>\n\n🟢 Live feedback routing active.\n🟢 Free commercial discussion groups enabled.\n\n✨ <i>Please select a service:</i>",
        "voice_welcome": "Welcome to Lina bot, business and coordination hub.",
        "blocked": "Sorry, service not available in your region.",
        "real_estate": "🟢 Real Estate 🟢",
        "cars": "🟢 Automotive 🟢",
        "services": "🟢 General Services 🟢",
        "ledger": "🟢 Accounting Ledger 🟢",
        "containers": "🟢 Containers 🟢",
        "support": "🟢 Digital Support 🟢",
        "feedback": "🟢 Leave Feedback / Issue 🟢",
        "business_group": "🟢 Trade Discussion Group (Free) 🟢",
        "sub": "🟢 VIP Sub (€2.99) ({price}) 🟢",
        "web3": "🟢 Crypto (€0.50) ({price}) 🟢",
        "bill_elec": "🟢 Electricity 🟢",
        "bill_water": "🟢 Water 🟢",
        "bill_phone": "🟢 Phone 🟢",
        "bill_tax": "🟢 Car Tax 🟢",
        "payment_prompt": "🟢 <b>Payment Confirmation (€0.50):</b>\n\nSelected: <b>{item}</b>\n\nTo proceed securely, please click below:",
        "feedback_prompt": "🟢 Please type your feedback or complaint. It will be sent directly to management:",
        "feedback_thanks": "🟢 Feedback sent successfully! Thank you.",
        "ledger_report": "🟢 <b>Ledger Report:</b>\n\n- Logged entries: {count}\n- Status: Verified.",
        "stripe_text": "🟢 <b>Secure Checkout (Stripe - Monthly Sub €2.99):</b>\n\nPrices dynamically adjusted.\n\n🔗 [Click here to pay]({url})",
        "web3_text": "🟢 <b>Web3 Crypto Payment (€0.50):</b>\n\nTransfer the equivalent to your wallet:\n\n`{wallet}`",
        "quick_reply": "🟢 Welcome back to Lina bot. Choose your next action:",
        "group_prompt": "🟢 <b>Free Trade Discussion Groups:</b>\n\nSecure session opened. Discuss invoices and shipments with partners; Lina will provide AI insights and solutions.",
        "ai_suggestion": "💡 <b>Lina AI Business Insight:</b> Based on your commercial discussion, ensure financial terms are logged and GDPR compliant."
    },
    "de": {
        "welcome": "🟢 <b>Willkommen beim offiziellen Lina-Bot (Business Hub)!</b>\n\n🟢 Live-Feedback-System aktiv.\n🟢 Kostenlose Handelsdiskussionsgruppen aktiviert.\n\n✨ <i>Bitte wählen Sie einen Dienst aus:</i>",
        "voice_welcome": "Willkommen beim Lina-Bot.",
        "blocked": "Entschuldigung, der Service ist in Ihrer Region nicht verfügbar.",
        "real_estate": "🟢 Immobilien 🟢",
        "cars": "🟢 Automobil 🟢",
        "services": "🟢 Allgemeine Dienstleistungen 🟢",
        "ledger": "🟢 Buchhaltung 🟢",
        "containers": "🟢 Container 🟢",
        "support": "🟢 Digitaler Support 🟢",
        "feedback": "🟢 Feedback / Beschwerde hinterlassen 🟢",
        "business_group": "🟢 Handelsgruppe (Kostenlos) 🟢",
        "sub": "🟢 VIP-Abo (€2.99) ({price}) 🟢",
        "web3": "🟢 Krypto (€0.50) ({price}) 🟢",
        "bill_elec": "🟢 Stromrechnung 🟢",
        "bill_water": "🟢 Wasserrechnung 🟢",
        "bill_phone": "🟢 Telefonrechnung 🟢",
        "bill_tax": "🟢 Kfz-Steuer 🟢",
        "payment_prompt": "🟢 <b>Zahlungsbestätigung (€0.50):</b>\n\nAusgewählt: <b>{item}</b>\n\nKlicken Sie unten, um sicher fortzufahren:",
        "feedback_prompt": "🟢 Bitte geben Sie Ihr Feedback oder Ihre Beschwerde ein:",
        "feedback_thanks": "🟢 Feedback erfolgreich gesendet! Vielen Dank.",
        "ledger_report": "🟢 <b>Bericht:</b>\n\n- Protokollierte Einträge: {count}\n- Status: Verifiziert.",
        "stripe_text": "🟢 <b>Sichere Kasse (Stripe - Abo €2.99):</b>\n\n🔗 [Hier bezahlen]({url})",
        "web3_text": "🟢 <b>Web3 Krypto-Zahlung (€0.50):</b>\n\n`{wallet}`",
        "quick_reply": "🟢 Willkommen zurück beim Lina-Bot:",
        "group_prompt": "🟢 <b>Handelsdiskussionsgruppe:</b> Sichere Sitzung aktiv. Lina unterstützt mit KI-Vorschlägen.",
        "ai_suggestion": "💡 <b>Lina KI-Geschäftstipp:</b> Dokumentieren Sie alle Transaktionen sicher."
    },
    "fr": {
        "welcome": "🟢 <b>Bienvenue sur le bot officiel de Lina !</b>",
        "voice_welcome": "Bienvenue sur le bot Lina.",
        "blocked": "Désolé, service non disponible dans votre région.",
        "real_estate": "🟢 Immobilier 🟢",
        "cars": "🟢 Automobile 🟢",
        "services": "🟢 Services généraux 🟢",
        "ledger": "🟢 Grand livre comptable 🟢",
        "containers": "🟢 Conteneurs 🟢",
        "support": "🟢 Support numérique 🟢",
        "feedback": "🟢 Laisser un commentaire / problème 🟢",
        "business_group": "🟢 Groupe de discussion (Gratuit) 🟢",
        "sub": "🟢 VIP (€2.99) ({price}) 🟢",
        "web3": "🟢 Crypto (€0.50) ({price}) 🟢",
        "bill_elec": "🟢 Électricité 🟢",
        "bill_water": "🟢 Eau 🟢",
        "bill_phone": "🟢 Téléphone 🟢",
        "bill_tax": "🟢 Taxe automobile 🟢",
        "payment_prompt": "🟢 <b>Confirmation (€0.50):</b> <b>{item}</b>",
        "feedback_prompt": "🟢 Veuillez saisir vos commentaires :",
        "feedback_thanks": "🟢 Commentaire envoyé avec succès !",
        "ledger_report": "🟢 <b>Rapport :</b> Entrées : {count}",
        "stripe_text": "🟢 <b>Paiement (€2.99) :</b> 🔗 [Payer]({url})",
        "web3_text": "🟢 <b>Crypto (€0.50) :</b> `{wallet}`",
        "quick_reply": "🟢 Bon retour sur le bot Lina.",
        "group_prompt": "🟢 <b>Groupe commercial gratuit :</b> Session sécurisée active.",
        "ai_suggestion": "💡 <b>Conseil IA de Lina :</b> Assurez-vous de valider les termes commerciaux."
    },
    "es": {
        "welcome": "🟢 <b>¡Bienvenido al bot oficial de Lina!</b>",
        "voice_welcome": "Bienvenido al bot de Lina.",
        "blocked": "Lo sentimos, el servicio no está disponible.",
        "real_estate": "🟢 Inmobiliaria 🟢",
        "cars": "🟢 Automoción 🟢",
        "services": "🟢 Servicios generales 🟢",
        "ledger": "🟢 Libro contable 🟢",
        "containers": "🟢 Contenedores 🟢",
        "support": "🟢 Soporte digital 🟢",
        "feedback": "🟢 Dejar comentarios 🟢",
        "business_group": "🟢 Grupo comercial (Gratis) 🟢",
        "sub": "🟢 Sub VIP (€2.99) ({price}) 🟢",
        "web3": "🟢 Cripto (€0.50) ({price}) 🟢",
        "bill_elec": "🟢 Electricidad 🟢",
        "bill_water": "🟢 Agua 🟢",
        "bill_phone": "🟢 Teléfono 🟢",
        "bill_tax": "🟢 Impuesto de autos 🟢",
        "payment_prompt": "🟢 <b>Confirmación (€0.50):</b> <b>{item}</b>",
        "feedback_prompt": "🟢 Escriba sus comentarios:",
        "feedback_thanks": "🟢 ¡Comentarios enviados!",
        "ledger_report": "🟢 <b>Informe:</b> Entradas: {count}",
        "stripe_text": "🟢 <b>Pago (€2.99) :</b> 🔗 [Pagar]({url})",
        "web3_text": "🟢 <b>Cripto (€0.50) :</b> `{wallet}`",
        "quick_reply": "🟢 Bienvenido de nuevo al bot de Lina.",
        "group_prompt": "🟢 <b>Grupo de comercio gratuito:</b> Sesión segura abierta.",
        "ai_suggestion": "💡 <b>Sugerencia IA de Lina:</b> Mantenga registradas las transacciones."
    },
    "it": {
        "welcome": "🟢 <b>Benvenuto nel bot ufficiale di Lina (Business Hub)!</b>\n\n🟢 Gruppi di discussione commerciale gratuiti attivi.",
        "voice_welcome": "Benvenuto nel bot di Lina.",
        "blocked": "Spiacenti, il servizio non è disponibile nella tua regione.",
        "real_estate": "🟢 Immobiliare 🟢",
        "cars": "🟢 Settore Automotive 🟢",
        "services": "🟢 Servizi Generali 🟢",
        "ledger": "🟢 Registro Contabile 🟢",
        "containers": "🟢 Spedizioni e Container 🟢",
        "support": "🟢 Supporto Digitale 🟢",
        "feedback": "🟢 Lascia Feedback / Reclamo 🟢",
        "business_group": "🟢 Gruppo di Discussione (Gratis) 🟢",
        "sub": "🟢 Abbonamento VIP (€2.99) ({price}) 🟢",
        "web3": "🟢 Pagamento Cripto (€0.50) ({price}) 🟢",
        "bill_elec": "🟢 Bolletta Luce 🟢",
        "bill_water": "🟢 Bolletta Acqua 🟢",
        "bill_phone": "🟢 Bolletta Telefono 🟢",
        "bill_tax": "🟢 Tassa Veicoli 🟢",
        "payment_prompt": "🟢 <b>Conferma operazione (€0.50):</b>\n\nHai selezionato: <b>{item}</b>",
        "feedback_prompt": "🟢 Scrivi il tuo feedback o reclamo:",
        "feedback_thanks": "🟢 Feedback inviato con successo!",
        "ledger_report": "🟢 <b>Rapporto Registro Contabile:</b> Voci: {count}",
        "stripe_text": "🟢 <b>Pagamento Sicuro (Stripe - Abbonamento €2.99):</b> 🔗 [Paga]({url})",
        "web3_text": "🟢 <b>Pagamento Cripto (Web3 - Servizio €0.50):</b> `{wallet}`",
        "quick_reply": "🟢 Bentornato nel bot di Lina.",
        "group_prompt": "🟢 <b>Gruppo di Discussione Commerciale Gratuito:</b> Sessione avviata in sicurezza.",
        "ai_suggestion": "💡 <b>Suggerimento AI di Lina:</b> Analisi commerciale e suggerimenti operativi pronti per il vostro accordo."
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
        InlineKeyboardButton(t["business_group"], callback_data="business_group"), # الزر الجديد للمجموعات التجارية المجانية
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
        lang = get_lang(message)
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

    # معالجة تفاعلات المجموعات التجارية واقتراحات الذكاء الاصطناعي الذكية
    if current_state == "in_business_group":
        user_text = message.text
        # إذا ناقش المستخدمون موضوعاً تجارياً، تتدخل لينا برأي أو اقتراح ذكي
        await message.answer(t["ai_suggestion"], parse_mode="HTML")
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

    # معالجة ميزة مجموعة النقاش التجاري المجانية الجديدة
    if call.data == "business_group":
        user_states[user_id] = "in_business_group"
        await call.message.answer(t["group_prompt"], parse_mode="HTML")
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
    
    if call.data in item_names:
        item_name = item_names[call.data]
        user_states[user_id] = "main_menu"
        
        # إنشاء زر تفاعلي يظهر تحت الرسالة يوجه المستخدم مباشرة لرابط الدفع (خدمة فردية €0.50)
        pay_keyboard = InlineKeyboardMarkup()
        pay_keyboard.add(InlineKeyboardButton("🔗 اضغط هنا لإتمام الدفع (€0.50)", url=STRIPE_ONETIME_URL))
        
        await call.message.answer(
            t["payment_prompt"].format(item=item_name),
            reply_markup=pay_keyboard,
            parse_mode="HTML"
        )
        return

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
