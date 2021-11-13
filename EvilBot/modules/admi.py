import html

from EvilBot import DRAGONS, dispatcher
from EvilBot.modules.disable import DisableAbleCommandHandler
from EvilBot.modules.helper_funcs.chat_status import bot_admin, can_pin, can_promote, connection_status, user_admin, ADMIN_CACHE
from EvilBot.helper_extra.admin_rights import user_can_pin, user_can_promote, user_can_changeinfo

from EvilBot.modules.helper_funcs.extraction import extract_user, extract_user_and_text
from EvilBot.modules.log_channel import loggable

from telegram import ParseMode, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler, Filters, run_async
from telegram.utils.helpers import mention_html

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
    log_message = ""

    promoter = chat.get_member(user.id)

    if not (promoter.can_promote_members or
            promoter.status == "creator") and not user.id in SUDO_USERS:
        message.reply_text("No tienes los derechos necesarios para hacer eso!")
        return log_message

    user_id = extract_user(message, args)

    if not user_id:
        message.reply_text(
            "No parece que se refiera a un usuario o el ID especificado es incorrecto.."
        )
        return log_message

    try:
        user_member = chat.get_member(user_id)
    except:
        return log_message

    if user_member.status == 'administrator' or user_member.status == 'creator':
        message.reply_text(
            "¿Cómo se supone que debo promover a alguien que ya es administrador?")
        return log_message

    if user_id == bot.id:
        message.reply_text(
            "¡No puedo promoverme! Consiga un administrador para que lo haga por mí.")
        return log_message

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
            can_pin_messages=bot_member.can_pin_messages)
    except BadRequest as err:
        if err.message == "User_not_mutual_contact":
            message.reply_text(
                "No puedo promover a alguien que no está en el grupo..")
            return log_message
        else:
            message.reply_text("Ocurrió un error al promoverlo.")
            return log_message

    bot.sendMessage(
        chat.id,
        f"Sucessfully promoted <b>{user_member.user.first_name or user_id}</b>!",
        parse_mode=ParseMode.HTML)

    log_message += (
        f"<b>{html.escape(chat.title)}:</b>\n"
        "#Promovido\n"
        f"<b>Administrador:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>Usuario:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
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
    log_message = ""

    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
            "No parece que se refiera a un usuario o el ID especificado es incorrecto.."
        )
        return log_message

    try:
        user_member = chat.get_member(user_id)
    except:
        return log_message

    if user_member.status == 'creator':
        message.reply_text(
            "Este men CREÓ el chat, ¿cómo lo rebajaria?")
        return log_message

    if not user_member.status == 'administrator':
        message.reply_text("No puedo rebajar a quien no promoví!")
        return log_message

    if user_id == bot.id:
        message.reply_text(
            "¡No puedo rebajarme! Consiga a un admin para que lo haga por mí.")
        return log_message

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
            can_promote_members=False)

        bot.sendMessage(
            chat.id,
            f"Haz sido rebajado <b>{user_member.user.first_name or user_id}</b>! :)",
            parse_mode=ParseMode.HTML)

        log_message += (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#Rebajado\n"
            f"<b>Administrador:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>Usuario:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
        )

        return log_message
    except BadRequest:
        message.reply_text(
            "No se pudo rebajar. Puede que no sea administrador o que el admin fue designado por otro"
            " usuario, por lo que no puedo actuar sobre ellos!")
        return log_message
    
@run_async
@user_admin
def refresh_admin(update, _):
    try:
        ADMIN_CACHE.pop(update.effective_chat.id)
    except KeyError:
        pass

    update.effective_message.reply_text("¡Se actualizó la lista de administradores!")


# Until the library releases the method
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
            "No parece que se refiera a un usuario o el ID especificado es incorrecto.."
        )
        return

    if user_member.status == 'creator':
        message.reply_text(
            "Este men CREÓ el chat, ¿cómo puedo configurar un título personalizado para él??")
        return

    if not user_member.status == 'administrator':
        message.reply_text(
            "¡No se puede establecer un título para no administradores!\nPromuevalo primero para establecer un título personalizado!"
        )
        return

    if user_id == bot.id:
        message.reply_text(
            "¡No puedo establecer mi propio título! Haz que el que me dio admin lo haga por mí."
        )
        return

    if not title:
        message.reply_text("Establecer un título en blanco no hace nada!")
        return

    if len(title) > 16:
        message.reply_text(
            "La longitud del título es superior a 16 caracteres. \nTruncalo a 16 caracteres."
        )

    try:
        bot.setChatAdministratorCustomTitle(chat.id, user_id, title)
    except BadRequest:
        message.reply_text(
            "No puedo establecer un título personalizado para administradores que no promoví!")
        return

    bot.sendMessage(
        chat.id,
        f"Se estableció correctamente el título para <code>{user_member.user.first_name or user_id}</code> "
        f"a <code>{title[:16]}</code>!",
        parse_mode=ParseMode.HTML)


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

    is_silent = True
    if len(args) >= 1:
        is_silent = not (args[0].lower() == 'notify' or args[0].lower()
                         == 'loud' or args[0].lower() == 'violent')

    if prev_message and is_group:
        try:
            bot.pinChatMessage(
                chat.id,
                prev_message.message_id,
                disable_notification=is_silent)
        except BadRequest as excp:
            if excp.message == "Chat_not_modified":
                pass
            else:
                raise
        log_message = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#Fijado\n"
            f"<b>Administrador:</b> {mention_html(user.id, user.first_name)}")

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

    log_message = (f"<b>{html.escape(chat.title)}:</b>\n"
                   f"#Desfijado\n"
                   f"<b>Administrador:</b> {mention_html(user.id, user.first_name)}")

    return log_message


