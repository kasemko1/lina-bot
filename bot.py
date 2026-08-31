
import logging
import json
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_CHAT_ID = 8807102611  

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_states = {}
user_data = {}
user_ledger = {}
verified_users = set()  # قائمة المستخدمين الذين أكملوا التحقق (KYC)

DATA_FILE = "bot_data.json"
user_interactions = set()
early_bird_users = set()
action_counter = {"clicks": 0}
EARLY_BIRD_LIMIT = 500

if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            saved_data = json.load(f)
            user_interactions = set(saved_data.get("users", []))
            early_bird_users = set(saved_data.get("early_birds", []))
            verified_users = set(saved_data.get("verified_users", []))
            action_counter = {"clicks": saved_data.get("clicks", 0)}
    except Exception as e:
        logging.error(f"Error loading saved data: {e}")

def save_data():
    try:
        data = {
            "users": list(user_interactions),
            "early_birds": list(early_bird_users),
            "verified_users": list(verified_users),
            "clicks": action_counter["clicks"]
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Error saving data: {e}")

BLOCKED_COUNTRIES = ["ru", "ir"]

TRANSLATIONS = {
    "ar": {
        "welcome": "🟢 <b>أهلاً بك في بوت لينا (منصة الأعمال الذكية)!</b>\n\n⚠️ <i>ملاحظة هامة: البوت حالياً في المرحلة التجريبية (لمدة 3 أسابيع إلى شهر)، ولن يتم تفعيل الخدمات المدفوعة أو الإطلاق الرسمي والنظامي الكامل إلا بعد استكمال كافة الإجراءات وتأسيس الشركة بشكل رسمي وقانوني في ألمانيا.</i>\n\nاختر الخدمة أو طريقة الدفع المطلوبة أدناه:",
        "blocked": "عذراً، الخدمة غير متاحة في منطقتك.",
        "kyc_prompt": "🔒 <b>تأكيد الهوية الأمني (KYC):</b>\n\nلضمان أعلى معايير الحماية القانونية وفقاً لمعايير الاتحاد الأوروبي وتأمين حسابك بالبنية اللامركزية، يرجى إتمام التحقق السريع قبل البدء:",
        "kyc_fast_btn": "✅ التحقق السريع بالهوية الرقمية (فوري)",
        "kyc_pi_btn": "🌐 ربط شبكة الحماية (Pi Network KYC)",
        "kyc_success": "✅ <b>تم التحقق بنجاح!</b>\n\nأصبح حسابك مؤمناً بالكامل وجاهزاً لاستخدام خدمات بوت لينا.",
        "real_estate": "🟢 عقارات دولية",
        "cars": "🟢 قطاع السيارات",
        "services": "🟢 خدمات عامة",
        "ledger": "🟢 السجل المحاسبي",
        "containers": "🟢 الشحن والكونتينرات",
        "support": "🟢 الدعم الفني",
        "feedback": "🟢 ترك ملاحظة أو شكوى",
        "share_bot": "📤 مشاركة البوت مع الأصدقاء",
        "admin_stats": "📊 لوحة تحكم الإحصائيات",
        "sub": "🟢 VIP - بطاقة بنكية / اشتراك (Stripe 2.99€)",
        "web3": "🟢 دفع رقمي سريع - TON / Crypto (0.50€)",
        "early_bird_btn": "🎯 حجز مبكر: الباقة السنوية (19.99€ بدلاً من 24.99€)",
        "bill_elec": "🟢 فاتورة الكهرباء",
        "bill_water": "🟢 فاتورة المياه",
        "bill_phone": "🟢 فاتورة الاتصالات",
        "bill_tax": "🟢 ضريبة المركبات",
        "test_notice": "⚠️ <b>تنبيه النسخة التجريبية:</b>\n\nلقد اخترت خدمة: <b>{item}</b>.\nهذا البوت في مرحلة الاختبار والتجربة المجانية ريثما يتم تأسيس الشركة رسمياً لضمان العمل النظامي والضريبي، ولا يتم خصم أي أموال حقيقية حالياً.",
        "feedback_prompt": "🟢 أهلاً بك. يرجى كتابة ملاحظتك أو شكواك في رسالة واحدة أدناه ليتم إرسالها للإدارة:",
        "feedback_thanks": "🟢 تم إرسال ملاحظتك بنجاح للإدارة، شكراً لتواصلك!",
        "ledger_report": "🟢 <b>السجل المحاسبي (التجريبي):</b> الحركات المسجلة: {count}",
        "test_payment_text": "🧪 <b>بوابة الدفع الثنائية المتاحة:</b>\n\nيمكنك الدفع إما عبر <b>بطاقات الدفع البنكية (Stripe)</b> أو عبر <b>العملات الرقمية (TON Network)</b>.\n\n💡 <b>الرسوم المستقبلية بعد الإطلاق الرسمي:</b>\n• رسوم المعاملة الواحدة: <b>0.50 سنت</b>\n• الاشتراك الشهري: <b>2.99 يورو</b>\n• الاشتراك السنوي الأساسي: <b>24.99 يورو</b>\n\nلن يتم خصم أي شيء منك الآن خلال الفترة التجريبية.",
        "early_bird_msg": "🟢 <b>أهلاً بك في قائمة الحجز المبكر الحصرية لبوت لينا!</b>\n\nنود إعلامك أن \"بوت لينا\" يعمل حالياً في <b>فترة تجريبية مجانية بالكامل</b>، ولن يتم تفعيل الخدمات المدفوعة إلا بعد استكمال تأسيس الشركة في ألمانيا.\n\n🎁 <b>مكافأة الحجز المبكر:</b>\n• التسجيل حالياً <b>مجاني 100%</b>.\n• الحصول على <b>الباقة السنوية بسعر حصري 19.99 يورو</b> (بدلاً من <b>24.99 يورو</b>).\n\n📊 <i>عدد المسجلين حتى الآن: <b>{count} / 500</b></i>",
        "early_bird_success": "✅ <b>تم تسجيلك بنجاح في قائمة الحجز المبكر الحصرية!</b>",
        "early_bird_already": "⚠️ <b>أنت مسجل بالفعل!</b>",
        "early_bird_full": "⚠️ عذراً، اكتمل العدد المخصص للحجز المبكر (500 مشترك).",
        "stats_report": "📊 <b>إحصائيات تفاعل البوت:</b>\n\n👥 إجمالي المستخدمين: <b>{users}</b>\n🔒 الموثقون (KYC): <b>{verified}</b>\n⚡ إجمالي التفاعلات: <b>{clicks}</b>\n🎯 مسجلو الحجز المبكر: <b>{early_count} / 500</b>",
        "quick_reply": "🟢 مرحباً بك مجدداً. اختر إحدى الخدمات من القائمة أدناه:",
        "share_text": "🤖 منصة الأعمال الذكية بوت لينا (Lina AI). جربه الآن:"
    },
    "de": {
        "welcome": "🟢 <b>Willkommen beim Lina Bot (Smart Business Platform)!</b>\n\n⚠️ <i>Hinweis: Testphase. Offizieller Start nach Firmengründung in Deutschland.</i>\n\nWählen Sie unten einen Dienst aus:",
        "blocked": "Entschuldigung, dieser Dienst ist in Ihrer Region nicht verfügbar.",
        "kyc_prompt": "🔒 <b>Sicherheits-Identitätsprüfung (KYC):</b>\n\nBitte schließen Sie die schnelle Verifizierung ab:",
        "kyc_fast_btn": "✅ Schnelle digitale ID-Prüfung",
        "kyc_pi_btn": "🌐 Pi Network Sicherheitsbindung",
        "kyc_success": "✅ <b>Erfolgreich verifiziert!</b>",
        "real_estate": "🟢 Internationale Immobilien",
        "cars": "🟢 Automobilsektor",
        "services": "🟢 Allgemeine Dienste",
        "ledger": "🟢 Buchhaltungsbuch",
        "containers": "🟢 Versand & Container",
        "support": "🟢 Support",
        "feedback": "🟢 Feedback / Beschwerde",
        "share_bot": "📤 Bot mit Freunden teilen",
        "admin_stats": "📊 Admin Statistik",
        "sub": "🟢 VIP - Karte / Abo (Stripe 2.99€)",
        "web3": "🟢 Krypto-Zahlung - TON (0.50€)",
        "early_bird_btn": "🎯 Frühbucher: Jahresabo (19.99€ statt 24.99€)",
        "bill_elec": "🟢 Stromrechnung",
        "bill_water": "🟢 Wasserrechnung",
        "bill_phone": "🟢 Telefonrechnung",
        "bill_tax": "🟢 Kfz-Steuer",
        "test_notice": "⚠️ <b>Test-Hinweis:</b>\n\nSie haben gewählt: <b>{item}</b>.",
        "feedback_prompt": "🟢 Bitte geben Sie Ihr Feedback ein:",
        "feedback_thanks": "🟢 Vielen Dank! Ihr Feedback wurde gesendet.",
        "ledger_report": "🟢 <b>Test-Buchhaltung:</b> Registrierte Einträge: {count}",
        "test_payment_text": "🧪 <b>Zahlungssystem:</b>\n\nZahlung via Kreditkarte (Stripe) oder Krypto (TON) verfügbar.",
        "early_bird_msg": "🟢 <b>Frühbucher-Warteliste!</b>",
        "early_bird_success": "✅ <b>Erfolgreich registriert!</b>",
        "early_bird_already": "⚠️ Sie sind bereits registriert.",
        "early_bird_full": "⚠️ Kontingent erschöpft.",
        "stats_report": "📊 <b>Statistiken:</b>\n\n👥 Benutzer: <b>{users}</b>\n🔒 Verifiziert: <b>{verified}</b>",
        "quick_reply": "🟢 Willkommen zurück:",
        "share_text": "🤖 Entdecken Sie den Lina KI Bot:"
    },
    "en": {
        "welcome": "🟢 <b>Welcome to Lina Bot (Smart Business Platform)!</b>\n\n⚠️ <i>Trial phase. Full launch follows company registration in Germany.</i>\n\nSelect a service below:",
        "blocked": "Region blocked.",
        "kyc_prompt": "🔒 <b>Security Identity Verification (KYC):</b>\n\nPlease complete fast verification to proceed:",
        "kyc_fast_btn": "✅ Fast Digital ID Verification",
        "kyc_pi_btn": "🌐 Pi Network Security Link",
        "kyc_success": "✅ <b>Successfully Verified!</b>",
        "real_estate": "🟢 Real Estate",
        "cars": "🟢 Automotive",
        "services": "🟢 General Services",
        "ledger": "🟢 Accounting Ledger",
        "containers": "🟢 Containers",
        "support": "🟢 Digital Support",
        "feedback": "🟢 Leave Feedback",
        "share_bot": "📤 Share Bot with Friends",
        "admin_stats": "📊 Admin Statistics",
        "sub": "🟢 VIP - Card / Sub (Stripe 2.99€)",
        "web3": "🟢 Crypto Fast Pay - TON (0.50€)",
        "early_bird_btn": "🎯 Early Bird: Annual Pass (19.99€ instead of 24.99€)",
        "bill_elec": "🟢 Electricity",
        "bill_water": "🟢 Water",
        "bill_phone": "🟢 Phone",
        "bill_tax": "🟢 Car Tax",
        "test_notice": "⚠️ <b>Test Notice:</b>\n\nYou selected: <b>{item}</b>.",
        "feedback_prompt": "🟢 Type your feedback:",
        "feedback_thanks": "🟢 Feedback sent!",
        "ledger_report": "🟢 <b>Ledger:</b> {count}",
        "test_payment_text": "🧪 <b>Payment Gateways:</b> Supported via Stripe (Card) or TON (Crypto).",
        "early_bird_msg": "🟢 <b>Early Bird Waitlist!</b>",
        "early_bird_success": "✅ <b>Successfully registered!</b>",
        "early_bird_already": "⚠️ Already registered.",
        "early_bird_full": "⚠️ Capacity reached.",
        "stats_report": "📊 <b>Statistics:</b>\n\n👥 Users: <b>{users}</b>\n🔒 Verified: <b>{verified}</b>",
        "quick_reply": "🟢 Welcome back:",
        "share_text": "🤖 Try the Lina AI Bot:"
    },
    "fr": {
        "welcome": "🟢 <b>Bienvenue sur Lina Bot !</b>",
        "blocked": "Région bloquée.",
        "kyc_prompt": "🔒 <b>Vérification d'identité (KYC) :</b>",
        "kyc_fast_btn": "✅ Vérification rapide",
        "kyc_pi_btn": "🌐 Liaison Pi Network",
        "kyc_success": "✅ <b>Vérifié avec succès !</b>",
        "real_estate": "🟢 Immobilier",
        "cars": "🟢 Automobile",
        "services": "🟢 Services généraux",
        "ledger": "🟢 Registre",
        "containers": "🟢 Conteneurs",
        "support": "🟢 Support",
        "feedback": "🟢 Avis",
        "share_bot": "📤 Partager",
        "admin_stats": "📊 Stats",
        "sub": "🟢 VIP (Stripe 2.99€)",
        "web3": "🟢 Crypto (TON 0.50€)",
        "early_bird_btn": "🎯 Offre Précoce (19.99€)",
        "bill_elec": "🟢 Électricité",
        "bill_water": "🟢 Eau",
        "bill_phone": "🟢 Téléphone",
        "bill_tax": "🟢 Taxe auto",
        "test_notice": "⚠️ Test : <b>{item}</b>",
        "feedback_prompt": "🟢 Commentaires :",
        "feedback_thanks": "🟢 Envoyé !",
        "ledger_report": "🟢 Registre : {count}",
        "test_payment_text": "🧪 Paiement par Stripe ou TON disponible.",
        "early_bird_msg": "🟢 Liste d'attente !",
        "early_bird_success": "✅ Inscrit !",
        "early_bird_already": "⚠️ Déjà inscrit.",
        "early_bird_full": "⚠️ Complet.",
        "stats_report": "📊 Stats : Utilisateurs {users}",
        "quick_reply": "🟢 Bon retour :",
        "share_text": "🤖 Essayez Lina AI :"
    },
    "it": {
        "welcome": "🟢 <b>Benvenuto in Lina Bot!</b>",
        "blocked": "Regione bloccata.",
        "kyc_prompt": "🔒 <b>Verifica d'identità (KYC):</b>",
        "kyc_fast_btn": "✅ Verifica rapida",
        "kyc_pi_btn": "🌐 Collegamento Pi Network",
        "kyc_success": "✅ <b>Verificato con successo!</b>",
        "real_estate": "🟢 Immobiliare",
        "cars": "🟢 Auto",
        "services": "🟢 Servizi",
        "ledger": "🟢 Registro",
        "containers": "🟢 Contenitori",
        "support": "🟢 Supporto",
        "feedback": "🟢 Feedback",
        "share_bot": "📤 Condividi",
        "admin_stats": "📊 Statistiche",
        "sub": "🟢 VIP (Stripe 2.99€)",
        "web3": "🟢 Crypto (TON 0.50€)",
        "early_bird_btn": "🎯 Early Bird (19.99€)",
        "bill_elec": "🟢 Elettricità",
        "bill_water": "🟢 Acqua",
        "bill_phone": "🟢 Telefono",
        "bill_tax": "🟢 Tassa auto",
        "test_notice": "⚠️ Test: <b>{item}</b>",
        "feedback_prompt": "🟢 Inserisci feedback:",
        "feedback_thanks": "🟢 Inviato!",
        "ledger_report": "🟢 Registro: {count}",
        "test_payment_text": "🧪 Pagamento tramite Stripe o TON.",
        "early_bird_msg": "🟢 Lista d'attesa!",
        "early_bird_success": "✅ Registrato!",
        "early_bird_already": "⚠️ Già registrato.",
        "early_bird_full": "⚠️ Esaurito.",
        "stats_report": "📊 Utenti: {users}",
        "quick_reply": "🟢 Bentornato:",
        "share_text": "🤖 Prova Lina AI:"
    },
    "es": {
        "welcome": "🟢 <b>¡Bienvenido a Lina Bot!</b>",
        "blocked": "Región bloqueada.",
        "kyc_prompt": "🔒 <b>Verificación de identidad (KYC):</b>",
        "kyc_fast_btn": "✅ Verificación rápida",
        "kyc_pi_btn": "🌐 Enlace Pi Network",
        "kyc_success": "✅ <b>¡Verificado con éxito!</b>",
        "real_estate": "🟢 Inmobiliaria",
        "cars": "🟢 Automoción",
        "services": "🟢 Servicios",
        "ledger": "🟢 Registro",
        "containers": "🟢 Contenedores",
        "support": "🟢 Soporte",
        "feedback": "🟢 Comentarios",
        "share_bot": "📤 Compartir",
        "admin_stats": "📊 Estadísticas",
        "sub": "🟢 VIP (Stripe 2.99€)",
        "web3": "🟢 Crypto (TON 0.50€)",
        "early_bird_btn": "🎯 Early Bird (19.99€)",
        "bill_elec": "🟢 Electricidad",
        "bill_water": "🟢 Agua",
        "bill_phone": "🟢 Teléfono",
        "bill_tax": "🟢 Impuesto",
        "test_notice": "⚠️ Prueba: <b>{item}</b>",
        "feedback_prompt": "🟢 Comentarios:",
        "feedback_thanks": "🟢 ¡Enviado!",
        "ledger_report": "🟢 Registro: {count}",
        "test_payment_text": "🧪 Pago mediante Stripe o TON disponible.",
        "early_bird_msg": "🟢 Lista de espera!",
        "early_bird_success": "✅ ¡Registrado!",
        "early_bird_already": "⚠️ Ya registrado.",
        "early_bird_full": "⚠️ Completo.",
        "stats_report": "📊 Usuarios: {users}",
        "quick_reply": "🟢 Bienvenido de nuevo:",
        "share_text": "🤖 Prueba Lina AI:"
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

def get_kyc_keyboard(t):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(t["kyc_fast_btn"], callback_data="do_kyc_fast"),
        InlineKeyboardButton(t["kyc_pi_btn"], callback_data="do_kyc_pi")
    )
    return keyboard

def get_main_keyboard(t, user_id, bot_username=""):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(t["real_estate"], callback_data="real_estate"),
        InlineKeyboardButton(t["cars"], callback_data="cars"),
        InlineKeyboardButton(t["bill_elec"], callback_data="bill_elec"),
        InlineKeyboardButton(t["bill_water"], callback_data="bill_water"),
        InlineKeyboardButton(t["bill_phone"], callback_data="bill_phone"),
        InlineKeyboardButton(t["bill_tax"], callback_data="bill_tax"),
        InlineKeyboardButton(t["ledger"], callback_data="view_ledger"),
    )
    
    if user_id != ADMIN_CHAT_ID:
        keyboard.add(InlineKeyboardButton(t["feedback"], callback_data="leave_feedback"))
        
    keyboard.add(
        InlineKeyboardButton(t["services"], callback_data="services"),
        InlineKeyboardButton(t["containers"], callback_data="containers"),
        InlineKeyboardButton(t["sub"], callback_data="sub"),
        InlineKeyboardButton(t["web3"], callback_data="web3")
    )
    
    keyboard.add(InlineKeyboardButton(t["early_bird_btn"], callback_data="early_bird_info"))
    
    if bot_username:
        share_url = f"https://t.me/share/url?url=https://t.me/{bot_username}&text={t['share_text']}"
        keyboard.add(InlineKeyboardButton(t["share_bot"], url=share_url))
        
    if user_id == ADMIN_CHAT_ID:
        keyboard.add(InlineKeyboardButton(t["admin_stats"], callback_data="admin_stats"))
        
    return keyboard

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    if message.from_user.language_code in BLOCKED_COUNTRIES:
        await message.answer(TRANSLATIONS[get_lang(message)]["blocked"])
        return

    user_interactions.add(user_id)
    save_data()
    lang = get_lang(message)
    t = TRANSLATIONS[lang]
    
    # التحقق عما إذا كان المستخدم قد أتم نظام الـ KYC مسبقاً
    if user_id not in verified_users and user_id != ADMIN_CHAT_ID:
        user_states[user_id] = "waiting_for_kyc"
        await message.answer(t["kyc_prompt"], reply_markup=get_kyc_keyboard(t), parse_mode="HTML")
        return

    user_states[user_id] = "main_menu"
    bot_info = await bot.get_me()
    await message.answer(t["welcome"], reply_markup=get_main_keyboard(t, user_id, bot_info.username), parse_mode="HTML")

@dp.message_handler(lambda message: not message.text.startswith('/'))
async def handle_smart_sensor(message: types.Message):
    user_id = message.from_user.id
    if message.from_user.language_code in BLOCKED_COUNTRIES:
        return

    user_interactions.add(user_id)
    save_data()
    lang = get_lang(message)
    t = TRANSLATIONS[lang]
    current_state = user_states.get(user_id, "main_menu")

    if user_id not in verified_users and user_id != ADMIN_CHAT_ID:
        user_states[user_id] = "waiting_for_kyc"
        await message.answer(t["kyc_prompt"], reply_markup=get_kyc_keyboard(t), parse_mode="HTML")
        return

    if current_state == "waiting_for_feedback":
        user_states[user_id] = "main_menu"
        user_text = message.text
        try:
            admin_msg = f"🟢 <b>ملاحظة جديدة في البوت:</b>\n\n💬 النص:\n<i>{user_text}</i>"
            await bot.send_message(ADMIN_CHAT_ID, admin_msg, parse_mode="HTML")
        except Exception as e:
            logging.error(f"Error: {e}")
        await message.answer(t["feedback_thanks"])
        return

    user_states[user_id] = "main_menu"
    bot_info = await bot.get_me()
    await message.answer(t["quick_reply"], reply_markup=get_main_keyboard(t, user_id, bot_info.username), parse_mode="HTML")

@dp.callback_query_handler(lambda call: True)
async def process_callbacks(call: types.CallbackQuery) -> None:
    user_id = call.from_user.id
    if call.from_user.language_code in BLOCKED_COUNTRIES:
        await call.answer("Blocked", show_alert=True)
        return

    user_interactions.add(user_id)
    action_counter["clicks"] += 1
    save_data()

    lang = get_lang(call)
    t = TRANSLATIONS[lang]
    await call.answer()

    # معالجة أزرار الـ KYC
    if call.data in ["do_kyc_fast", "do_kyc_pi"]:
        verified_users.add(user_id)
        save_data()
        user_states[user_id] = "main_menu"
        
        bot_info = await bot.get_me()
        await call.message.answer(t["kyc_success"], parse_mode="HTML")
        await call.message.answer(t["welcome"], reply_markup=get_main_keyboard(t, user_id, bot_info.username), parse_mode="HTML")
        return

    if user_id not in verified_users and user_id != ADMIN_CHAT_ID:
        user_states[user_id] = "waiting_for_kyc"
        await call.message.answer(t["kyc_prompt"], reply_markup=get_kyc_keyboard(t), parse_mode="HTML")
        return

    if call.data == "admin_stats" and user_id == ADMIN_CHAT_ID:
        total_users = len(user_interactions)
        total_clicks = action_counter["clicks"]
        early_count = len(early_bird_users)
        verified_count = len(verified_users)
        await call.message.answer(t["stats_report"].format(users=total_users, verified=verified_count, clicks=total_clicks, early_count=early_count), parse_mode="HTML")
        return

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

    if call.data == "early_bird_info":
        user_states[user_id] = "main_menu"
        count = len(early_bird_users)
        
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("✅ تأكيد الحجز المجاني الآن", callback_data="confirm_early_bird"))
        
        await call.message.answer(t["early_bird_msg"].format(count=count), reply_markup=keyboard, parse_mode="HTML")
        return

    if call.data == "confirm_early_bird":
        user_states[user_id] = "main_menu"
        
        if user_id in early_bird_users:
            await call.message.answer(t["early_bird_already"], parse_mode="HTML")
            return
            
        if len(early_bird_users) >= EARLY_BIRD_LIMIT:
            await call.message.answer(t["early_bird_full"], parse_mode="HTML")
            return
            
        early_bird_users.add(user_id)
        save_data()
        await call.message.answer(t["early_bird_success"], parse_mode="HTML")
        
        try:
            admin_notify = f"🎯 <b>تسجيل جديد في الحجز المبكر (VIP)!</b>\n👤 User ID: <code>{user_id}</code>\n📊 العدد الحالي: {len(early_bird_users)} / 500"
            await bot.send_message(ADMIN_CHAT_ID, admin_notify, parse_mode="HTML")
        except Exception as e:
            logging.error(f"Error notifying admin: {e}")
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
