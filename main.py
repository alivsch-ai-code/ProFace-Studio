import logging
import os
import uuid

from dotenv import load_dotenv
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    LabeledPrice,
    Update,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PreCheckoutQueryHandler,
    filters,
)

from ai_pipeline import AIPipeline, SYSTEM_PROMPTS
from database import Database


load_dotenv()
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("proface")


TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
NEON_DATABASE_URL = os.getenv("NEON_DATABASE_URL", "")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")
REPLICATE_PREVIEW_MODEL = os.getenv("REPLICATE_PREVIEW_MODEL", "google/nano-banana-2")
REPLICATE_FINAL_MODEL = os.getenv("REPLICATE_FINAL_MODEL", "google/nano-banana-pro")
WEBAPP_URL = os.getenv("WEBAPP_URL", "")
PRICE_XTR = int(os.getenv("PROFACE_PRICE_XTR", "49"))

if not TELEGRAM_TOKEN:
    raise RuntimeError("Missing TELEGRAM_TOKEN")
if not NEON_DATABASE_URL:
    raise RuntimeError("Missing NEON_DATABASE_URL")
if not REPLICATE_API_TOKEN:
    raise RuntimeError("Missing REPLICATE_API_TOKEN")

db = Database(NEON_DATABASE_URL)
ai = AIPipeline(
    api_key=REPLICATE_API_TOKEN,
    preview_model=REPLICATE_PREVIEW_MODEL,
    final_model=REPLICATE_FINAL_MODEL,
)


async def _file_ids_to_telegram_urls(bot, file_ids: list[str]) -> list[str]:
    out: list[str] = []
    for file_id in file_ids:
        try:
            tg_file = await bot.get_file(file_id)
            if tg_file.file_path:
                out.append(f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{tg_file.file_path}")
        except Exception:
            continue
    return out


def style_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("LinkedIn-Style", callback_data="style:linkedin")],
            [InlineKeyboardButton("Creative Studio", callback_data="style:creative")],
        ]
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_user or not update.effective_chat:
        return
    user = update.effective_user
    db.upsert_user(user.id, user.username)
    db.clear_uploads(user.id)
    db.set_stage(user.id, "await_template")
    context.user_data.clear()
    welcome = (
        "Willkommen bei ProFace.\n"
        "Sende zuerst ein Template, dann genau 5 Fotos.\n"
        "Danach starten wir die AI-Pipeline mit Telegram Stars."
    )
    await update.effective_chat.send_message(welcome, reply_markup=style_keyboard())
    if WEBAPP_URL:
        await update.effective_chat.send_message(f"WebApp: {WEBAPP_URL}")


async def new_session(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_user or not update.effective_chat:
        return
    user_id = update.effective_user.id
    db.clear_uploads(user_id)
    db.set_stage(user_id, "await_template")
    context.user_data.clear()
    await update.effective_chat.send_message(
        "Neue Session gestartet. Wähle ein Template:", reply_markup=style_keyboard()
    )


async def on_style_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    await query.answer()
    user_id = query.from_user.id
    _, style = query.data.split(":", 1)
    if style not in SYSTEM_PROMPTS:
        await query.edit_message_text("Unbekanntes Template.")
        return
    db.set_template(user_id, style)
    db.clear_uploads(user_id)
    await query.edit_message_text(
        f"Template gesetzt: {style}\nBitte sende jetzt 5 Fotos (1/5)."
    )


async def on_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_user or not update.message:
        return
    user_id = update.effective_user.id
    stage = db.get_stage(user_id)
    if stage != "await_uploads":
        await update.message.reply_text("Bitte zuerst ein Template wählen: /start")
        return

    photos = update.message.photo or []
    if not photos:
        await update.message.reply_text("Kein Foto gefunden.")
        return

    largest = photos[-1]
    slot = db.add_upload(user_id, largest.file_id)
    count = db.count_uploads(user_id)

    if count < 5:
        await update.message.reply_text(f"Foto gespeichert ({slot}/5). Bitte weiter senden.")
        return

    db.set_stage(user_id, "await_payment")
    payload = f"proface:{user_id}:{uuid.uuid4().hex}"
    db.create_pending_transaction(user_id, payload, PRICE_XTR)
    await update.message.reply_text("Top. 5/5 Fotos erhalten. Jetzt Zahlung via Telegram Stars:")
    await context.bot.send_invoice(
        chat_id=update.effective_chat.id,
        title="ProFace Business Portrait",
        description="Finales ProFace Rendering mit Nano Banana Pro",
        payload=payload,
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label="ProFace Render", amount=PRICE_XTR)],
    )


