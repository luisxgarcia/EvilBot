import html

from telegram import ParseMode, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler, Filters, run_async
from telegram.utils.helpers import mention_html

from EvilBot import DRAGONS, dispatcher
from EvilBot.modules.disable import DisableAbleCommandHandler
from EvilBot.modules.helper_funcs.chat_status import (
    bot_admin,
    can_pin,
    can_promote,
    connection_status,
    user_admin,
    ADMIN_CACHE,
)
from EvilBot.helper_extra.admin_rights import (
    user_can_pin,
    user_can_promote,
    user_can_changeinfo,
)

from EvilBot.modules.helper_funcs.extraction import (
    extract_user,
    extract_user_and_text,
)
from EvilBot.modules.log_channel import loggable
from EvilBot.modules.helper_funcs.alternate import send_message
from EvilBot.modules.helper_funcs.alternate import typing_action


@run_async
@connection_status
@bot_admin
@can_promote
@user_admin
@loggable
def promote(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    promoter = chat.get_member(user.id)

    if (
        not (promoter.can_promote_members or promoter.status == "creator")
        and user.id not in DRAGONS
    ):
        message.reply_text("¡No tienes los permisos necesarios para hacer eso!")
        return

    user_id = extract_user(message, args)

    if not user_id:
        message.reply_text(
            "No parece que se esté refiriendo a un usuario o el ID especificado es incorrecto ..."
        )
        return

    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if user_member.status == "administrator" or user_member.status == "creator":
        message.reply_text("¿Cómo se supone que debo promover a alguien que ya es administrador?")
        return

    if user_id == bot.id:
        message.reply_text("¡No puedo promoverme! Consiga un administrador para que lo haga por mí.")
        return

    # set same perms as bot - bot can't assign higher perms than itself!
    bot_member = chat.get_member(bot.id)

    try:
        bot.promoteChatMember(
            chat.id,
            user_id,
            can_change_info=bot_member.can_change_info,
            can_post_messages=bot_member.can_post_messages,
            can_edit_messages=bot_member.can_edit_messages,
            can_delete_messages=bot_member.can_delete_messages,
            can_invite_users=bot_member.can_invite_users,
            # can_promote_members=bot_member.can_promote_members,
            can_restrict_members=bot_member.can_restrict_members,
            can_pin_messages=bot_member.can_pin_messages,
        )
    except BadRequest as err:
        if err.message == "User_not_mutual_contact":
            message.reply_text("No puedo promover a alguien que no esté en el grupo.")
        else:
            message.reply_text("Se produjo un error durante la promoción")
        return

    bot.sendMessage(
        chat.id,
        f"Promovido con éxito <b>{user_member.user.first_name or user_id}</b>!",
        parse_mode=ParseMode.HTML,
    )

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"USER PROMOVIDO CON EXITO\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
    )

    return log_message


@run_async
@connection_status
@bot_admin
@can_promote
@user_admin
@loggable
def demote(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    message = update.effective_message
    user = update.effective_user

    user_id = extract_user(message, args)

    if user_can_promote(chat, user, context.bot.id) is False:
        message.reply_text("¡No tienes suficientes derechos para degradar a alguien!")
        return ""

    if not user_id:
        message.reply_text(
            "No parece que se esté refiriendo a un usuario o el ID especificado es incorrecto ..."
        )
        return

    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if user_member.status == "creator":
        message.reply_text("Esta persona CREÓ el chat, ¿cómo la removeria?")
        return

    if not user_member.status == "administrator":
        message.reply_text("¡No se puede remover lo que no se promovió!")
        return

    if user_id == bot.id:
        message.reply_text("¡No puedo removerme! Consiga un administrador para que lo haga por mí.")
        return

    try:
        bot.promoteChatMember(
            chat.id,
            user_id,
            can_change_info=False,
            can_post_messages=False,
            can_edit_messages=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False,
        )

        bot.sendMessage(
            chat.id,
            f"Removido con exito <b>{user_member.user.first_name or user_id}</b>!",
            parse_mode=ParseMode.HTML,
        )

        log_message = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"USUARIO REMOVIDO CON EXITO\n"
            f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>User:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
        )

        return log_message
    except BadRequest:
        message.reply_text(
            "No se pudo remover. Es posible que no sea administrador o que el estado de administrador fue designado por otro"
            " user, ¡así que no puedo actuar sobre ellos!"
        )
        return


