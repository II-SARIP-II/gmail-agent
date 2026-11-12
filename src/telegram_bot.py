import asyncio
import os

from dotenv import load_dotenv
from telegram import (
    Bot,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)

from src.models.mail import Mail
from src.smtp_sender import sendEmail

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID", "0"))


class TelegramBot:
    def __init__(self, mails: list[Mail]):
        if not TOKEN or not CHAT_ID:
            raise ValueError("TELEGRAM_BOT_TOKEN or CHAT_ID not found in .env")

        self.mails = mails
        self.reponse_queue: asyncio.Queue[str] = asyncio.Queue()

        self.app = ApplicationBuilder().token(token=TOKEN).build()
        self.app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_message)
        )

    async def start(self) -> None:
        """Démarre le bot et lance le traitement des e-mails."""
        if not self.mails:
            return

        async with self.app:
            await self.app.start()
            if self.app.updater:
                await self.app.updater.start_polling()

            await self.process_mails(self.app.bot)

            if self.app.updater:
                await self.app.updater.stop()
            await self.app.stop()

    async def get_message(self, update: Update,
                          context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.effective_chat and update.effective_chat.id == CHAT_ID:
            if update.message and update.message.text:
                await self.reponse_queue.put(update.message.text.strip())

    async def process_mails(self, bot: Bot) -> None:
        clavier_choix = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton("Response 1"), KeyboardButton("Response 2")],
                [KeyboardButton("Write your response"),
                 KeyboardButton("Ignore")],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )

        for i, mail in enumerate(self.mails, start=1):
            body_preview = (
                mail.message[:2000] + "..."
                if len(mail.message) > 2000
                else mail.message
            )

            message_text = (
                f"📩 Mail {i}/{len(self.mails)}\n"
                f"De : {mail.sender}\n"
                f"Sujet : {mail.subject}\n\n"
                f"Message :\n{body_preview}\n\n"
                f"--- Proposition 1 ---\n{mail.response1}\n\n"
                f"--- Proposition 2 ---\n{mail.response2}"
            )

            await bot.send_message(
                chat_id=CHAT_ID,
                text=message_text,
                reply_markup=clavier_choix,
            )

            choice = await self.reponse_queue.get()

            if choice == "Response 1":
                await bot.send_message(
                    chat_id=CHAT_ID,
                    text="✅ Response 1 sent.",
                    reply_markup=ReplyKeyboardRemove(),
                )
                sendEmail(mail.response1, mail.sender)

            elif choice == "Response 2":
                await bot.send_message(
                    chat_id=CHAT_ID,
                    text="✅ Response 2 sent.",
                    reply_markup=ReplyKeyboardRemove(),
                )
                sendEmail(mail.response2, mail.sender)

            elif choice == "Write your response":
                await bot.send_message(
                    chat_id=CHAT_ID,
                    text="✍️ Write your own response:",
                    reply_markup=ReplyKeyboardRemove(),
                )
                user_reponse = await self.reponse_queue.get()
                await bot.send_message(
                    chat_id=CHAT_ID,
                    text=f"✅ Response sent:\n« {user_reponse} »",
                )
                sendEmail(user_reponse, mail.sender)

            else:
                await bot.send_message(
                    chat_id=CHAT_ID,
                    text="⏭️ Ignored.",
                    reply_markup=ReplyKeyboardRemove(),
                )

        await bot.send_message(chat_id=CHAT_ID, text="All mails processed!")
