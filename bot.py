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

# القاموس الشامل للّغات الست مع الزر البارز للنقاش التجاري
TRANSLATIONS = {
    "ar": {
        "welcome": "🟢 <b>أهلاً بك في بوت لينا الرسمي (منصة الأعمال الذكية)!</b>\n\n🟢 تم تفعيل نظام رصد الملاحظات والشكاوى.\n🟢 مجموعات النقاش التجاري متاحة **مجاناً** لتسهيل صفقاتكم وتنسيق الأطراف.\n\n✨ <i>اختر الخدمة المطلوبة أدناه:</i>",
        "voice_welcome": "أهلاً بك في بوت لينا، منصة الأعمال والتنسيق التجاري.",
        "blocked": "عذراً، الخدمة غير متاحة في منطقتك.",
        "real_estate": "🟢 عقارات دولية 🟢",
        "cars": "🟢 قطاع السيارات 🟢",
        "services": "🟢 خدمات عامة 🟢",
        "ledger": "🟢 السجل المحاسبي 🟢",
        "containers": "🟢 الشحن والكونتينرات 🟢",
        "support": "🟢 الدعم الفني 🟢",
        "feedback": "🟢 ترك ملاحظة أو شكوى 🟢",
        "business_group": "👥 🟢 مجموعة نقاش تجاري (مجاني) 🟢",
        "sub": "🟢 اشتراك VIP (€2.99) 🟢",
        "web3": "🟢 دفع رقمي (€0.50) 🟢",
        "bill_elec": "🟢 فاتورة الكهرباء 🟢",
        "bill_water": "🟢 فاتورة المياه 🟢",
        "bill_phone": "🟢 فاتورة الاتصالات 🟢",
        "bill_tax": "🟢 ضريبة المركبات 🟢",
        "payment_prompt": "🟢 <b>تأكيد العملية (€0.50):</b>\n\nلقد اخترت: <b>{item}</b>\n\nلإتمام الدفع بشكل آمن، يرجى النقر على الزر أدناه:",
        "feedback_prompt": "🟢 تفضل يا غالي، اكتب ملاحظتك أو شكواك، وستصل مباشرة إلى الإدارة:",
        "feedback_thanks": "🟢 تم إرسال ملاحظتك بنجاح للإدارة! شكراً لمساعدتك.",
        "ledger_report": "🟢 <b>السجل المحاسبي النظامي:</b>\n\n- الحركات المسجلة: {count}\n- الحالة: موثقة 100%.",
        "stripe_text": "🟢 <b>بوابة الدفع الآمنة (اشتراك شهري €2.99):</b>\n\n🔗 [اضغط هنا للدفع بالبطاقة]({url})",
        "web3_text": "🟢 <b>دفع عبر الكريبتو (خدمة فردية €0.50):</b>\n\n`{wallet}`",
        "quick_reply": "🟢 مرحباً بك مجدداً في بوت لينا. اختر إحدى الخدمات:",
        "group_prompt": "👥 <b>غرفة النقاش التجاري المشترك (مجاني):</b>\n\nتم فتح الجلسة بنجاح! يمكنك أنت وشركاؤك (بين شخصين أو ثلاثة) إرسال تفاصيل الفواتير والشحنات هنا، وستتدخل 'لينا' فوراً لتقديم الحلول والاقتراحات التجارية.",
        "ai_suggestion": "💡 <b>اقتراح استشاري من لينا (AI Business Hub):</b> بناءً على نقاشكم التجاري الحالي، ننصح بتوثيق البنود المالية والتأكد من توافقها مع معايير الأمان التجارية."
    },
    "en": {
        "welcome": "🟢 <b>Welcome to Lina's Official Bot (Business Hub)!</b>\n\n🟢 Free trade discussion groups enabled.\n\n✨ <i>Please select a service:</i>",
        "voice_welcome": "Welcome to Lina bot.",
        "blocked": "Sorry, service not available in your region.",
        "real_estate": "🟢 Real Estate 🟢",
        "cars": "🟢 Automotive 🟢",
        "services": "🟢 General Services 🟢",
        "ledger": "🟢 Accounting Ledger 🟢",
        "containers": "🟢 Containers 🟢",
        "support": "🟢 Digital Support 🟢",
        "feedback": "🟢 Leave Feedback / Issue 🟢",
        "business_group": "👥 🟢 Free Trade Group 🟢",
        "sub": "🟢 VIP Sub (€2.99) 🟢",
        "web3": "🟢 Crypto (€0.50) 🟢",
        "bill_elec": "🟢 Electricity 🟢",
        "bill_water": "🟢 Water 🟢",
        "bill_phone": "🟢 Phone 🟢",
        "bill_tax": "🟢 Car Tax 🟢",
        "payment_prompt": "🟢 <b>Payment Confirmation (€0.50):</b>\n\nSelected: <b>{item}</b>",
        "feedback_prompt": "🟢 Please type your feedback or complaint:",
        "feedback_thanks": "🟢 Feedback sent successfully! Thank you.",
        "ledger_report": "🟢 <b>Ledger Report:</b> Entries: {count}",
        "stripe_text": "🟢 <b>Secure Checkout (€2.99):</b> 🔗 [Pay]({url})",
        "web3_text": "🟢 <b>Web3 Payment (€0.50):</b> `{wallet}`",
        "quick_reply": "🟢 Welcome back to Lina bot. Choose your action:",
        "group_prompt": "👥 <b>Free Trade Discussion Group:</b> Secure session active. Discuss invoices and shipments; Lina will provide insights.",
        "ai_suggestion": "💡 <b>Lina AI Insight:</b> Ensure commercial terms are documented securely."
    },
    "de": {
        "welcome": "🟢 <b>Willkommen beim offiziellen Lina-Bot!</b>",
        "voice_welcome": "Willkommen beim Lina-Bot.",
        "blocked": "Entschuldigung, der Service ist in Ihrer Region nicht verfügbar.",
        "real_estate": "🟢 Immobilien 🟢",
        "cars": "🟢 Automobil 🟢",
        "services": "🟢 Allgemeine Dienstleistungen 🟢",
        "ledger": "🟢 Buchhaltung 🟢",
        "containers": "🟢 Container 🟢",
        "support": "🟢 Digitaler Support 🟢",
        "feedback": "🟢 Feedback 🟢",
        "business_group": "👥 🟢 Kostenlose Handelsgruppe 🟢",
        "sub": "🟢 VIP-Abo (€2.99) 🟢",
        "web3": "🟢 Krypto (€0.50) 🟢",
        "bill_elec": "🟢 Strom 🟢",
        "bill_water": "🟢 Wasser 🟢",
        "bill_phone": "🟢 Telefon 🟢",
        "bill_tax": "🟢 Kfz-Steuer 🟢",
        "payment_prompt": "🟢 <b>Zahlungsbestätigung (€0.50):</b> <b>{item}</b>",
        "feedback_prompt": "🟢 Feedback eingeben:",
        "feedback_thanks": "🟢 Danke!",
        "ledger_report": "🟢 <b>Bericht:</b> {count}",
        "stripe_text": "🟢 <b>Abo (€2.99):</b> 🔗 [Bezahlen]({url})",
        "web3_text": "🟢 <b>Krypto (€0.50):</b> `{wallet}`",
        "quick_reply": "🟢 Willkommen zurück:",
        "group_prompt": "👥 <b>Handelsgruppe:</b> Sitzung aktiv.",
        "ai_suggestion": "💡 <b>Lina KI-Tipp:</b> Dokumentieren Sie alle Transaktionen."
    },
    "fr": {
        "welcome": "🟢 <b>Bienvenue sur le bot de Lina !</b>",
        "voice_welcome": "Bienvenue.",
        "blocked": "Service non disponible.",
        "real_estate": "🟢 Immobilier 🟢",
        "cars": "🟢 Automobile 🟢",
        "services": "🟢 Services 🟢",
        "ledger": "🟢 Grand livre 🟢",
        "containers": "🟢 Conteneurs 🟢",
        "support": "🟢 Support 🟢",
        "feedback": "🟢 Commentaire 🟢",
        "business_group": "👥 🟢 Groupe commercial (Gratuit) 🟢",
        "sub": "🟢 VIP (€2.99) 🟢",
        "web3": "🟢 Crypto (€0.50) 🟢",
        "bill_elec": "🟢 Électricité 🟢",
        "bill_water": "🟢 Eau 🟢",
        "bill_phone": "🟢 Téléphone 🟢",
        "bill_tax": "🟢 Taxe 🟢",
        "payment_prompt": "🟢 <b>Confirmation (€0.50):</b> {item}",
        "feedback_prompt": "🟢 Saisissez votre commentaire :",
        "feedback_thanks": "🟢 Envoyé !",
        "ledger_report": "🟢 <b>Rapport :</b> {count}",
        "stripe_text": "🟢 🔗 [Payer]({url})",
        "web3_text": "🟢 `{wallet}`",
        "quick_reply": "🟢 Retour :",
        "group_prompt": "👥 <b>Groupe gratuit actif.</b>",
        "ai_suggestion": "💡 <b>Conseil IA :</b> Validez vos termes."
    },
    "es": {
        "welcome": "🟢 <b>¡Bienvenido al bot de Lina!</b>",
        "voice_welcome": "Bienvenido.",
        "blocked": "No disponible.",
        "real_estate": "🟢 Inmobiliaria 🟢",
        "cars": "🟢 Autos 🟢",
        "services": "🟢 Servicios 🟢",
        "ledger": "🟢 Libro 🟢",
        "containers": "🟢 Contenedores 🟢",
        "support": "🟢 Soporte 🟢",
        "feedback": "🟢 Feedback 🟢",
        "business_group": "👥 🟢 Grupo comercial (Gratis) 🟢",
        "sub": "🟢 VIP (€2.99) 🟢",
        "web3": "🟢 Cripto (€0.50) 🟢",
        "bill_elec": "🟢 Luz 🟢",
        "bill_water": "🟢 Agua 🟢",
        "bill_phone": "🟢 Teléfono 🟢",
        "bill_tax": "🟢 Impuesto 🟢",
        "payment_prompt": "🟢 <b>Confirmación (€0.50):</b> {item}",
        "feedback_prompt": "🟢 Escriba:",
        "feedback_thanks": "🟢 ¡Enviado!",
        "ledger_report": "🟢 <b>Informe:</b> {count}",
        "stripe_text": "🟢 🔗 [Pagar]({url})",
        "web3_text": "🟢 `{wallet}`",
        "quick_reply": "🟢 Menú:",
        "group_prompt": "👥 <b>Grupo comercial abierto.</b>",
        "ai_suggestion": "💡 <b>Sugerencia IA:</b> Mantenga el registro."
    },
    "it": {
        "welcome": "🟢 <b>Benvenuto nel bot ufficiale di Lina (Business Hub)!</b>",
        "voice_welcome": "Benvenuto.",
        "blocked": "Spiacenti, servizio non disponibile.",
        "real_estate": "🟢 Immobiliare 🟢",
        "cars": "🟢 Automotive 🟢",
        "services": "🟢 Servizi 🟢",
        "ledger": "🟢 Registro 🟢",
        "containers": "🟢 Container 🟢",
        "support": "🟢 Supporto 🟢",
        "feedback": "🟢 Feedback 🟢",
        "business_group": "👥 🟢 Gruppo Commerciale (Gratis) 🟢",
        "sub": "🟢 VIP (€2.99) 🟢",
        "web3": "🟢 Pagamento Cripto (€0.50) 🟢",
        "bill_elec": "🟢 Luce 🟢",
        "bill_water": "🟢 Acqua 🟢",
        "bill_phone": "🟢 Telefono 🟢",
        "bill_tax": "🟢 Tassa 🟢",
        "payment_prompt": "🟢 <b>Conferma (€0.50):</b> {item}",
        "feedback_prompt": "🟢 Scrivi il feedback:",
        "feedback_thanks": "🟢 Inviato!",
        "ledger_report": "🟢 <b>Registro:</b> {count}",
        "stripe_text": "🟢 🔗 [Paga]({url})",
        "web3_text": "🟢 `{wallet}`",
        "quick_reply": "🟢 Bentornato:",
        "group_prompt": "👥 <b>Gruppo di discussione commerciale avviato.</b>",
        "ai_suggestion": "💡 <b>Suggerimento AI di Lina:</b> Analisi pronta per il vostro accordo."
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
        InlineKeyboardButton(t["business_group"], callback_data="business_group"), # الزر البارز الجديد للمجموعة التجارية بين الأطراف
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

    if current_state == "in_business_group":
        # تفاعل لينا داخل مجموعة النقاش التجاري المشترك للأطراف
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

    if call.data == "business_group":
        user_states[user_id] = "in_business_group"
        await call.message.answer(t["group_prompt"], parse_mode="HTML")
        return

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
