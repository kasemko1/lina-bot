import logging
import json
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = os.getenv("BOT_TOKEN")

# رقم الآيدي الخاص بك للإدارة وتلقي الملاحظات والإحصائيات بشكل آمن
ADMIN_CHAT_ID = 8807102611  

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_states = {}
user_data = {}
user_ledger = {}

# ملف حفظ البيانات لضمان عدم ضياع الإحصائيات عند إعادة التشغيل أو التحديث
DATA_FILE = "bot_data.json"
user_interactions = set()
early_bird_users = set()
action_counter = {"clicks": 0}
EARLY_BIRD_LIMIT = 500

# تحميل البيانات السابقة إن وجدت
if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            saved_data = json.load(f)
            user_interactions = set(saved_data.get("users", []))
            early_bird_users = set(saved_data.get("early_birds", []))
            action_counter = {"clicks": saved_data.get("clicks", 0)}
    except Exception as e:
        logging.error(f"Error loading saved data: {e}")

# دالة لحفظ البيانات فوراً على القرص الصلب
def save_data():
    try:
        data = {
            "users": list(user_interactions),
            "early_birds": list(early_bird_users),
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
        "early_bird_btn": "🎯 حجز مبكر: الباقة السنوية (19.99€ بدلاً من 24.99€)",
        "bill_elec": "🟢 فاتورة الكهرباء",
        "bill_water": "🟢 فاتورة المياه",
        "bill_phone": "🟢 فاتورة الاتصالات",
        "bill_tax": "🟢 ضريبة المركبات",
        "test_notice": "⚠️ <b>تنبيه النسخة التجريبية:</b>\n\nلقد اخترت خدمة: <b>{item}</b>.\nهذا البوت في مرحلة الاختبار والتجربة المجانية ريثما يتم تأسيس الشركة رسمياً لضمان العمل النظامي والضريبي، ولا يتم خصم أي أموال حقيقية حالياً.",
        "feedback_prompt": "🟢 أهلاً بك. يرجى كتابة ملاحظتك أو شكواك في رسالة واحدة أدناه ليتم إرسالها للإدارة:",
        "feedback_thanks": "🟢 تم إرسال ملاحظتك بنجاح للإدارة، شكراً لتواصلك!",
        "ledger_report": "🟢 <b>السجل المحاسبي (التجريبي):</b> الحركات المسجلة: {count}",
        "test_payment_text": "🧪 <b>بوابة الدفع التجريبية:</b>\n\nهذه الخدمة مجانية حالياً أثناء الفترة التجريبية.\n\n💡 <b>رسوم الاستخدام المستقبلية بعد تأسيس الشركة:</b>\n• رسوم المعاملة الواحدة: <b>0.50 سنت</b>.\n• الاشتراك الشهري: <b>2.99 يورو</b>.\n• الاشتراك السنوي الأساسي: <b>24.99 يورو</b>.\n\nلن يتم خصم أي شيء منك الآن.",
        "early_bird_msg": "🟢 <b>أهلاً بك في قائمة الحجز المبكر الحصرية لبوت لينا!</b>\n\nنود إعلامك أن \"بوت لينا\" يعمل حالياً في <b>فترة تجريبية مجانية بالكامل</b> (تستمر من 3 أسابيع إلى شهر)، ولن يتم تفعيل الخدمات المدفوعة أو الإطلاق الرسمي والنظامي الكامل إلا بعد استكمال كافة الإجراءات وتأسيس الشركة بشكل رسمي وقانوني في ألمانيا.\n\n🎁 <b>مكافأة الحجز المبكر (بدون أي رسوم حالياً):</b>\n• التسجيل والحجز الآن <b>مجاني 100%</b> ولا يتطلب دفع أي مبالغ مالية.\n• هذا الحجز يضمن لك الحصول على <b>الباقة السنوية بسعر حصري 19.99 يورو</b> (بدلاً من السعر الأساسي <b>24.99 يورو</b>) فور الإطلاق الرسمي والنظامي للشركة.\n• <b>ملاحظة:</b> هذا العرض خاص وحصري فقط لـ <b>أول 500 شخص</b> يقومون بالتسجيل المبدئي!\n\n📊 <i>عدد المسجلين في قائمة الحجز المبكر حتى الآن: <b>{count} / 500</b></i>",
        "early_bird_success": "✅ <b>تم تسجيلك بنجاح في قائمة الحجز المبكر الحصرية!</b>\n\nتم تثبيت مقعدك ضمن أول 500 مستفيد للحصول على الباقة السنوية بـ 19.99 يورو (بدلاً من 24.99 يورو) فور الإطلاق الرسمي.",
        "early_bird_already": "⚠️ <b>أنت مسجل بالفعل!</b>\n\nلقد قمت بحجز مقعدك مسبقاً في قائمة الحجز المبكر.",
        "early_bird_full": "⚠️ عذراً، اكتمل العدد المخصص للحجز المبكر (500 مشترك).",
        "stats_report": "📊 <b>إحصائيات تفاعل البوت (محفوظة دائماً):</b>\n\n👥 عدد المستخدمين الكلي: <b>{users}</b>\n⚡ عدد تفاعلات النقر والخدمات: <b>{clicks}</b>\n🎯 مسجلو الحجز المبكر: <b>{early_count} / 500</b>",
        "quick_reply": "🟢 مرحباً بك مجدداً. اختر إحدى الخدمات من القائمة أدناه:",
        "share_text": "🤖 منصة الأعمال الذكية بوت لينا (Lina AI). جربه الآن:"
    },
    "de": {
        "welcome": "🟢 <b>Willkommen beim Lina Bot (Smart Business Platform)!</b>\n\n⚠️ <i>Hinweis: Der Bot befindet sich in der Testphase (3 Wochen bis 1 Monat). Offizieller Start erst nach offizieller Firmengründung in Deutschland.</i>\n\nWählen Sie unten einen Dienst aus:",
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
        "early_bird_btn": "🎯 Frühbucher: Jahresabo (19.99€ statt 24.99€)",
        "bill_elec": "🟢 Stromrechnung",
        "bill_water": "🟢 Wasserrechnung",
        "bill_phone": "🟢 Telefonrechnung",
        "bill_tax": "🟢 Kfz-Steuer",
        "test_notice": "⚠️ <b>Test-Hinweis:</b>\n\nSie haben gewählt: <b>{item}</b>.\nDer Bot befindet sich in der Testphase vor der offiziellen Registrierung.",
        "feedback_prompt": "🟢 Bitte geben Sie Ihr Feedback ein:",
        "feedback_thanks": "🟢 Vielen Dank! Ihr Feedback wurde gesendet.",
        "ledger_report": "🟢 <b>Test-Buchhaltung:</b> Registrierte Einträge: {count}",
        "test_payment_text": "🧪 <b>Zahlungssystem:</b>\n\nKostenlos in der Testphase.\n\n💡 <b>Zukünftige Gebühren:</b>\n• Transaktion: <b>0.50€</b>\n• Monatsabo: <b>2.99€</b>\n• Jahresabo regulär: <b>24.99€</b>\n\nEs wird jetzt nichts abgebucht.",
        "early_bird_msg": "🟢 <b>Willkommen auf der exklusiven Frühbucher-Warteliste!</b>\n\nDer Lina Bot befindet sich in einer <b>kostenlosen Testphase</b> (3 Wochen bis 1 Monat). Der offizielle Start erfolgt erst nach vollständiger Firmengründung in Deutschland.\n\n🎁 <b>Frühbucher-Vorteil (jetzt 100% kostenlos):</b>\n• Keine Gebühren während der Testphase.\n• Sichern Sie sich das Jahresabo zum Vorzugspreis von <b>19.99€</b> (statt regulär <b>24.99€</b>) nach dem offiziellen Start.\n• Exklusiv für die <b>ersten 500 Registrierungen</b>!\n\n📊 <i>Bereits registriert: <b>{count} / 500</b></i>",
        "early_bird_success": "✅ <b>Erfolgreich in der Frühbucher-Liste registriert!</b>\n\nIhr Platz unter den ersten 500 für das Jahresabo zu 19.99€ (statt 24.99€) ist gesichert.",
        "early_bird_already": "⚠️ Sie sind bereits in der Frühbucher-Liste registriert.",
        "early_bird_full": "⚠️ Das Kontingent für Frühbucher (500) ist leider erschöpft.",
        "stats_report": "📊 <b>Bot-Statistiken:</b>\n\n👥 Gesamtzahl der Benutzer: <b>{users}</b>\n⚡ Gesamtzahl der Interaktionen: <b>{clicks}</b>\n🎯 Frühbucher: <b>{early_count} / 500</b>",
        "quick_reply": "🟢 Willkommen zurück. Wählen Sie eine Option:",
        "share_text": "🤖 Entdecken Sie den Lina KI Bot:"
    },
    "en": {
        "welcome": "🟢 <b>Welcome to Lina Bot (Smart Business Platform)!</b>\n\n⚠️ <i>Note: Free trial phase (3 weeks to 1 month). Full launch follows official company registration in Germany.</i>\n\nSelect a service below:",
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
        "early_bird_btn": "🎯 Early Bird: Annual Pass (19.99€ instead of 24.99€)",
        "bill_elec": "🟢 Electricity",
        "bill_water": "🟢 Water",
        "bill_phone": "🟢 Phone",
        "bill_tax": "🟢 Car Tax",
        "test_notice": "⚠️ <b>Test Notice:</b>\n\nYou selected: <b>{item}</b>.\nThis bot is in a free test mode pending formal company setup.",
        "feedback_prompt": "🟢 Type your feedback:",
        "feedback_thanks": "🟢 Feedback sent!",
        "ledger_report": "🟢 <b>Ledger:</b> {count}",
        "test_payment_text": "🧪 <b>Payment Gateway:</b>\n\nFree during the trial phase.\n\n💡 <b>Future Fees:</b>\n• Per transaction: <b>0.50€</b>\n• Monthly subscription: <b>2.99€</b>\n• Regular Annual subscription: <b>24.99€</b>\n\nNo charges will be made now.",
        "early_bird_msg": "🟢 <b>Welcome to Lina Bot Early Bird Waitlist!</b>\n\nOperating in a <b>free trial phase</b> (3 weeks to 1 month). Official rollout takes place after formal company incorporation in Germany.\n\n🎁 <b>Early Bird Perks (100% Free Now):</b>\n• Zero charges today.\n• Secure the annual plan for <b>19.99€</b> (instead of the regular <b>24.99€</b>) upon official launch.\n• Strictly limited to the <b>first 500 users</b>!\n\n📊 <i>Registered so far: <b>{count} / 500</b></i>",
        "early_bird_success": "✅ <b>Successfully registered for Early Bird access!</b>\n\nYour spot is secured for the annual pass at 19.99€ (instead of 24.99€).",
        "early_bird_already": "⚠️ You are already on the early bird list.",
        "early_bird_full": "⚠️ Early bird capacity (500 users) has been reached.",
        "stats_report": "📊 <b>Bot Statistics:</b>\n\n👥 Total Users: <b>{users}</b>\n⚡ Total Interactions: <b>{clicks}</b>\n🎯 Early Bird Signups: <b>{early_count} / 500</b>",
        "quick_reply": "🟢 Welcome back:",
        "share_text": "🤖 Try the Lina AI Bot:"
    },
    "fr": {
        "welcome": "🟢 <b>Bienvenue sur Lina Bot !</b>\n\n⚠️ <i>Phase de test gratuite (3 semaines à 1 mois). Lancement officiel après enregistrement de l'entreprise en Allemagne.</i>\n\nSélectionnez un service :",
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
        "early_bird_btn": "🎯 Offre Précoce : Annuel (19.99€ au lieu de 24.99€)",
        "bill_elec": "🟢 Électricité",
        "bill_water": "🟢 Eau",
        "bill_phone": "🟢 Téléphone",
        "bill_tax": "🟢 Taxe auto",
        "test_notice": "⚠️ <b>Avis de test :</b>\n\nVous avez sélectionné : <b>{item}</b>.",
        "feedback_prompt": "🟢 Entrez vos commentaires :",
        "feedback_thanks": "🟢 Commentaires envoyés !",
        "ledger_report": "🟢 <b>Registre :</b> {count}",
        "test_payment_text": "🧪 <b>Paiement :</b>\n\nGratuit pendant la phase de test.\n\n💡 <b>Tarifs futurs :</b>\n• Transaction : <b>0.50€</b>\n• Abonnement mensuel : <b>2.99€</b>\n• Abonnement annuel : <b>24.99€</b>",
        "early_bird_msg": "🟢 <b>Bienvenue sur la liste d'attente anticipée !</b>\n\nPhase de test gratuite. Réservé aux <b>500 premiers utilisateurs</b>.\n\n🎁 Obtenez l'annuel pour <b>19.99€</b> au lieu de <b>24.99€</b>.\n\n📊 <i>Inscrits : <b>{count} / 500</b></i>",
        "early_bird_success": "✅ <b>Inscription réussie !</b> Votre place est réservée.",
        "early_bird_already": "⚠️ Vous êtes déjà inscrit.",
        "early_bird_full": "⚠️ Capacité maximale atteinte.",
        "stats_report": "📊 <b>Statistiques :</b>\n\n👥 Utilisateurs : <b>{users}</b>\n⚡ Interactions : <b>{clicks}</b>\n🎯 Pré-inscriptions : <b>{early_count} / 500</b>",
        "quick_reply": "🟢 Bon retour :",
        "share_text": "🤖 Essayez le bot Lina AI :"
    },
    "it": {
        "welcome": "🟢 <b>Benvenuto in Lina Bot!</b>\n\n⚠️ <i>Fase di prova gratuita. Lancio ufficiale dopo la registrazione dell'azienda in Germania.</i>\n\nSeleziona un servizio:",
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
        "early_bird_btn": "🎯 Prenotazione anticipata (19.99€ anziché 24.99€)",
        "bill_elec": "🟢 Elettricità",
        "bill_water": "🟢 Acqua",
        "bill_phone": "🟢 Telefono",
        "bill_tax": "🟢 Tassa auto",
        "test_notice": "⚠️ <b>Avviso di test:</b>\n\nHai selezionato: <b>{item}</b>.",
        "feedback_prompt": "🟢 Inserisci il tuo feedback:",
        "feedback_thanks": "🟢 Feedback inviato!",
        "ledger_report": "🟢 <b>Registro:</b> {count}",
        "test_payment_text": "🧪 <b>Pagamento:</b>\n\nGratuito durante la fase di prova.\n\n💡 <b>Tariffe future:</b>\n• Transazione: <b>0.50€</b>\n• Abbonamento mensile: <b>2.99€</b>\n• Abbonamento annuale: <b>24.99€</b>",
        "early_bird_msg": "🟢 <b>Benvenuto nella lista d'attesa anticipata!</b>\n\nRiservato ai primi <b>500 utenti</b>.\n\n🎁 Assicurati l'annuale a <b>19.99€</b> anziché <b>24.99€</b>.\n\n📊 <i>Registrati: <b>{count} / 500</b></i>",
        "early_bird_success": "✅ <b>Registrazione completata!</b>",
        "early_bird_already": "⚠️ Sei già registrato.",
        "early_bird_full": "⚠️ Posti esauriti.",
        "stats_report": "📊 <b>Statistiche:</b>\n\n👥 Utenti: <b>{users}</b>\n⚡ Interazioni: <b>{clicks}</b>\n🎯 Early Bird: <b>{early_count} / 500</b>",
        "quick_reply": "🟢 Bentornato:",
        "share_text": "🤖 Prova il bot Lina AI:"
    },
    "es": {
        "welcome": "🟢 <b>¡Bienvenido a Lina Bot!</b>\n\n⚠️ <i>Fase de prueba gratuita. Lanzamiento oficial tras el registro de la empresa en Alemania.</i>\n\nSelecciona un servicio:",
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
        "early_bird_btn": "🎯 Reserva anticipada (19.99€ en vez de 24.99€)",
        "bill_elec": "🟢 Electricidad",
        "bill_water": "🟢 Agua",
        "bill_phone": "🟢 Teléfono",
        "bill_tax": "🟢 Impuesto de vehículos",
        "test_notice": "⚠️ <b>Aviso de prueba:</b>\n\nHas seleccionado: <b>{item}</b>.",
        "feedback_prompt": "🟢 Escribe tus comentarios:",
        "feedback_thanks": "🟢 ¡Comentarios enviados!",
        "ledger_report": "🟢 <b>Registro:</b> {count}",
        "test_payment_text": "🧪 <b>Pago:</b>\n\nGratis durante la prueba.\n\n💡 <b>Tarifas futuras:</b>\n• Transacción: <b>0.50€</b>\n• Suscripción mensual: <b>2.99€</b>\n• Suscripción anual: <b>24.99€</b>",
        "early_bird_msg": "🟢 <b>¡Bienvenido a la lista de reserva anticipada!</b>\n\nExclusivo para los <b>primeros 500 usuarios</b>.\n\n🎁 Consigue el plan anual por <b>19.99€</b> en vez de <b>24.99€</b>.\n\n📊 <i>Registrados: <b>{count} / 500</b></i>",
        "early_bird_success": "✅ <b>¡Registro exitoso!</b> Tu plaza está asegurada.",
        "early_bird_already": "⚠️ Ya estás registrado.",
        "early_bird_full": "⚠️ Cupo completo.",
        "stats_report": "📊 <b>Estadísticas:</b>\n\n👥 Usuarios: <b>{users}</b>\n⚡ Total interactions: <b>{clicks}</b>\n🎯 Early Bird: <b>{early_count} / 500</b>",
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
    save_data()
    lang = get_lang(message)
    t = TRANSLATIONS[lang]
    current_state = user_states.get(user_id, "main_menu")

    if current_state == "waiting_for_feedback":
        user_states[user_id] = "main_menu"
        user_text = message.text
        try:
            admin_msg = f"🟢 <b>ملاحظة جديدة في البوت (تجريبي):</b>\n\n💬 النص:\n<i>{user_text}</i>"
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

    if call.data == "admin_stats" and user_id == ADMIN_CHAT_ID:
        total_users = len(user_interactions)
        total_clicks = action_counter["clicks"]
        early_count = len(early_bird_users)
        await call.message.answer(t["stats_report"].format(users=total_users, clicks=total_clicks, early_count=early_count), parse_mode="HTML")
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
