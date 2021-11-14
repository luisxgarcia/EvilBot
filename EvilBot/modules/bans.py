import html

from telegram import ParseMode, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler, Filters, run_async
from telegram.utils.helpers import mention_html

from EvilBot import (
    DEV_USERS,
    LOGGER,
    OWNER_ID,
    DRAGONS,
    DEMONS,
    TIGERS,
    WOLVES,
    dispatcher,
)
from EvilBot.modules.disable import DisableAbleCommandHandler
from EvilBot.modules.helper_funcs.chat_status import (
    bot_admin,
    can_restrict,
    connection_status,
    is_user_admin,
    is_user_ban_protected,
    is_user_in_chat,
    user_admin,
    user_can_ban,
    can_delete,
)
from EvilBot.modules.helper_funcs.extraction import extract_user_and_text
from EvilBot.modules.helper_funcs.string_handling import extract_time
from EvilBot.modules.log_channel import gloggable, loggable


@run_async
@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def ban(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot = context.bot
    args = context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("Dudo que sea un usuario.")
        return log_message
    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "User not found":
            raise
        message.reply_text("Parece que no puedo encontrar a esta persona.")
        return log_message
    if user_id == bot.id:
        message.reply_text("Oh sí, banéame, estupidx!")
        return log_message

    if is_user_ban_protected(chat, user_id, member) and user not in DEV_USERS:
        if user_id == OWNER_ID:
            message.reply_text("Tratando de ponerme en contra de alguin nivel Dios, ¿eh?")
        elif user_id in DEV_USERS:
            message.reply_text("I can't act against our own.")
        elif user_id in DRAGONS:
            message.reply_text(
                "Luchar contra este Dragón aquí pondrá en peligro la vida de civiles."
            )
        elif user_id in DEMONS:
            message.reply_text(
                "Lleva una orden de la asociación de héroes para luchar contra un demonio."
            )
        elif user_id in TIGERS:
            message.reply_text(
                "Traiga una orden de la asociación de héroes para luchar contra un tigre."
            )
        elif user_id in WOLVES:
            message.reply_text("¡Las habilidades de los lobos los hacen inmunes!")
        else:
            message.reply_text("Este usuario tiene inmunidad y no puede ser prohibido.")
        return log_message
    if message.text.startswith("/s"):
        silent = True
        if not can_delete(chat, context.bot.id):
            return ""
    else:
        silent = False
    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#{'S' if silent else ''}BANEADO\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>User:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
    )
    if reason:
        log += "\n<b>Razon:</b> {}".format(reason)

    try:
        chat.kick_member(user_id)

        if silent:
            if message.reply_to_message:
                message.reply_to_message.delete()
            message.delete()
            return log

        bot.send_sticker(chat.id, "CAACAgEAAxkBAAICL2GIS1rV-HBllEQYxBcSjh4XnpBJAAIDAQACPF8xRmEkSUQJNOg6IgQ")  # banhammer marie sticker
        reply = (
            f"<code>❕</code><b>Evento Ban</b>\n"
            f"<code> </code><b>•  Usuario:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
        )
        if reason:
            reply += f"\n<code> </code><b>•  Razon:</b> \n{html.escape(reason)}"
        bot.sendMessage(chat.id, reply, parse_mode=ParseMode.HTML, quote=False)
        return log

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            if silent:
                return log
            message.reply_text("Baneadx!", quote=False)
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR baneando al usuario %s en el chat %s (%s) debido a %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("Uhm ... eso no funcionó ...")

    return log_message


@run_async
@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def temp_ban(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("Dudo que sea un usuario.")
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "User not found":
            raise
        message.reply_text("Parece que no puedo encontrar a este usuario.")
        return log_message
    if user_id == bot.id:
        message.reply_text("Yo no me voy a BANEAR, are u ok?")
        return log_message

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("No me apetece.")
        return log_message

    if not reason:
        message.reply_text("¡No has especificado un momento para prohibir a este usuario!")
        return log_message

    split_reason = reason.split(None, 1)

    time_val = split_reason[0].lower()
    reason = split_reason[1] if len(split_reason) > 1 else ""
    bantime = extract_time(message, time_val)

    if not bantime:
        return log_message

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        "#TEMP BANNED\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>Usuario:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}\n"
        f"<b>Tiempo:</b> {time_val}"
    )
    if reason:
        log += "\n<b>Razon:</b> {}".format(reason)

    try:
        chat.kick_member(user_id, until_date=bantime)
        bot.send_sticker(chat.id, "CAACAgEAAxkBAAICL2GIS1rV-HBllEQYxBcSjh4XnpBJAAIDAQACPF8xRmEkSUQJNOg6IgQ")  # banhammer marie sticker
        bot.sendMessage(
            chat.id,
            f"Usuario Baneado! {mention_html(member.user.id, html.escape(member.user.first_name))} "
            f"podria estar baneado por: {time_val}.",
            parse_mode=ParseMode.HTML,
        )
        return log

    except BadRequest as excp:
        if excp.message == "Mensaje no encontrado":
            # Do not reply
            message.reply_text(
                f"Baneado! Podria estar baneado por: {time_val}.", quote=False
            )
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "Error baneando usuario %s en el chat %s (%s) podria ser por %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("Maldita sea, no puedo prohibir a ese usuario.")

    return log_message


