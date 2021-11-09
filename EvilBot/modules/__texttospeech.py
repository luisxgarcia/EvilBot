from EvilBot import telethn as tbot
import os

from gtts import gTTS
from gtts import gTTSError
from telethon import *
from telethon.tl import functions
from telethon.tl import types
from telethon.tl.types import *

from EvilBot import *

from EvilBot.events import register

async def is_register_admin(chat, user):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):
        return isinstance(
            (
                await tbot(functions.channels.GetParticipantRequest(chat, user))
            ).participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator, types.ChannelParticipant),
        )
    if isinstance(chat, types.InputPeerUser):
        return True

@register(pattern="^/tts (.*)")
async def _(event):

    input_str = event.pattern_match.group(1)
    reply_to_id = event.message.id
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        text = previous_message.message
        lan = input_str
    elif "|" in input_str:
        lan, text = input_str.split("|")
    else:
        await event.reply(
            "Sintaxis invalida\nFormato `/tts idioma | text`\nPor ejemplo: `/tts en | hello`"
        )
        return
    text = text.strip()
    lan = lan.strip()
    try:
        tts = gTTS(text, tld="com", lang=lan)
        tts.save("k.mp3")
    except AssertionError:
        await event.reply(
            "El texto esta vacio.\n"
            "No queda nada para hablar después del preprocesamiento, "
            "tokenizing and cleaning."
        )
        return
    except ValueError:
        await event.reply("El idioma no es compatible.")
        return
    except RuntimeError:
        await event.reply("Error al cargar el diccionario de idiomas.")
        return
    except gTTSError:
        await event.reply("Error en la solicitud de la API de texto a voz de Google!")
        return
    with open("k.mp3", "r"):
        await tbot.send_file(
            event.chat_id, "k.mp3", voice_note=True, reply_to=reply_to_id
        )
        os.remove("k.mp3")