@run_async
@user_admin
def refresh_admin(update, _):
    try:
        ADMIN_CACHE.pop(update.effective_chat.id)
    except KeyError:
        pass

    update.effective_message.reply_text("¡Se actualizó la lista de administradores!")


@run_async
@connection_status
@bot_admin
@can_promote
@user_admin
def set_title(update: Update, context: CallbackContext):
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    message = update.effective_message

    user_id, title = extract_user_and_text(message, args)
    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if not user_id:
        message.reply_text(
            "No parece que se esté refiriendo a un usuario o el ID especificado es incorrecto ..."
        )
        return

    if user_member.status == "creator":
        message.reply_text(
            "Esta persona CREÓ el chat, ¿cómo puedo configurar un título personalizado para él?"
        )
        return

    if user_member.status != "administrator":
        message.reply_text(
            "¡No se puede establecer un título para los que no son administradores!\n¡Promuévelos primero para establecer un título personalizado!"
        )
        return

    if user_id == bot.id:
        message.reply_text(
            "¡No puedo establecer mi propio título! Haz que el que me hizo administrador lo haga por mí."
        )
        return

    if not title:
        message.reply_text("¡Establecer un título en blanco no hace nada!")
        return

    if len(title) > 16:
        message.reply_text(
            "La longitud del título es superior a 16 caracteres.\nTruncarlo a 16 caracteres."
        )

    try:
        bot.setChatAdministratorCustomTitle(chat.id, user_id, title)
    except BadRequest:
        message.reply_text("¡No puedo establecer un título personalizado para administradores que no promovi!")
        return

    bot.sendMessage(
        chat.id,
        f"Estableci correctamente el título: <code>{user_member.user.first_name or user_id}</code> "
        f"para <code>{html.escape(title[:16])}</code>!",
        parse_mode=ParseMode.HTML,
    )


@run_async
@bot_admin
@user_admin
@typing_action
def setchatpic(update, context):
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user

    if user_can_changeinfo(chat, user, context.bot.id) is False:
        msg.reply_text("¡Te falta el derecho a cambiar la información del grupo!")
        return

    if msg.reply_to_message:
        if msg.reply_to_message.photo:
            pic_id = msg.reply_to_message.photo[-1].file_id
        elif msg.reply_to_message.document:
            pic_id = msg.reply_to_message.document.file_id
        else:
            msg.reply_text("¡Solo puedes configurar alguna foto como imagen de chat!")
            return
        dlmsg = msg.reply_text("Just a sec...")
        tpic = context.bot.get_file(pic_id)
        tpic.download("gpic.png")
        try:
            with open("gpic.png", "rb") as chatp:
                context.bot.set_chat_photo(int(chat.id), photo=chatp)
                msg.reply_text("¡Establece con éxito una nueva imagen de chat!")
        except BadRequest as excp:
            msg.reply_text(f"Error! {excp.message}")
        finally:
            dlmsg.delete()
            if os.path.isfile("gpic.png"):
                os.remove("gpic.png")
    else:
        msg.reply_text("¡Responde alguna foto o archivo para establecer una nueva foto de chat!")


@run_async
@bot_admin
@user_admin
@typing_action
def rmchatpic(update, context):
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user

    if user_can_changeinfo(chat, user, context.bot.id) is False:
        msg.reply_text("No tienes suficientes derechos para eliminar la foto de grupo")
        return
    try:
        context.bot.delete_chat_photo(int(chat.id))
        msg.reply_text("¡La foto de perfil del chat se eliminó correctamente!")
    except BadRequest as excp:
        msg.reply_text(f"Error! {excp.message}.")
        return