@run_async
@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def punch(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("Dudo que sea un usuario.")
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "User not found":
            raise

        message.reply_text("No puedo encontrar a este usuario")
        return log_message
    if user_id == bot.id:
        message.reply_text("Yeahhh, no voy a hacer eso.")
        return log_message

    if is_user_ban_protected(chat, user_id):
        message.reply_text("Realmente desearía poder sacar a este usuario....")
        return log_message

    res = chat.unban_member(user_id)  # unban on current user = kick
    if res:
        bot.send_sticker(chat.id, "CAACAgEAAxkBAAICL2GIS1rV-HBllEQYxBcSjh4XnpBJAAIDAQACPF8xRmEkSUQJNOg6IgQ" )  # banhammer marie sticker
        bot.sendMessage(
            chat.id,
            f"Eliminado! {mention_html(member.user.id, html.escape(member.user.first_name))}.",
            parse_mode=ParseMode.HTML,
        )
        log = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#KICKED\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>Usuario:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
        )
        if reason:
            log += f"\n<b>Razon:</b> {reason}"

        return log

    else:
        message.reply_text("Maldita sea, no puedo sacar a ese usuario.")

    return log_message


@run_async
@bot_admin
@can_restrict
def punchme(update: Update, context: CallbackContext):
    user_id = update.effective_message.from_user.id
    if is_user_admin(update.effective_chat, user_id):
        update.effective_message.reply_text("Desearía poder ... pero eres un admin.")
        return

    res = update.effective_chat.unban_member(user_id)  # unban on current user = kick
    if res:
        update.effective_message.reply_text("*te saca del grupo*")
    else:
        update.effective_message.reply_text("¿Eh? No puedo :/")


@run_async
@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def unban(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    log_message = ""
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("No creo que sea un usuario")
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "User not found":
            raise
        message.reply_text("No puedo encontrar a este usuario.")
        return log_message
    if user_id == bot.id:
        message.reply_text("¿Cómo me desharía del BAN si no estuviera aquí...?")
        return log_message

    if is_user_in_chat(chat, user_id):
        message.reply_text("¿No está esta persona ya aquí???")
        return log_message

    chat.unban_member(user_id)
    message.reply_text("Sí, este usuario puede unirse.!")

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#UNBANNED\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>Usuario:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
    )
    if reason:
        log += f"\n<b>Reason:</b> {reason}"

    return log


@run_async
@connection_status
@bot_admin
@can_restrict
@gloggable
def selfunban(context: CallbackContext, update: Update) -> str:
    message = update.effective_message
    user = update.effective_user
    bot, args = context.bot, context.args
    if user.id not in DRAGONS or user.id not in TIGERS:
        return

    try:
        chat_id = int(args[0])
    except:
        message.reply_text("Dame un ID de chat válido.")
        return

    chat = bot.getChat(chat_id)

    try:
        member = chat.get_member(user.id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("Parece que no puedo encontrar a este usuario.")
            return
        else:
            raise

    if is_user_in_chat(chat, user.id):
        message.reply_text("¿No estás ya en el chat???")
        return

    chat.unban_member(user.id)
    message.reply_text("Sí, te he quitado el BAN.")

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#UNBANNED\n"
        f"<b>User:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
    )

    return log


__help__ = """
 ❍ /punchme*:* saca al usuario que emitió el comando

*Admins only:*
 ❍ /ban <userhandle>*:* prohíbe a un usuario. (a través del identificador o respuesta).
 ❍ /sban <userhandle>*:* Prohibir silenciosamente a un usuario. Elimina comando, mensaje respondido y no responde. (a través del identificador o respuesta).
 ❍ /tban <userhandle> x(m/h/d)*:* banea a un usuario por tiempo `x`. (a través del identificador o respuesta). `m` =` minutos`, `h` =` horas`, `d` =` días`.
 ❍ /unban <userhandle>*:* desbanea a un usuario. (a través del identificador o respuesta)
 ❍ /punch <userhandle>*:* Saca a un usuario del grupo, (a través del identificador o respuesta)

 *Admins only:*
 ❍ /mute <userhandle>*:* silencia a un usuario. También se puede utilizar como respuesta, silenciando la respuesta al usuario.
 ❍ /tmute <userhandle> x(m/h/d)*:* silencia a un usuario por x veces. (a través del identificador o respuesta). `m` =` minutos`, `h` =` horas`, `d` =` días`.
 ❍ /unmute <userhandle>*:* des-mutea un usuario. También se puede utilizar como respuesta, silenciando la respuesta al usuario.
"""

BAN_HANDLER = CommandHandler(["ban", "sban"], ban)
TEMPBAN_HANDLER = CommandHandler(["tban"], temp_ban)
PUNCH_HANDLER = CommandHandler("punch", punch)
UNBAN_HANDLER = CommandHandler("unban", unban)
ROAR_HANDLER = CommandHandler("roar", selfunban)
PUNCHME_HANDLER = DisableAbleCommandHandler("punchme", punchme, filters=Filters.group)

dispatcher.add_handler(BAN_HANDLER)
dispatcher.add_handler(TEMPBAN_HANDLER)
dispatcher.add_handler(PUNCH_HANDLER)
dispatcher.add_handler(UNBAN_HANDLER)
dispatcher.add_handler(ROAR_HANDLER)
dispatcher.add_handler(PUNCHME_HANDLER)

__mod_name__ = "Ban/Mute"
__handlers__ = [
    BAN_HANDLER,
    TEMPBAN_HANDLER,
    PUNCH_HANDLER,
    UNBAN_HANDLER,
    ROAR_HANDLER,
    PUNCHME_HANDLER,
]
