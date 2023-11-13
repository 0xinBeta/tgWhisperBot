import logging
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import keys
import whisper
import tempfile
from io import BytesIO
import openai
from elevenlabs import set_api_key, generate


model = whisper.load_model("large-v3")

token = keys.BOT_TOKEN
openai.api_key = keys.OPENAI_API
set_api_key(f"{keys.ELEVEN_API}")


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


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle voice messages."""
    voice = update.message.voice
    voice_file = await voice.get_file()

    voice_io = BytesIO()
    # download_path = "audio.ogg"
    await voice_file.download_to_memory(out=voice_io)
    voice_io.seek(0)

    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=True) as tmp_file:
        tmp_file.write(voice_io.read())
        tmp_file.flush()

        result = model.transcribe(tmp_file.name, fp16=False)

    question = result['text']

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"{question}"}
        ]   
    )

    bot_resp = completion.choices[0].message.content

    audio = generate(
        text=f"{bot_resp}",
        voice="Bella",
        model="eleven_multilingual_v2"
    )

    await update.message.reply_voice(audio=audio)


def main() -> None:
    """Start the bot."""
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("hello", hello))

    # Handle voice messages
    voice_handler = MessageHandler(filters.VOICE, handle_voice)
    application.add_handler(voice_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