@run_async
@bot_admin
@user_admin
@typing_action
def setchat_title(update, context):
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user
    args = context.args

    if user_can_changeinfo(chat, user, context.bot.id) is False:
        msg.reply_text("¡No tienes suficientes derechos para cambiar la información del chat!")
        return

    title = " ".join(args)
    if not title:
        msg.reply_text("¡Ingrese un poco de texto para establecer un nuevo título en su chat!")
        return

    try:
        context.bot.set_chat_title(int(chat.id), str(title))
        msg.reply_text(
            f"Establecido con éxito <b>{title}</b> como nuevo título de chat!",
            parse_mode=ParseMode.HTML,
        )
    except BadRequest as excp:
        msg.reply_text(f"Error! {excp.message}.")
        return


@run_async
@bot_admin
@user_admin
@typing_action
def set_sticker(update, context):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if user_can_changeinfo(chat, user, context.bot.id) is False:
        return msg.reply_text("¡Te faltan derechos para cambiar la información del chat!")

    if msg.reply_to_message:
        if not msg.reply_to_message.sticker:
            return msg.reply_text(
                "¡Tienes que responder a alguna pegatina para configurar el conjunto de pegatinas de chat!"
            )
        stkr = msg.reply_to_message.sticker.set_name
        try:
            context.bot.set_chat_sticker_set(chat.id, stkr)
            msg.reply_text(
                f"Coloqué con éxito nuevas pegatinas de grupo en {chat.title}!")
        except BadRequest as excp:
            if excp.message == "Participants_too_few":
                return msg.reply_text(
                    "Lo sentimos, debido a las restricciones de telegram, el chat debe tener un mínimo de 100 miembros antes de que puedan tener pegatinas grupales."
                )
            msg.reply_text(f"Error! {excp.message}.")
    else:
        msg.reply_text(
            "¡Tienes que responder a alguna pegatina para configurar el conjunto de pegatinas de chat!")


@run_async
@bot_admin
@user_admin
@typing_action
def set_desc(update, context):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if user_can_changeinfo(chat, user, context.bot.id) is False:
        return msg.reply_text("¡Te faltan derechos para cambiar la información del chat!")

    tesc = msg.text.split(None, 1)
    if len(tesc) >= 2:
        desc = tesc[1]
    else:
        return msg.reply_text("¡Establecer una descripción vacía no hará nada!")
    try:
        if len(desc) > 255:
            return msg.reply_text(
                "La descripción debe tener menos de 255 caracteres.")
        context.bot.set_chat_description(chat.id, desc)
        msg.reply_text(
            f"Descripción del chat actualizada con éxito en {chat.title}!")
    except BadRequest as excp:
        msg.reply_text(f"Error! {excp.message}.")


def __chat_settings__(chat_id, user_id):
    return "Tu estas *admin*: `{}`".format(
        dispatcher.bot.get_chat_member(chat_id, user_id).status
        in ("administrator", "creator")
    )


@run_async
@bot_admin
@can_pin
@user_admin
@loggable
def pin(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    user = update.effective_user
    chat = update.effective_chat

    is_group = chat.type != "private" and chat.type != "channel"
    prev_message = update.effective_message.reply_to_message

    if user_can_pin(chat, user, context.bot.id) is False:
        message.reply_text("¡Te faltan derechos para fijar un mensaje!")
        return ""

    is_silent = True
    if len(args) >= 1:
        is_silent = not (
            args[0].lower() == "notify"
            or args[0].lower() == "loud"
            or args[0].lower() == "violent"
        )

    if prev_message and is_group:
        try:
            bot.pinChatMessage(
                chat.id, prev_message.message_id, disable_notification=is_silent
            )
        except BadRequest as excp:
            if excp.message == "Chat_not_modified":
                pass
            else:
                raise
        log_message = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"MENSAJE FIJADO EXITOSAMENTE\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}"
        )

        return log_message


@run_async
@bot_admin
@can_pin
@user_admin
@loggable
def unpin(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    chat = update.effective_chat
    user = update.effective_user

    try:
        bot.unpinChatMessage(chat.id)
    except BadRequest as excp:
        if excp.message == "Chat_not_modified":
            pass
        else:
            raise

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
            f"MENSAJE DESFIJADO CON ÉXITO\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}"
    )

    return log_message


