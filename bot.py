"""Lina Telegram broker bot for Replit.

Required Secrets:
    BOT_TOKEN
    POLYGONSCAN_API_KEY
"""

import asyncio
import logging
import os
import re
import tempfile
import threading
from typing import Any

import requests
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from flask import Flask
from gtts import gTTS


logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("lina-bot")

BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
POLYGONSCAN_API_KEY = os.environ.get("POLYGONSCAN_API_KEY", "").strip()

ADMIN_ID = 7123144123
WEB3_WALLET = "0x0e3c35B1242dB3f7E60E554266eB7be90706f355"
WEB3_NETWORK = "Polygon"
USDT_CONTRACT = "0xc2132d05d31c914a87c6611c10748aeb04b58e8f"
PORT = int(os.environ.get("PORT", "8080"))

TX_HASH_RE = re.compile(r"^0x[a-fA-F0-9]{64}$")
PAYMENT_TOLERANCE = 0.05

# A harmless placeholder keeps module import and static checks usable before
# the user adds the real Secret. validate_configuration() blocks startup.
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
user_data: dict[int, dict[str, Any]] = {}
used_payments: set[str] = set()

flask_app = Flask(__name__)


@flask_app.get("/")
def home() -> str:
    return "Lina bot is alive!"


@flask_app.get("/health")
def health() -> tuple[dict[str, str], int]:
    ready = bool(TOKEN and POLYGONSCAN_API_KEY)
    return ({"status": "ok" if ready else "missing_secrets"}, 200 if ready else 503)


def run_flask() -> None:
    flask_app.run(host="0.0.0.0", port=PORT, use_reloader=False)


async def send_lina_voice(chat_id: int, text: str) -> None:
    """Generate Arabic speech off the event loop and send it as a voice note."""
    audio_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as audio:
            audio_path = audio.name
        await asyncio.to_thread(gTTS(text=text, lang="ar", slow=False).save, audio_path)
        with open(audio_path, "rb") as voice:
            await bot.send_voice(chat_id, voice)
    except Exception:
        logger.exception("Voice message failed; sending text fallback")
        await bot.send_message(chat_id, text)
    finally:
        if audio_path:
            try:
                os.unlink(audio_path)
            except OSError:
                logger.warning("Could not remove temporary audio file %s", audio_path)


@dp.message_handler(commands=["start"])
async def start(message: types.Message) -> None:
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("سيارات", callback_data="cars"),
        InlineKeyboardButton("عقارات", callback_data="real"),
        InlineKeyboardButton("كونتينرات", callback_data="containers"),
        InlineKeyboardButton("خدمات", callback_data="services"),
        InlineKeyboardButton("اشتراكي 2.99€", callback_data="sub"),
    )
    text_voice = (
        "أهلا وسهلا بحضرتكم، معكم لينا من مكتب الوساطة، رسوم العملية خمسين سنت "
        "فقط، والاشتراك الشهري اثنان فاصل تسعة وتسعون يورو، كيف يمكنني مساعدتكم اليوم؟"
    )
    await send_lina_voice(message.chat.id, text_voice)
    await message.answer(
        "أهلا وسهلا! أنا لينا\n\n"
        "رسوم العملية 0.50€ - الاشتراك الشهري 2.99€\n\n"
        "شو بتحب أساعدك اليوم؟",
        reply_markup=keyboard,
    )


@dp.callback_query_handler(lambda call: True)
async def process(call: types.CallbackQuery) -> None:
    user_id = call.from_user.id
    await call.answer()
if call.data == "web3":
        voice_text = (
            "لإتمام الطلب، يرجى دفع رسوم فتح الطلب وقدرها خمسين سنت فقط عبر العملات الرقمية."
        )
        await send_lina_voice(call.message.chat.id, voice_text)
        await call.message.answer(
            f"💳 **الدفع عبر العملات الرقمية (Web3):**\n\n"
            f"📍 **العنوان:** `{WEB3_WALLET}`\n"
            f"🌐 **الشبكة:** {WEB3_NETWORK}\n"
            f"💰 **المبلغ المطلوب:** 0.50 USDT\n\n"
            f"بعد الدفع، يرجى إرسال رقم العملية (Tx Hash) الذي يبدأ بـ (0x...).",
            parse_mode="Markdown",
        )
        return    ) await send_lina_voice(
        call.message.chat.id,
        f"ممتاز، رسوم الخدمة {price} فقط، يرجى الدفع بالعملات الرقمية لفتح الطلب",
    ) await call.message.answer(
        f"ممتاز!\nرسوم الخدمة **{price} فقط**\n\nادفع كريبتو ليفتح الطلب:",
        reply_markup=keyboard,
        parse_mode="Markdown",
    )@dp.message_handler(lambda message: bool(message.text) and message.text.startswith("0x"))
