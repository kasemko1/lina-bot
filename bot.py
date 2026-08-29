import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

API_TOKEN = os.getenv("BOT_TOKEN")

# رقم الآيدي الخاص بك للإدارة وتلقي الملاحظات والإحصائيات
ADMIN_CHAT_ID = 8807102611  

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_states = {}
user_data = {}
user_ledger = {}
user_interactions = set()  # تتبع المستخدمين الفريدين للإحصائيات
action_counter = {"clicks": 0}  # عداد التفاعلات والنقرات

BLOCKED_COUNTRIES = ["ru", "ir"]

# القاموس الشامل للغات الست مع الأسعار الواضحة تماماً في أزرار الدفع
TRANSLATIONS = {
    "ar": {
        "welcome": "🟢 <b>أهلاً بك في بوت لينا (منصة الأعمال الذكية)!</b>\n\n⚠️ <i>ملاحظة هامة: البوت حالياً في المرحلة التجريبية ريثما يتم التسجيل النظامي وتأسيس الشركة رسمياً للامتثال الضريبي والمالي، وجميع المعاملات الحالية مجانية ولن يتم خصم أي مبالغ.</i>\n\nاختر الخدمة أو طريقة الدفع المطلوبة أدناه:",
        "blocked": "عذراً، الخدمة غير متاحة في منطقتك.",
        "real_estate": "🟢 عقارات دولية",
        "cars": "🟢 قطاع السيارات",
        "services": "🟢 خدمات عامة",
        "ledger": "🟢 السجل المحاسبي",
        "containers": "🟢 الشحن والكونتينرات",
        "support": "🟢 الدعم الفني",
        "feedback": "🟢 ترك ملاحظة أو شكوى",
        "share_bot": "📤 مشاركة البوت مع الأصدقاء",
        "admin_stats": "📊 لوحة تحكم الإحصائيات",
        "sub": "🟢 VIP (2.99€ ستريب)",
        "web3": "🟢 دفع ميتاماسك (0.50€)",
        "bill_elec": "🟢 فاتورة الكهرباء",
        "bill_water": "🟢 فاتورة المياه",
        "bill_phone": "🟢 فاتورة الاتصالات",
        "bill_tax": "🟢 ضريبة المركبات",
        "test_notice": "⚠️ <b>تنبيه النسخة التجريبية:</b>\n\nلقد اخترت خدمة: <b>{item}</b>.\nهذا البوت في مرحلة الاختبار والتجربة المجانية ريثما يتم تأسيس الشركة رسمياً لضمان العمل النظامي والضريبي، ولا يتم خصم أي أموال حقيقية حالياً.",
        "feedback_prompt": "🟢 تفضل يا غالي، اكتب ملاحظتك أو شكواك للإدارة:",
        "feedback_thanks": "🟢 تم إرسال ملاحظتك بنجاح للإدارة!",
        "ledger_report": "🟢 <b>السجل المحاسبي (التجريبي):</b> الحركات المسجلة: {count}",
        "test_payment_text": "🧪 <b>بوابة الدفع التجريبية:</b>\n\nالخدمات المالية والضريبية مغلقة مؤقتاً لحين استكمال تأسيس الشركة رسمياً وتفعيل الربط المالي النظامي، ولن يتم خصم أي شيء منك الآن.",
        "stats_report": "📊 <b>إحصائيات تفاعل البوت:</b>\n\n👥 عدد المستخدمين الكلي: <b>{users}</b>\n⚡ عدد تفاعلات النقر والخدمات: <b>{clicks}</b>",
        "quick_reply": "🟢 مرحباً بك مجدداً. اختر إحدى الخدمات:",
        "share_text": "🤖 منصة الأعمال الذكية بوت لينا (Lina AI). جربه الآن:"
    },
    "de": {
        "welcome": "🟢 <b>Willkommen beim Lina Bot (Smart Business Platform)!</b>\n\n⚠️ <i>Hinweis: Der Bot befindet sich in der Testphase bis zur offiziellen Firmengründung.</i>\n\nWählen Sie unten einen Dienst aus:",
        "blocked": "Entschuldigung, dieser Dienst ist in Ihrer Region nicht verfügbar.",
        "real_estate": "🟢 Internationale Immobilien",
        "cars": "🟢 Automobilsektor",
        "services": "🟢 Allgemeine Dienste",
        "ledger": "🟢 Buchhaltungsbuch",
        "containers": "🟢 Versand & Container",
        "support": "🟢 Support",
        "feedback": "🟢 Feedback / Beschwerde",
        "share_bot": "📤 Bot mit Freunden teilen",
        "admin_stats": "📊 Admin Statistik",
        "sub": "🟢 VIP (2.99€ Stripe)",
        "web3": "🟢 MetaMask (0.50€)",
        "bill_elec": "🟢 Stromrechnung",
        "bill_water": "🟢 Wasserrechnung",
        "bill_phone": "🟢 Telefonrechnung",
        "bill_tax": "🟢 Kfz-Steuer",
        "test_notice": "⚠️ <b>Test-Hinweis:</b>\n\nSie haben gewählt: <b>{item}</b>.\nDer Bot befindet sich in der Testphase vor der offiziellen Registrierung.",
        "feedback_prompt": "🟢 Bitte geben Sie Ihr Feedback ein:",
        "feedback_thanks": "🟢 Vielen Dank! Ihr Feedback wurde gesendet.",
        "ledger_report": "🟢 <b>Test-Buchhaltung:</b> Registrierte Einträge: {count}",
        "test_payment_text": "🧪 <b>Zahlungssystem:</b>\n\nFinanzdienste sind bis zur offiziellen Firmengründung deaktiviert.",
        "stats_report": "📊 <b>Bot-Statistiken:</b>\n\n👥 Gesamtzahl der Benutzer: <b>{users}</b>\n⚡ Gesamtzahl der Interaktionen: <b>{clicks}</b>",
        "quick_reply": "🟢 Willkommen zurück. Wählen Sie eine Option:",
        "share_text": "🤖 Entdecken Sie den Lina KI Bot:"
    },
    "en": {
        "welcome": "🟢 <b>Welcome to Lina Bot (Smart Business Platform)!</b>\n\n⚠️ <i>Note: This bot is currently in test mode pending official company registration and tax compliance.</i>\n\nSelect a service below:",
        "blocked": "Region blocked.",
        "real_estate": "🟢 Real Estate",
        "cars": "🟢 Automotive",
        "services": "🟢 General Services",
        "ledger": "🟢 Accounting Ledger",
        "containers": "🟢 Containers",
        "support": "🟢 Digital Support",
        "feedback": "🟢 Leave Feedback",
        "share_bot": "📤 Share Bot with Friends",
        "admin_stats": "📊 Admin Statistics",
        "sub": "🟢 VIP (2.99€ Stripe)",
        "web3": "🟢 MetaMask (0.50€)",
        "bill_elec": "🟢 Electricity",
        "bill_water": "🟢 Water",
        "bill_phone": "🟢 Phone",
        "bill_tax": "🟢 Car Tax",
        "test_notice": "⚠️ <b>Test Notice:</b>\n\nYou selected: <b>{item}</b>.\nThis bot is in a free test mode pending formal company setup.",
        "feedback_prompt": "🟢 Type your feedback:",
        "feedback_thanks": "🟢 Feedback sent!",
        "ledger_report": "🟢 <b>Ledger:</b> {count}",
        "test_payment_text": "🧪 <b>Payment:</b>\n\nPayment services are currently disabled until official company setup.",
        "stats_report": "📊 <b>Bot Statistics:</b>\n\n👥 Total Users: <b>{users}</b>\n⚡ Total Interactions: <b>{clicks}</b>",
        "quick_reply": "🟢 Welcome back:",
        "share_text": "🤖 Try the Lina AI Bot:"
    },
    "fr": {
        "welcome": "🟢 <b>Bienvenue sur Lina Bot !</b>\n\n⚠️ <i>Ce bot est en mode test en attendant l'enregistrement officiel de l'entreprise.</i>\n\nSélectionnez un service :",
        "blocked": "Région bloquée.",
        "real_estate": "🟢 Immobilier",
        "cars": "🟢 Automobile",
        "services": "🟢 Services généraux",
        "ledger": "🟢 Registre comptable",
        "containers": "🟢 Conteneurs",
        "support": "🟢 Support technique",
        "feedback": "🟢 Laisser un avis",
        "share_bot": "📤 Partager le bot avec des amis",
        "admin_stats": "📊 Statistiques Admin",
        "sub": "🟢 VIP (2.99€ Stripe)",
        "web3": "🟢 MetaMask (0.50€)",
        "bill_elec": "🟢 Électricité",
        "bill_water": "🟢 Eau",
        "bill_phone": "🟢 Téléphone",
        "bill_tax": "🟢 Taxe auto",
        "test_notice": "⚠️ <b>Avis de test :</b>\n\nVous avez sélectionné : <b>{item}</b> (En attente d'enregistrement officiel).",
        "feedback_prompt": "🟢 Entrez vos commentaires :",
        "feedback_thanks": "🟢 Commentaires envoyés !",
        "ledger_report": "🟢 <b>Registre :</b> {count}",
        "test_payment_text": "🧪 <b>Paiement :</b>\n\nDésactivé jusqu'à la création officielle de l'entreprise.",
        "stats_report": "📊 <b>Statistiques :</b>\n\n👥 Utilisateurs : <b>{users}</b>\n⚡ Interactions : <b>{clicks}</b>",
        "quick_reply": "🟢 Bon retour :",
        "share_text": "🤖 Essayez le bot Lina AI :"
    },
    "it": {
        "welcome": "🟢 <b>Benvenuto in Lina Bot!</b>\n\n⚠️ <i>Nota: Questo bot è in fase di test in attesa della registrazione ufficiale dell'azienda.</i>\n\nSeleziona un servizio:",
        "blocked": "Regione bloccata.",
        "real_estate": "🟢 Immobiliare",
        "cars": "🟢 Settore automobilistico",
        "services": "🟢 Servizi generali",
        "ledger": "🟢 Registro contabile",
        "containers": "🟢 Contenitori",
        "support": "🟢 Supporto",
        "feedback": "🟢 Lascia un feedback",
        "share_bot": "📤 Condividi il bot con gli amici",
        "admin_stats": "📊 Statistiche Admin",
        "sub": "🟢 VIP (2.99€ Stripe)",
        "web3": "🟢 MetaMask (0.50€)",
        "bill_elec": "🟢 Elettricità",
        "bill_water": "🟢 Acqua",
        "bill_phone": "🟢 Telefono",
        "bill_tax": "🟢 Tassa auto",
        "test_notice": "⚠️ <b>Avviso di test:</b>\n\nHai selezionato: <b>{item}</b> (In attesa di registrazione aziendale).",
        "feedback_prompt": "🟢 Inserisci il tuo feedback:",
        "feedback_thanks": "🟢 Feedback inviato!",
        "ledger_report": "🟢 <b>Registro:</b> {count}",
        "test_payment_text": "🧪 <b>Pagamento:</b>\n\nDisabilitato fino alla costituzione ufficiale della società.",
        "stats_report": "📊 <b>Statistiche:</b>\n\n👥 Utenti: <b>{users}</b>\n⚡ Interazioni: <b>{clicks}</b>",
        "quick_reply": "🟢 Bentornato:",
        "share_text": "🤖 Prova il bot Lina AI:"
    },
    "es": {
        "welcome": "🟢 <b>¡Bienvenido a Lina Bot!</b>\n\n⚠️ <i>Nota: Este bot está en modo de prueba a la espera del registro oficial de la empresa.</i>\n\nSelecciona un servicio:",
        "blocked": "Regione bloquée.",
        "real_estate": "🟢 Inmobiliaria",
        "cars": "🟢 Automoción",
        "services": "🟢 Servicios generales",
        "ledger": "🟢 Registro contable",
        "containers": "🟢 Contenedores",
        "support": "🟢 Soporte técnico",
        "feedback": "🟢 Dejar comentarios",
        "share_bot": "📤 Compartir bot con amigos",
        "admin_stats": "📊 Estadísticas de Admin",
        "sub": "🟢 VIP (2.99€ Stripe)",
        "web3": "🟢 MetaMask (0.50€)",
        "bill_elec": "🟢 Electricidad",
        "bill_water": "🟢 Agua",
        "bill_phone": "🟢 Teléfono",
        "bill_tax": "🟢 Impuesto de vehículos",
        "test_notice": "⚠️ <b>Aviso de prueba:</b>\n\nHas seleccionado: <b>{item}</b> (Pendiente de registro de empresa).",
        "feedback_prompt": "🟢 Escribe tus comentarios:",
        "feedback_thanks": "🟢 ¡Comentarios enviados!",
        "ledger_report": "🟢 <b>Registro:</b> {count}",
        "test_payment_text": "🧪 <b>Pago:</b>\n\nDeshabilitado hasta la constitución oficial de la empresa.",
        "stats_report": "📊 <b>Estadísticas:</b>\n\n👥 Usuarios: <b>{users}</b>\n⚡ Total interactions: <b>{clicks}</b>",
        "quick_reply": "🟢 Bienvenido de nuevo:",
        "share_text": "🤖 Prueba el bot Lina AI:"
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
        InlineKeyboardButton(t["feedback"], callback_data="leave_feedback"),
        InlineKeyboardButton(t["services"], callback_data="services"),
        InlineKeyboardButton(t["containers"], callback_data="containers"),
        InlineKeyboardButton(t["sub"], callback_data="sub"),
        InlineKeyboardButton(t["web3"], callback_data="web3")
    )
    
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
    user_states[user_id] = "main_menu"
    lang = get_lang(message)
    t = TRANSLATIONS[lang]
    
    bot_info = await bot.get_me()
    bot_username = bot_info.username
    
    await message.answer(t["welcome"], reply_markup=get_main_keyboard(t, user_id, bot_username), parse_mode="HTML")

@dp.message_handler(lambda message: not message.text.startswith('/'))
async def handle_smart_sensor(message: types.Message):
    user_id = message.from_user.id
    if message.from_user.language_code in BLOCKED_COUNTRIES:
        return

    user_interactions.add(user_id)
    lang = get_lang(message)
    t = TRANSLATIONS[lang]
    current_state = user_states.get(user_id, "main_menu")

    if current_state == "waiting_for_feedback":
        user_states[user_id] = "main_menu"
        user_text = message.text
        user_name = message.from_user.full_name or "مستخدم مجهول"
        try:
            admin_msg = f"🟢 <b>ملاحظة جديدة في بوت لينا (تجريبي):</b>\n\n👤 الاسم: {user_name}\n🆔 الآيدي: `{user_id}`\n\n💬 النص:\n<i>{user_text}</i>"
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

    lang = get_lang(call)
    t = TRANSLATIONS[lang]
    await call.answer()
    
    action_counter["clicks"] += 1

    if call.data == "admin_stats" and user_id == ADMIN_CHAT_ID:
        total_users = len(user_interactions)
        total_clicks = action_counter["clicks"]
        await call.message.answer(t["stats_report"].format(users=total_users, clicks=total_clicks), parse_mode="HTML")
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
