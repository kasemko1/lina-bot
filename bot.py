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

# القاموس الشامل للغات الست (العربية، الإنجليزية، الألمانية، الفرنسية، الإيطالية، الإسبانية)
TRANSLATIONS = {
    "ar": {
        "welcome": "🟢 <b>أهلاً بك في بوت لينا (النسخة التجريبية - Test Version)!</b>\n\nهذا البوت في مرحلة الاختبار والتجربة المجانية. اختر الخدمة أدناه للاختبار:",
        "blocked": "عذراً، الخدمة غير متاحة في منطقتك.",
        "real_estate": "🟢 عقارات دولية (تجريبي) 🟢",
        "cars": "🟢 قطاع السيارات (تجريبي) 🟢",
        "services": "🟢 خدمات عامة (تجريبي) 🟢",
        "ledger": "🟢 السجل المحاسبي 🟢",
        "containers": "🟢 الشحن والكونتينرات (تجريبي) 🟢",
        "support": "🟢 الدعم الفني 🟢",
        "feedback": "🟢 ترك ملاحظة أو شكوى 🟢",
        "share_bot": "📤 مشاركة البوت مع الأصدقاء 📤",
        "admin_stats": "📊 لوحة تحكم الإحصائيات 📊",
        "sub": "🧪 تجربة اشتراك VIP 🧪",
        "web3": "🧪 تجربة دفع ميتاماسك 🧪",
        "bill_elec": "🟢 فاتورة الكهرباء (تجريبي) 🟢",
        "bill_water": "🟢 فاتورة المياه (تجريبي) 🟢",
        "bill_phone": "🟢 فاتورة الاتصالات (تجريبي) 🟢",
        "bill_tax": "🟢 ضريبة المركبات (تجريبي) 🟢",
        "test_notice": "⚠️ <b>ملاحظة تجريبية (Test-Modus):</b>\n\nلقد اخترت خدمة: <b>{item}</b>.\nهذا البوت في مرحلة الاختبار التجريبي المجاني ولا يتم دفع أي أموال حقيقية حالياً.",
        "feedback_prompt": "🟢 تفضل يا غالي، اكتب ملاحظتك أو شكواك للإدارة:",
        "feedback_thanks": "🟢 تم إرسال ملاحظتك بنجاح للإدارة!",
        "ledger_report": "🟢 <b>السجل المحاسبي التجريبي:</b> الحركات المسجلة: {count}",
        "test_payment_text": "🧪 <b>بوابة الدفع التجريبية:</b>\n\nالخدمات المالية مغلقة حالياً لأن البوت يخضع للاختبار المجاني وسيتم تفعيلها رسمياً بعد التسجيل النهائي للشركة.",
        "stats_report": "📊 <b>إحصائيات تفاعل البوت:</b>\n\n👥 عدد المستخدمين الكلي: <b>{users}</b>\n⚡ عدد تفاعلات النقر والخدمات: <b>{clicks}</b>",
        "quick_reply": "🟢 مرحباً بك مجدداً في نسخة التجربة. اختر إحدى الخدمات:",
        "share_text": "🤖 تجربة ممتازة لبوت الذكاء الاصطناعي لينا (Lina AI). جربه الآن:"
    },
    "de": {
        "welcome": "🟢 <b>Willkommen beim Lina Bot (Testversion)!</b>\n\nDieser Bot befindet sich in der Testphase. Wählen Sie unten einen Dienst aus:",
        "blocked": "Entschuldigung, dieser Dienst ist in Ihrer Region nicht verfügbar.",
        "real_estate": "🟢 Internationale Immobilien (Test) 🟢",
        "cars": "🟢 Automobilsektor (Test) 🟢",
        "services": "🟢 Allgemeine Dienste (Test) 🟢",
        "ledger": "🟢 Buchhaltungsbuch 🟢",
        "containers": "🟢 Versand & Container (Test) 🟢",
        "support": "🟢 Support 🟢",
        "feedback": "🟢 Feedback / Beschwerde 🟢",
        "share_bot": "📤 Bot mit Freunden teilen 📤",
        "admin_stats": "📊 Admin Statistik 📊",
        "sub": "🧪 VIP-Abo (Test) 🧪",
        "web3": "🧪 MetaMask-Zahlung (Test) 🧪",
        "bill_elec": "🟢 Stromrechnung (Test) 🟢",
        "bill_water": "🟢 Wasserrechnung (Test) 🟢",
        "bill_phone": "🟢 Telefonrechnung (Test) 🟢",
        "bill_tax": "🟢 Kfz-Steuer (Test) 🟢",
        "test_notice": "⚠️ <b>Test-Hinweis (Test-Modus):</b>\n\nSie haben gewählt: <b>{item}</b>.\nDieser Bot befindet sich in der kostenlosen Testphase. Keine echten Zahlungen.",
        "feedback_prompt": "🟢 Bitte geben Sie Ihr Feedback ein:",
        "feedback_thanks": "🟢 Vielen Dank! Ihr Feedback wurde gesendet.",
        "ledger_report": "🟢 <b>Test-Buchhaltung:</b> Registrierte Einträge: {count}",
        "test_payment_text": "🧪 <b>Test-Zahlungssystem:</b>\n\nFinanzdienste sind derzeit deaktiviert während der Testphase.",
        "stats_report": "📊 <b>Bot-Statistiken:</b>\n\n👥 Gesamtzahl der Benutzer: <b>{users}</b>\n⚡ Gesamtzahl der Interaktionen: <b>{clicks}</b>",
        "quick_reply": "🟢 Willkommen zurück im Test-Modus. Wählen Sie eine Option:",
        "share_text": "🤖 Entdecken Sie den Lina KI Bot:"
    },
    "en": {
        "welcome": "🟢 <b>Welcome to Lina Bot (Test Version)!</b>\n\nThis bot is in a free test mode. Select a service below:",
        "blocked": "Region blocked.",
        "real_estate": "🟢 Real Estate (Test) 🟢",
        "cars": "🟢 Automotive (Test) 🟢",
        "services": "🟢 General Services (Test) 🟢",
        "ledger": "🟢 Accounting Ledger 🟢",
        "containers": "🟢 Containers (Test) 🟢",
        "support": "🟢 Digital Support 🟢",
        "feedback": "🟢 Leave Feedback 🟢",
        "share_bot": "📤 Share Bot with Friends 📤",
        "admin_stats": "📊 Admin Statistics 📊",
        "sub": "🧪 VIP Sub (Test) 🧪",
        "web3": "🧪 MetaMask (Test) 🧪",
        "bill_elec": "🟢 Electricity (Test) 🟢",
        "bill_water": "🟢 Water (Test) 🟢",
        "bill_phone": "🟢 Phone (Test) 🟢",
        "bill_tax": "🟢 Car Tax (Test) 🟢",
        "test_notice": "⚠️ <b>Test Notice (Test-Modus):</b>\n\nYou selected: <b>{item}</b>.\nThis bot is in a free test mode. No real payments.",
        "feedback_prompt": "🟢 Type your feedback:",
        "feedback_thanks": "🟢 Feedback sent!",
        "ledger_report": "🟢 <b>Test Ledger:</b> {count}",
        "test_payment_text": "🧪 <b>Test Payment:</b>\n\nPayment services are currently disabled during testing.",
        "stats_report": "📊 <b>Bot Statistics:</b>\n\n👥 Total Users: <b>{users}</b>\n⚡ Total Interactions: <b>{clicks}</b>",
        "quick_reply": "🟢 Welcome back to test mode:",
        "share_text": "🤖 Try the Lina AI Bot:"
    },
    "fr": {
        "welcome": "🟢 <b>Bienvenue sur Lina Bot (Version Test) !</b>\n\nCe bot est en mode test gratuit. Sélectionnez un service ci-dessous :",
        "blocked": "Région bloquée.",
        "real_estate": "🟢 Immobilier (Test) 🟢",
        "cars": "🟢 Automobile (Test) 🟢",
        "services": "🟢 Services généraux (Test) 🟢",
        "ledger": "🟢 Registre comptable 🟢",
        "containers": "🟢 Conteneurs (Test) 🟢",
        "support": "🟢 Support technique 🟢",
        "feedback": "🟢 Laisser un avis 🟢",
        "share_bot": "📤 Partager le bot avec des amis 📤",
        "admin_stats": "📊 Statistiques Admin 📊",
        "sub": "🧪 Abonnement VIP (Test) 🧪",
        "web3": "🧪 Paiement MetaMask (Test) 🧪",
        "bill_elec": "🟢 Électricité (Test) 🟢",
        "bill_water": "🟢 Eau (Test) 🟢",
        "bill_phone": "🟢 Téléphone (Test) 🟢",
        "bill_tax": "🟢 Taxe auto (Test) 🟢",
        "test_notice": "⚠️ <b>Avis de test :</b>\n\nVous avez sélectionné : <b>{item}</b>.\nCe bot est en test gratuit. Aucun paiement réel.",
        "feedback_prompt": "🟢 Entrez vos commentaires :",
        "feedback_thanks": "🟢 Commentaires envoyés !",
        "ledger_report": "🟢 <b>Registre de test :</b> {count}",
        "test_payment_text": "🧪 <b>Paiement test :</b>\n\nLes services de paiement sont désactivés pendant les tests.",
        "stats_report": "📊 <b>Statistiques du bot :</b>\n\n👥 Total utilisateurs : <b>{users}</b>\n⚡ Total interactions : <b>{clicks}</b>",
        "quick_reply": "🟢 Bon retour en mode test :",
        "share_text": "🤖 Essayez le bot Lina AI :"
    },
    "it": {
        "welcome": "🟢 <b>Benvenuto in Lina Bot (Versione di prova)!</b>\n\nQuesto bot è in modalità test gratuita. Seleziona un servizio qui sotto:",
        "blocked": "Regione bloccata.",
        "real_estate": "🟢 Immobiliare (Test) 🟢",
        "cars": "🟢 Settore automobilistico (Test) 🟢",
        "services": "🟢 Servizi generali (Test) 🟢",
        "ledger": "🟢 Registro contabile 🟢",
        "containers": "🟢 Contenitori (Test) 🟢",
        "support": "🟢 Supporto 🟢",
        "feedback": "🟢 Lascia un feedback 🟢",
        "share_bot": "📤 Condividi il bot con gli amici 📤",
        "admin_stats": "📊 Statistiche Admin 📊",
        "sub": "🧪 Abbonamento VIP (Test) 🧪",
        "web3": "🧪 Pagamento MetaMask (Test) 🧪",
        "bill_elec": "🟢 Elettricità (Test) 🟢",
        "bill_water": "🟢 Acqua (Test) 🟢",
        "bill_phone": "🟢 Telefono (Test) 🟢",
        "bill_tax": "🟢 Tassa auto (Test) 🟢",
        "test_notice": "⚠️ <b>Avviso di test:</b>\n\nHai selezionato: <b>{item}</b>.\nQuesto bot è in fase di test gratuito. Nessun pagamento reale.",
        "feedback_prompt": "🟢 Inserisci il tuo feedback:",
        "feedback_thanks": "🟢 Feedback inviato!",
        "ledger_report": "🟢 <b>Registro di prova:</b> {count}",
        "test_payment_text": "🧪 <b>Pagamento di prova:</b>\n\nI servizi di pagamento sono disabilitati durante i test.",
        "stats_report": "📊 <b>Statistiche del bot:</b>\n\n👥 Utenti totali: <b>{users}</b>\n⚡ Interazioni totali: <b>{clicks}</b>",
        "quick_reply": "🟢 Bentornato in modalità test:",
        "share_text": "🤖 Prova il bot Lina AI:"
    },
    "es": {
        "welcome": "🟢 <b>¡Bienvenido a Lina Bot (Versión de prueba)!</b>\n\nEste bot está en modo de prueba gratuito. Selecciona un servicio a continuación:",
        "blocked": "Región bloqueada.",
        "real_estate": "🟢 Inmobiliaria (Prueba) 🟢",
        "cars": "🟢 Automoción (Prueba) 🟢",
        "services": "🟢 Servicios generales (Prueba) 🟢",
        "ledger": "🟢 Registro contable 🟢",
        "containers": "🟢 Contenedores (Prueba) 🟢",
        "support": "🟢 Soporte técnico 🟢",
        "feedback": "🟢 Dejar comentarios 🟢",
        "share_bot": "📤 Compartir bot con amigos 📤",
        "admin_stats": "📊 Estadísticas de Admin 📊",
        "sub": "🧪 Suscripción VIP (Prueba) 🧪",
        "web3": "🧪 Pago MetaMask (Prueba) 🧪",
        "bill_elec": "🟢 Electricidad (Prueba) 🟢",
        "bill_water": "🟢 Agua (Prueba) 🟢",
        "bill_phone": "🟢 Teléfono (Prueba) 🟢",
        "bill_tax": "🟢 Impuesto de vehículos (Prueba) 🟢",
        "test_notice": "⚠️ <b>Aviso de prueba:</b>\n\nHas seleccionado: <b>{item}</b>.\nEste bot está en modo de prueba gratuito. No hay pagos reales.",
        "feedback_prompt": "🟢 Escribe tus comentarios:",
        "feedback_thanks": "🟢 ¡Comentarios enviados!",
        "ledger_report": "🟢 <b>Registro de prueba:</b> {count}",
        "test_payment_text": "🧪 <b>Pago de prueba:</b>\n\nLos servicios de pago están deshabilitados durante las pruebas.",
        "stats_report": "📊 <b>Estadísticas del bot:</b>\n\n👥 Usuarios totales: <b>{users}</b>\n⚡ Interacciones totales: <b>{clicks}</b>",
        "quick_reply": "🟢 Bienvenido de nuevo al modo de prueba:",
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
    return "en"  # اللغة الافتراضية الإنجليزية في حال لم تكن اللغة ضمن الست

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
    
    # زر مشاركة تليجرام المباشر للأصدقاء داخل التطبيق
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
    bot_info = await bot.get_me()
    await message.answer(t["quick_reply"], reply_markup=get_main_keyboard(t, user_id, bot_info.username), parse_mode="HTML")

@dp.callback_query_handler(lambda call: True)
async def process_callbacks(call: types.CallbackQuery) -> None:
    user_id = call.from_user.id
    if call.from_user.language_code in BLOCKED_COUNTRIES:
        await call.answer("Blocked", show_alert=True)
        return

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