async def verify_tx(message: types.Message) -> None:
    tx_hash = message.text.strip()
    if not TX_HASH_RE.fullmatch(tx_hash):
        await message.answer("صيغة Tx Hash غير صحيحة. أرسل 64 خانة بعد 0x.")
        return

    await message.answer("عم أتأكد من الدفعة، لحظة من فضلك...")
    await send_lina_voice(message.chat.id, "لحظة من فضلك، جاري التأكد من عملية الدفع الخاصة بكم")

    normalized_hash = tx_hash.lower()
    if normalized_hash in used_payments:
        await message.answer("هذا الرقم مستخدم من قبل.")
        return

    verified = await asyncio.to_thread(check_payment, normalized_hash, 0.50)
    if verified:
        used_payments.add(normalized_hash)
        await send_lina_voice(
            message.chat.id,
            "شكرا لكم، تم تأكيد الدفع بنجاح، تم تفعيل طلبكم وسيتم التواصل معكم بأقرب وقت",
        )
        await message.answer("تم الدفع! طلبك اتفعل ورح نتواصل معك.")
        username = message.from_user.username or "بدون username"
        await bot.send_message(ADMIN_ID, f"دفع مؤكد! Tx: {tx_hash} من @{username}")
    else:
        await send_lina_voice(
            message.chat.id,
            "عذرا، لم أجد عملية الدفع، يرجى التأكد من الشبكة بوليغون والمحاولة بعد دقيقة",
        )
        await message.answer("ما لقيت الدفعة. تأكد من شبكة Polygon وجرب بعد دقيقة.")

@dp.message_handler(lambda message: bool(message.text) and not message.text.startswith("0x"))
async def steps(message: types.Message) -> None:
    user_id = message.from_user.id
    if user_id not in user_data:
        return

    current = user_data[user_id]
    step = current.get("step", 0)
    if step == 1:
        current["what"], current["step"] = message.text, 2
        await send_lina_voice(message.chat.id, "شكرا لك، والآن من أين إلى أين؟")
        await message.answer("2. من وين لوين؟")
    elif step == 2:
        current["where"], current["step"] = message.text, 3
        await send_lina_voice(message.chat.id, "تمام، وما هي ميزانيتكم الكريمة؟")
        await message.answer("3. ميزانيتك؟")
    elif step == 3:
        current["budget"], current["step"] = message.text, 4
        await send_lina_voice(message.chat.id, "ممتاز، أخيرا ما هو رقم الواتساب للتواصل مع حضرتكم؟")
        await message.answer("4. رقم واتساب؟")
    elif step == 4:
        current["phone"] = message.text
        await send_request_to_admin(user_id, current)
        price = "2.99€ اشتراك" if current["type"] == "sub" else "0.50€ عملية"
        keyboard = InlineKeyboardMarkup().add(
            InlineKeyboardButton(f"ادفع {price}", callback_data="web3")
        )
        await send_lina_voice(
            message.chat.id,
            f"شكرا لكم تم استلام بياناتكم، لإتمام الطلب يرجى دفع رسوم {price}",
        )
        await message.answer(
            f"تمام! لفتح الطلب ادفع **{price}**",
            reply_markup=keyboard,
            parse_mode="Markdown",
        )
async def send_request_to_admin(user_id: int, info: dict[str, Any]) -> None:
    await bot.send_message(
        ADMIN_ID,
        f"طلب جديد:\nنوع: {info['type']}\nشو بده: {info['what']}\n"
        f"من وين: {info['where']}\nميزانية: {info['budget']}\n"
        f"واتساب: {info['phone']}\nID: {user_id}",
    )
def check_payment(tx_hash: str, expected_amount: float) -> bool:
    """Confirm an incoming Polygon USDT transfer to our wallet."""
    if not POLYGONSCAN_API_KEY:
        logger.error("POLYGONSCAN_API_KEY is not configured")
        return False

    try:
        response = requests.get(
            "https://api.polygonscan.com/api",
            params={
                "module": "account",
                "action": "tokentx",
                "contractaddress": USDT_CONTRACT,
                "address": WEB3_WALLET,
                "page": 1,
                "offset": 100,
                "sort": "desc",
                "apikey": POLYGONSCAN_API_KEY,
            },
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()
        for transaction in payload.get("result", []):
            if transaction.get("hash", "").lower() != tx_hash.lower():
                continue
            amount = int(transaction["value"]) / 10 ** int(transaction["tokenDecimal"])
            is_incoming = transaction.get("to", "").lower() == WEB3_WALLET.lower()
            return is_incoming and amount >= expected_amount - PAYMENT_TOLERANCE
    except (requests.RequestException, ValueError, KeyError, TypeError):
        logger.exception("PolygonScan payment check failed")
    return False


def validate_configuration() -> None:
    missing = [name for name, value in {
        "BOT_TOKEN": BOT_TOKEN,
        "POLYGONSCAN_API_KEY": POLYGONSCAN_API_KEY,
    }.items() if not value]
    if missing:
        raise RuntimeError(
            "Missing required Replit Secrets: " + ", ".join(missing)
        )


if __name__ == "__main__":
    validate_configuration()
    threading.Thread(target=run_flask, daemon=True, name="health-server").start()
    logger.info("Lina bot starting on port %s", PORT)
    executor.start_polling(dp, skip_updates=True)