async def on_pre_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.pre_checkout_query
    if not query:
        return
    user_id = db.get_pending_payload_owner(query.invoice_payload)
    if user_id is None:
        await query.answer(ok=False, error_message="Ungültiger Warenkorb.")
        return
    await query.answer(ok=True)


async def on_successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.successful_payment or not update.effective_user:
        return

    payment = update.message.successful_payment
    payload = payment.invoice_payload
    user_id = update.effective_user.id
    db.mark_transaction_paid(
        payload=payload,
        tg_charge_id=payment.telegram_payment_charge_id,
        provider_charge_id=payment.provider_payment_charge_id,
    )

    file_ids = db.list_upload_file_ids(user_id)
    if len(file_ids) != 5:
        await update.message.reply_text("Es müssen genau 5 Fotos vorliegen. Bitte /newsession starten.")
        return
    input_urls = await _file_ids_to_telegram_urls(context.bot, file_ids)
    if len(input_urls) != 5:
        await update.message.reply_text("Konnte Upload-Dateien nicht auflösen. Bitte /newsession")
        return

    style = db.get_template(user_id) or "linkedin"
    db.set_stage(user_id, "rendering_previews")
    await update.message.reply_text("Zahlung bestätigt. Generiere Vorschauen (Nano Banana 2)...")

    previews = ai.generate_previews(style_key=style, image_inputs=input_urls)
    if not previews:
        db.set_stage(user_id, "await_template")
        await update.message.reply_text("Preview-Generierung fehlgeschlagen. Bitte /newsession")
        return

    context.user_data["preview_urls"] = previews
    buttons = [
        [InlineKeyboardButton(f"Vorschau {idx + 1} verwenden", callback_data=f"pick_preview:{idx}")]
        for idx in range(len(previews))
    ]
    media = [InputMediaPhoto(media=url) for url in previews]
    await update.message.reply_media_group(media)
    await update.message.reply_text(
        "Wähle eine Vorschau für das finale HQ-Rendering:",
        reply_markup=InlineKeyboardMarkup(buttons),
    )
    db.set_stage(user_id, "await_preview_pick")


async def on_pick_preview(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    await query.answer()
    user_id = query.from_user.id
    stage = db.get_stage(user_id)
    if stage != "await_preview_pick":
        await query.edit_message_text("Diese Auswahl ist nicht mehr aktiv.")
        return

    preview_urls = context.user_data.get("preview_urls") or []
    try:
        idx = int(query.data.split(":", 1)[1])
    except Exception:
        await query.edit_message_text("Ungültige Auswahl.")
        return
    if idx < 0 or idx >= len(preview_urls):
        await query.edit_message_text("Ungültige Auswahl.")
        return

    chosen = preview_urls[idx]
    file_ids = db.list_upload_file_ids(user_id)
    input_urls = await _file_ids_to_telegram_urls(context.bot, file_ids)
    if len(input_urls) != 5:
        await query.edit_message_text("Dateien konnten nicht aufgelöst werden. Bitte /newsession")
        return
    style = db.get_template(user_id) or "linkedin"
    db.set_stage(user_id, "rendering_final")
    await query.edit_message_text("Starte finales Rendering (Nano Banana Pro)...")

    final_url = ai.generate_final(style_key=style, image_inputs=input_urls, chosen_preview_url=chosen)
    await query.message.reply_photo(final_url, caption="Hier ist dein finales ProFace Business-Porträt.")
    db.set_stage(user_id, "completed")


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_chat:
        return
    await update.effective_chat.send_message(
        "/start - neuer Einstieg\n"
        "/newsession - Session zurücksetzen\n"
        "/help - Hilfe"
    )


def main() -> None:
    db.init_schema()
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("newsession", new_session))
    app.add_handler(CallbackQueryHandler(on_style_chosen, pattern=r"^style:"))
    app.add_handler(CallbackQueryHandler(on_pick_preview, pattern=r"^pick_preview:"))
    app.add_handler(MessageHandler(filters.PHOTO & ~filters.COMMAND, on_photo))
    app.add_handler(PreCheckoutQueryHandler(on_pre_checkout))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, on_successful_payment))
    logger.info("ProFace bot started")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
