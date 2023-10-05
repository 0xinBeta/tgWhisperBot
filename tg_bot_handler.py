import logging
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, ContextTypes, filters
import keys

import whisper

model = whisper.load_model("base")
result = model.transcribe("audio.mp3")
print(result["text"])



token = keys.BOT_TOKEN

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /hello is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hello {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(token=token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("hello", hello))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