@run_async
@bot_admin
@user_admin
@connection_status
def invite(update: Update, context: CallbackContext):
    bot = context.bot
    chat = update.effective_chat

    if chat.username:
        update.effective_message.reply_text(f"https://t.me/{chat.username}")
    elif chat.type in [chat.SUPERGROUP, chat.CHANNEL]:
        bot_member = chat.get_member(bot.id)
        if bot_member.can_invite_users:
            invitelink = bot.exportChatInviteLink(chat.id)
            update.effective_message.reply_text(invitelink)
        else:
            update.effective_message.reply_text(
                "No tengo acceso al enlace de invitación, ¡intente cambiar mis permisos!"
            )
    else:
        update.effective_message.reply_text(
            "Solo puedo darte enlaces de invitación para supergrupos y canales, ¡lo siento!"
        )


@run_async
@connection_status
def adminlist(update, context):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    args = context.args
    bot = context.bot

    if update.effective_message.chat.type == "private":
        send_message(update.effective_message, "Este comando solo funciona en grupos.")
        return

    chat = update.effective_chat
    chat_id = update.effective_chat.id
    chat_name = update.effective_message.chat.title

    try:
        msg = update.effective_message.reply_text(
            "Obteniendo administradores de grupo ...", parse_mode=ParseMode.HTML
        )
    except BadRequest:
        msg = update.effective_message.reply_text(
            "Obteniendo administradores de grupo ...", quote=False, parse_mode=ParseMode.HTML
        )

    administrators = bot.getChatAdministrators(chat_id)
    text = "Administradores en <b>{}</b>:".format(html.escape(update.effective_chat.title))

    bot_admin_list = []

    for admin in administrators:
        user = admin.user
        status = admin.status
        custom_title = admin.custom_title

        if user.first_name == "":
            name = "☠ Deleted Account"
        else:
            name = "{}".format(
                mention_html(
                    user.id, html.escape(user.first_name + " " + (user.last_name or ""))
                )
            )

        if user.is_bot:
            bot_admin_list.append(name)
            administrators.remove(admin)
            continue

        # if user.username:
        #    name = escape_markdown("@" + user.username)
        if status == "creator":
            text += "\n 👑 Creator:"
            text += "\n<code> • </code>{}\n".format(name)

            if custom_title:
                text += f"<code> ┗━ {html.escape(custom_title)}</code>\n"

    text += "\n🔱 Admins:"

    custom_admin_list = {}
    normal_admin_list = []

    for admin in administrators:
        user = admin.user
        status = admin.status
        custom_title = admin.custom_title

        if user.first_name == "":
            name = "☠ Deleted Account"
        else:
            name = "{}".format(
                mention_html(
                    user.id, html.escape(user.first_name + " " + (user.last_name or ""))
                )
            )
        # if user.username:
        #    name = escape_markdown("@" + user.username)
        if status == "administrator":
            if custom_title:
                try:
                    custom_admin_list[custom_title].append(name)
                except KeyError:
                    custom_admin_list.update({custom_title: [name]})
            else:
                normal_admin_list.append(name)

    for admin in normal_admin_list:
        text += "\n<code> • </code>{}".format(admin)

    for admin_group in custom_admin_list.copy():
        if len(custom_admin_list[admin_group]) == 1:
            text += "\n<code> • </code>{} | <code>{}</code>".format(
                custom_admin_list[admin_group][0], html.escape(admin_group)
            )
            custom_admin_list.pop(admin_group)

    text += "\n"
    for admin_group, value in custom_admin_list.items():
        text += "\n🚨 <code>{}</code>".format(admin_group)
        for admin in value:
            text += "\n<code> • </code>{}".format(admin)
        text += "\n"

    text += "\n🤖 Bots:"
    for each_bot in bot_admin_list:
        text += "\n<code> • </code>{}".format(each_bot)

    try:
        msg.edit_text(text, parse_mode=ParseMode.HTML)
    except BadRequest:  # if original message is deleted
        return