@run_async
@bot_admin
@user_admin
def invite(update: Update, context: CallbackContext):
    bot = context.bot
    chat = update.effective_chat

    if chat.username:
        update.effective_message.reply_text(f"https://t.me/{chat.username}")
    elif chat.type == chat.SUPERGROUP or chat.type == chat.CHANNEL:
        bot_member = chat.get_member(bot.id)
        if bot_member.can_invite_users:
            invitelink = bot.exportChatInviteLink(chat.id)
            update.effective_message.reply_text(invitelink)
        else:
            update.effective_message.reply_text(
                "No tengo acceso al enlace de invitación, intente cambiar mis permisos!"
            )
    else:
        update.effective_message.reply_text(
            "Solo puedo darte enlaces de invitación para supergrupos y canales, lo siento!"
        )


@run_async
@connection_status
def adminlist(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    args = context.args
    bot = context.bot

    if update.effective_message.chat.type == "private":
        send_message(update.effective_message, "This command only works in Groups.")
        return

    chat = update.effective_chat
    chat_id = update.effective_chat.id
    chat_name = update.effective_message.chat.title

    try:
        msg = update.effective_message.reply_text(
            "Fetching group admins...", parse_mode=ParseMode.HTML
        )
    except BadRequest:
        msg = update.effective_message.reply_text(
            "Fetching group admins...", quote=False, parse_mode=ParseMode.HTML
        )

    administrators = bot.getChatAdministrators(chat_id)
    text = "Admins in <b>{}</b>:".format(html.escape(update.effective_chat.title))

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

def __chat_settings__(chat_id, user_id):
    return "Eres *admin*: `{}`".format(
        dispatcher.bot.get_chat_member(chat_id, user_id).status in (
            "administrator", "creator"))


__help__ = """
• `/adminlist`*:* Lista de administradores en el chat
*Solo administradores:*
 • `/pin`*:* Fija silenciosamente el mensaje al que respondió - agregue` 'loud'` o `' notify'` para dar notificaciones a los usuarios.
 • `/unpin`*:* Quita el mensaje anclado actualmente.
 • `/invitelink`*:* Obtén el link del grupo.
 • `/promote`*:* Promueve el usuario al que respondió.
 • `/demote`*:* Rebaja al usuario al que respondió.
 • `/settitle`*:* Establece un título personalizado para un administrador que promovió el bot.
 • `/reload`*:* Forzar la actualización de la lista de administradores
"""

ADMINLIST_HANDLER = DisableAbleCommandHandler(["staff", "admins"],
                                              adminlist)

PIN_HANDLER = CommandHandler("pin", pin, filters=Filters.group)
UNPIN_HANDLER = CommandHandler("unpin", unpin, filters=Filters.group)

INVITE_HANDLER = DisableAbleCommandHandler(
    "invitelink", invite, filters=Filters.group)

PROMOTE_HANDLER = DisableAbleCommandHandler("promote", promote)
DEMOTE_HANDLER = DisableAbleCommandHandler("demote", demote)

SET_TITLE_HANDLER = CommandHandler("settitle", set_title)

ADMIN_REFRESH_HANDLER = CommandHandler(
    "reload", refresh_admin, filters=Filters.group
)

dispatcher.add_handler(ADMINLIST_HANDLER)
dispatcher.add_handler(PIN_HANDLER)
dispatcher.add_handler(UNPIN_HANDLER)
dispatcher.add_handler(INVITE_HANDLER)
dispatcher.add_handler(PROMOTE_HANDLER)
dispatcher.add_handler(DEMOTE_HANDLER)
dispatcher.add_handler(SET_TITLE_HANDLER)
dispatcher.add_handler(ADMIN_REFRESH_HANDLER)

__mod_name__ = "Admin"
__command_list__ = ["staff", "admins", "invitelink", "promote", "demote", "reload"]
__handlers__ = [
    ADMINLIST_HANDLER, PIN_HANDLER, UNPIN_HANDLER, INVITE_HANDLER,
    PROMOTE_HANDLER, DEMOTE_HANDLER, SET_TITLE_HANDLER, ADMIN_REFRESH_HANDLER
]