__help__ = """
 ❍ /admins*:* lista de administradores en el chat

*Solo Administradores:*
 ❍ /pin*:* fija silenciosamente el mensaje al que respondió: agregue ``loud'' o ``notify'' para dar notificaciones a los usuarios
 ❍ /unpin*:* elimina el mensaje anclado actualmente 
 ❍ /invitelink*:* obtiene un enlace de invitación
 ❍ /promote*:* promueve al usuario
 ❍ /demote*:* remueve al usuario
 ❍ /title <titulo>*:* establece un título personalizado para un administrador promovido por el bot
 ❍ /setgtitle <nuevo_tirulo>*:* Establece un nuevo título de chat en su grupo.
 ❍ /setgpic*:* ¡Como respuesta a un archivo o foto para configurar una foto de perfil de grupo!
 ❍ /delgpic*:* Igual que el anterior pero para eliminar la foto del perfil del grupo.
 ❍ /setsticker*:* ¡Como respuesta a alguna pegatina para configurarla como conjunto de pegatinas de grupo!
 ❍ /setdescription <descripcion>*:* Establebe una nueva descripcion del chat.
 ❍ /admincache*:* Forzar la actualización de la lista de administradores
 ❍ /antispam <on/off/yes/no>*:* Cambiará nuestra tecnología antispam o devolverá su configuración actual.
 ❍ /del*:* Elimina el mensaje al que respondiste
 ❍ /purge*:* Elimina todos los mensajes entre este y el mensaje respondido.
 ❍ /purge <integer X>*:* Elimina el mensaje respondido y los X mensajes que lo siguen si respondieron a un mensaje.
*Zombies:*
 ❍ /zombies*:* Escanear cuentas eliminadas
 ❍ /zombies clean*:* Limpia cuentas eliminadas

*Note:* Los chats en modo nocturno se cierran automáticamente a las 12 am (IST)
y Se abre automáticamente a las 6 am (IST) para prevenir el spam nocturno.

⚠️ `Leer desde arriba`
"""

ADMINLIST_HANDLER = DisableAbleCommandHandler("admins", adminlist)

PIN_HANDLER = CommandHandler("pin", pin, filters=Filters.group)
UNPIN_HANDLER = CommandHandler("unpin", unpin, filters=Filters.group)

INVITE_HANDLER = DisableAbleCommandHandler("invitelink", invite)

PROMOTE_HANDLER = DisableAbleCommandHandler("promote", promote)
DEMOTE_HANDLER = DisableAbleCommandHandler("demote", demote)

SET_TITLE_HANDLER = CommandHandler("title", set_title)
ADMIN_REFRESH_HANDLER = CommandHandler(
    "admincache", refresh_admin, filters=Filters.group
)

CHAT_PIC_HANDLER = CommandHandler("setgpic", setchatpic, filters=Filters.group)
DEL_CHAT_PIC_HANDLER = CommandHandler(
    "delgpic", rmchatpic, filters=Filters.group)
SETCHAT_TITLE_HANDLER = CommandHandler(
    "setgtitle", setchat_title, filters=Filters.group
)
SETSTICKET_HANDLER = CommandHandler(
    "setsticker", set_sticker, filters=Filters.group)
SETDESC_HANDLER = CommandHandler(
    "setdescription",
    set_desc,
    filters=Filters.group)

dispatcher.add_handler(ADMINLIST_HANDLER)
dispatcher.add_handler(PIN_HANDLER)
dispatcher.add_handler(UNPIN_HANDLER)
dispatcher.add_handler(INVITE_HANDLER)
dispatcher.add_handler(PROMOTE_HANDLER)
dispatcher.add_handler(DEMOTE_HANDLER)
dispatcher.add_handler(SET_TITLE_HANDLER)
dispatcher.add_handler(ADMIN_REFRESH_HANDLER)
dispatcher.add_handler(CHAT_PIC_HANDLER)
dispatcher.add_handler(DEL_CHAT_PIC_HANDLER)
dispatcher.add_handler(SETCHAT_TITLE_HANDLER)
dispatcher.add_handler(SETSTICKET_HANDLER)
dispatcher.add_handler(SETDESC_HANDLER)

__mod_name__ = "Admin"
__command_list__ = [
    "adminlist",
    "admins",
    "invitelink",
    "promote",
    "demote",
    "admincache",
]
__handlers__ = [
    ADMINLIST_HANDLER,
    PIN_HANDLER,
    UNPIN_HANDLER,
    INVITE_HANDLER,
    PROMOTE_HANDLER,
    DEMOTE_HANDLER,
    SET_TITLE_HANDLER,
    ADMIN_REFRESH_HANDLER,
]
