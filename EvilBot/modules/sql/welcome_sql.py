import random
import threading
from typing import Union

from EvilBot.modules.helper_funcs.msg_types import Types
from EvilBot.modules.sql import BASE, SESSION
from sqlalchemy import BigInteger, Boolean, Column, Integer, String, UnicodeText

DEFAULT_WELCOME = "Hey {first}, how are you?"
DEFAULT_GOODBYE = "Nice knowing ya!"

DEFAULT_WELCOME_MESSAGES = [
    "¡{first} ya está aquí!", # mensajes de bienvenida de Discord copiados
    "Jugador listo {first}",
    "Genos, {first} está aquí",
    "Apareció un {first} salvaje",
    "¡{first} entró como un león!",
    "{first} se ha unido al grupo",
    "{first} acaba de unirse. ¿Puedo curarme?",
    "{first} acaba de unirse al chat - ¡asdgfhak!",
    "{first} acaba de unirse. ¡Todos, parezcan ocupados!",
    "Bienvenido, {first}. Quédate un rato y escucha",
    "Bienvenido, {first}. Te estábamos esperando (͡ ° ͜ʖ ͡ °)",
    "Bienvenido, {first}. Esperamos que hayas traído pizza",
    "Bienvenido, {first}. Deja tus armas junto a la puerta",
    "Swoooosh. {first} acaba de aterrizar",
    "Prepárense. {first} acaba de unirse al chat",
    "{first} acaba de unirse. Esconde tus plátanos",
    "{first} acaba de entrar en el chat",
    "Se ha generado una {first} en el chat",
    "¡Big {first} apareció!",
    "¿Dónde está {first}? ¡En el chat!",
    "{first} saltó al chat. ¡¡Canguro!!",
    "{first} acaba de aparecer. Me quitare la ropa",
    "¡Se acerca un retador! ¡{first} ha aparecido!",
    "¡Es un pájaro! ¡Es un avión! No importa, es solo {first}",
    "¡Es {first}! ¡Alabado sea el sol! \ O /",
    "Nunca me rendiré {first}. Nunca decepcionaré a {first}.",
    "¡Ja! ¡{first} se ha unido! ¡Activaste mi modo Bad Blood!",
    "¡Oye! ¡Escucha! ¡{first} se ha unido!",
    "Te estábamos esperando {first}",
    "¡{first} se ha unido al chat! ¡Es muy eficaz!",
    "¡Salud, amor! ¡{first} está aquí!",
    "{first} está aquí, como predijo la profecía.",
    "{first} ha llegado. Se acabó la fiesta",
    "{first} está aquí para patear traseros y masticar chicle. Y {first} no tiene chicle",
    "Hola. ¿Es {first} lo que estás buscando?",
    "{first} se ha unido. ¡Quédate un rato y escucha!",
    "Las rosas son rojas, las violetas son azules, {first} se unió a este chat conmigo",
    "¡Bienvenido {first}, evita los puñetazos si puedes!",
    "¡Es un pájaro! ¡Es un avión! - ¡No, es {primero}!",
    "{first} ¡Únete!"
    "Ok.", # Finalizan los mensajes de bienvenida de Discord.
    "Hola, {primero}. No te quedes al acecho, solo los villanos hacen eso",
    "{first} se ha unido al autobús de batalla",
    "¡Entra un nuevo Challenger!", # Tekken
    "¡OK!",
    "¡{first} acaba de entrar en el chat!",
    "¡Algo acaba de caer del cielo! - oh, es {first}.",
    "{first} ¡Recién teletransportado al chat!",
    "¡Hola, {first}, muéstrame tu licencia de cazador!", # Hunter Hunter
    "¡Bienvenido {first}, irse no es una opción!",
    "¡Ejecuta el bosque! ... quiero decir ... {first}.",
    "¡{first} haz 100 flexiones, 100 abdominales, 100 sentadillas y 10 km corriendo TODOS LOS DÍAS!", # One Punch ma
    "¿Eh?\n¿Alguien con un nivel de desastre acaba de unirse?\nOh, espera, es solo {first}", # One Punch ma
    "Oye, {first}, vacía tus bolsillos",
    "¡Oye, {first} !, ¿eres fuerte?",
    "¡Llamen a los Vengadores! - {first} acaba de unirse al chat",
    "{first} se ha unido. Debes construir torres adicionales.",
    "¡Ven por la carrera de caracoles, quédate por las chimichangas!",
    "¿Quién necesita Google? Eres todo lo que estábamos buscando",
    "Este lugar debe tener WiFi gratis, porque siento una conexión",
    "Habla amigo y entra",
    "Bienvenido, eres?",
    "Bienvenido {first}, tu princesa está en otro castillo.",
    "Hola {first}, bienvenido al lado oscuro",
    "Hola {first}, ten cuidado con las personas con niveles de desastre",
    "Hola, {first}\nEste no es un lugar extraño, esta es mi casa, son las personas las que son extrañas",
    "Oh, hey {first} ¿cuál es la contraseña?",
    "Oye, {first}, sé lo que haremos hoy",
    "{first} acaba de unirse, esté alerta de que podrían ser un espía",
    "{first} se unió al grupo, leído por Mark Zuckerberg, CIA y otras 35 personas",
    "Bienvenido {first}, cuidado con los monos que caen",
    "Todos dejen lo que están haciendo. Ahora estamos en presencia de {first}",
    "Oye {first}, ¿quieres saber cómo conseguí merch gratis?",
    "Bienvenido {first}, suelta tus armas y procede al escáner espía",
    "Mantente a salvo {first}, mantén una distancia social de 3 metros entre tus mensajes", # Corona memes lmao
    "Oye, {first}, ¿sabes que una vez golpeé un meteorito con un solo golpe?",
    "Estás aquí ahora {first}, la resistencia es inútil",
    "{first} acaba de llegar, la fuerza es fuerte con este",
    "{first} acaba de unirse por orden del presidente",
    "Hola, {first}, ¿el vaso está medio lleno o medio vacío?",
    "Bienvenido {first}, si eres un agente secreto, presiona 1; de lo contrario, inicia una conversación",
    "¡La costa está despejada! Pueden salir chicos, es solo {first}",
    "Bienvenido {first}, no le prestes atención a ese tipo que está al acecho",
    "Bienvenido {first}, que la fuerza te acompañe",
    "Que {first} esté contigo",
    "{first} acaba de unirse. Oye, ¿dónde está Perry?",
    "{first} acaba de unirse. Ah, ahí estás, Perry",
    "Señoras y señores, les doy ... {first}.",
    "He aquí mi nuevo plan maligno, el {first}-inador.",
    "Ah, {first} el ornitorrinco, llegas justo a tiempo ... para que te atrapen",
    "Ven. No quiero destruir este lugar", # hunter x hunter
    "Oye, {first} ... ¿alguna vez has escuchado estas palabras?", # BNHA
    "¿No puede una chica dormir un poco por aquí?", # Kamina Falls - Gurren Lagann
    "Es hora de que alguien te ponga en tu lugar, {first}", # Hellsing
    "Prepárate para los problemas ... y haz que se dupliquen", # Pokémon
    "Adivina quién sobrevivió a su tiempo en el infierno, {first}", # jojo
    "¿Cuántas hogazas de pan has comido en tu vida?", # Jojo
    "¿Qué dijiste? Dependiendo de tu respuesta, ¡puede que tenga que patearte el trasero!", # Jojo
    "¡{first} acaba de entrar en el grupo!",
    "{first}, ¿sabes que a los dioses de la muerte les encantan las manzanas?", # Death Note owo
    "¡{first}! ¡Yo, Taylor Swift! Te declaro el más fuerte",
    "{first}, esta vez te prestaré mi poder", # Kyuubi a Naruto
    "{first}, ¡bienvenido a la aldea oculta de las hojas!", 
    "En la jungla, debes esperar... hasta que los dados marquen cinco u ocho", # cosas de Jumanji
    "Dr. {first} famoso arqueólogo y explorador internacional, \n¡Bienvenido a Jumanji!\nEl destino de Jumanji depende de ti ahora",
    "{first}, esta no será una misión fácil: los monos ralentizan la expedición", # Fin de las cosas de Jumanji
    "Recuerda, recuerda, el cinco de noviembre, la traición y el complot de la pólvora. No conozco ninguna razón por la que la Traición de la pólvora deba olvidarse jamás", #V de Vendetta
    "Detrás de {first} hay algo más que carne. Debajo de este usuario hay una idea ... y las ideas son a prueba de balas", #V de Vendetta
    "¡Quítame las apestosas patas de encima, maldito simio sucio!", #Planeta de los simios
    "Ven conmigo si quieres vivir",
]
DEFAULT_GOODBYE_MESSAGES = [
    "{first} se perderá.",
    "{first} acaba de desconectarse",
    "{first} ha abandonado el vestíbulo",
    "{first} ha dejado el culto.",
    "{first} ha abandonado el juego",
    "{first} ha huido del área",
    "{first} está fuera de ejecución",
    "¡Encantado de conocerte, {first}!",
    "Fue un momento divertido {first}",
    "Esperamos volver a verte pronto, {first}",
    "No quiero decir adiós, {first}",
    "¡Adiós {first}! Adivina quién te va a extrañar: ')",
    "¡Adiós {first}! Va a ser muy solitario sin ti.",
    "¡Por favor, no me dejes solo en este lugar, {first}!",
    "¡Buena suerte encontrando mejores carteles de mierda que nosotros, {first}!",
    "Sabes que te vamos a extrañar {first}. ¿Verdad? ¿Verdad? ¿Verdad?",
    "¡Felicitaciones, {first}! Estás oficialmente libre de este lío",
    "{first}. Eras un oponente que valía la pena pelear.",
    "Tráele la foto",
    "¡Salio fuera!",
    "Pregunta de nuevo más tarde",
    "Piensa por ti mismo",
    "Cuestiona a la autoridad",
    "Estás adorando a un dios del sol",
    "No salgas de casa hoy",
    "¡Darse por vencido!",
    "Casarse y reproducirse",
    "Permanecer dormido",
    "Despierta",
    "Mira a la luna",
    "Steven vive",
    "Conoce a extraños sin prejuicios",
    "Un ahorcado no te traerá suerte hoy",
    "¿Qué quieres hacer hoy?",
    "Estás oscuro por dentro",
    "¿Has visto la salida?",
    "Consíguete una mascota bebé que te animará",
    "Tu princesa está en otro castillo",
    "Lo estás jugando mal dame el mando",
    "Confía en la gente buena",
    "Vivir para morir.",
    "¡Cuando la vida te da limones vuelve a enrollar!",
    "Bueno, eso fue inútil",
    "¡Me quedé dormido!",
    "Que tus problemas sean muchos",
    "Tu antigua vida está en ruinas",
    "Siempre mira el lado positivo",
    "Es peligroso ir solo",
    "Nunca serás perdonado",
    "No tienes a nadie a quien culpar más que a ti mismo",
    "Solo un pecador",
    "Usa las bombas con prudencia",
    "Nadie sabe los problemas que has visto",
    "Te ves gordo, deberías hacer más ejercicio",
    "Sigue a la cebra",
    "¿Por qué tan azul?",
    "El diablo disfrazado",
    "Salio fuera",
    "Siempre tu cabeza en las nubes",
]



class Welcome(BASE):
    __tablename__ = "welcome_pref"
    chat_id = Column(String(14), primary_key=True)
    should_welcome = Column(Boolean, default=True)
    should_goodbye = Column(Boolean, default=True)
    custom_content = Column(UnicodeText, default=None)

    custom_welcome = Column(
        UnicodeText, default=random.choice(DEFAULT_WELCOME_MESSAGES)
    )
    welcome_type = Column(Integer, default=Types.TEXT.value)

    custom_leave = Column(UnicodeText, default=random.choice(DEFAULT_GOODBYE_MESSAGES))
    leave_type = Column(Integer, default=Types.TEXT.value)

    clean_welcome = Column(BigInteger)

    def __init__(self, chat_id, should_welcome=True, should_goodbye=True):
        self.chat_id = chat_id
        self.should_welcome = should_welcome
        self.should_goodbye = should_goodbye

    def __repr__(self):
        return "<Chat {} should Welcome new users: {}>".format(
            self.chat_id, self.should_welcome
        )


class WelcomeButtons(BASE):
    __tablename__ = "welcome_urls"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(String(14), primary_key=True)
    name = Column(UnicodeText, nullable=False)
    url = Column(UnicodeText, nullable=False)
    same_line = Column(Boolean, default=False)

    def __init__(self, chat_id, name, url, same_line=False):
        self.chat_id = str(chat_id)
        self.name = name
        self.url = url
        self.same_line = same_line


class GoodbyeButtons(BASE):
    __tablename__ = "leave_urls"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(String(14), primary_key=True)
    name = Column(UnicodeText, nullable=False)
    url = Column(UnicodeText, nullable=False)
    same_line = Column(Boolean, default=False)

    def __init__(self, chat_id, name, url, same_line=False):
        self.chat_id = str(chat_id)
        self.name = name
        self.url = url
        self.same_line = same_line


class WelcomeMute(BASE):
    __tablename__ = "welcome_mutes"
    chat_id = Column(String(14), primary_key=True)
    welcomemutes = Column(UnicodeText, default=False)

    def __init__(self, chat_id, welcomemutes):
        self.chat_id = str(chat_id)  # ensure string
        self.welcomemutes = welcomemutes


class WelcomeMuteUsers(BASE):
    __tablename__ = "human_checks"
    user_id = Column(Integer, primary_key=True)
    chat_id = Column(String(14), primary_key=True)
    human_check = Column(Boolean)

    def __init__(self, user_id, chat_id, human_check):
        self.user_id = user_id  # ensure string
        self.chat_id = str(chat_id)
        self.human_check = human_check


class CleanServiceSetting(BASE):
    __tablename__ = "clean_service"
    chat_id = Column(String(14), primary_key=True)
    clean_service = Column(Boolean, default=True)

    def __init__(self, chat_id):
        self.chat_id = str(chat_id)

    def __repr__(self):
        return "<Chat used clean service ({})>".format(self.chat_id)


Welcome.__table__.create(checkfirst=True)
WelcomeButtons.__table__.create(checkfirst=True)
GoodbyeButtons.__table__.create(checkfirst=True)
WelcomeMute.__table__.create(checkfirst=True)
WelcomeMuteUsers.__table__.create(checkfirst=True)
CleanServiceSetting.__table__.create(checkfirst=True)

INSERTION_LOCK = threading.RLock()
WELC_BTN_LOCK = threading.RLock()
LEAVE_BTN_LOCK = threading.RLock()
WM_LOCK = threading.RLock()
CS_LOCK = threading.RLock()


def welcome_mutes(chat_id):
    try:
        welcomemutes = SESSION.query(WelcomeMute).get(str(chat_id))
        if welcomemutes:
            return welcomemutes.welcomemutes
        return False
    finally:
        SESSION.close()


def set_welcome_mutes(chat_id, welcomemutes):
    with WM_LOCK:
        prev = SESSION.query(WelcomeMute).get((str(chat_id)))
        if prev:
            SESSION.delete(prev)
        welcome_m = WelcomeMute(str(chat_id), welcomemutes)
        SESSION.add(welcome_m)
        SESSION.commit()


def set_human_checks(user_id, chat_id):
    with INSERTION_LOCK:
        human_check = SESSION.query(WelcomeMuteUsers).get((user_id, str(chat_id)))
        if not human_check:
            human_check = WelcomeMuteUsers(user_id, str(chat_id), True)

        else:
            human_check.human_check = True

        SESSION.add(human_check)
        SESSION.commit()

        return human_check


def get_human_checks(user_id, chat_id):
    try:
        human_check = SESSION.query(WelcomeMuteUsers).get((user_id, str(chat_id)))
        if not human_check:
            return None
        human_check = human_check.human_check
        return human_check
    finally:
        SESSION.close()


def get_welc_mutes_pref(chat_id):
    welcomemutes = SESSION.query(WelcomeMute).get(str(chat_id))
    SESSION.close()

    if welcomemutes:
        return welcomemutes.welcomemutes

    return False


def get_welc_pref(chat_id):
    welc = SESSION.query(Welcome).get(str(chat_id))
    SESSION.close()
    if welc:
        return (
            welc.should_welcome,
            welc.custom_welcome,
            welc.custom_content,
            welc.welcome_type,
        )

    else:
        # Welcome by default.
        return True, DEFAULT_WELCOME, None, Types.TEXT


def get_gdbye_pref(chat_id):
    welc = SESSION.query(Welcome).get(str(chat_id))
    SESSION.close()
    if welc:
        return welc.should_goodbye, welc.custom_leave, welc.leave_type
    else:
        # Welcome by default.
        return True, DEFAULT_GOODBYE, Types.TEXT


def set_clean_welcome(chat_id, clean_welcome):
    with INSERTION_LOCK:
        curr = SESSION.query(Welcome).get(str(chat_id))
        if not curr:
            curr = Welcome(str(chat_id))

        curr.clean_welcome = int(clean_welcome)

        SESSION.add(curr)
        SESSION.commit()


def get_clean_pref(chat_id):
    welc = SESSION.query(Welcome).get(str(chat_id))
    SESSION.close()

    if welc:
        return welc.clean_welcome

    return False


def set_welc_preference(chat_id, should_welcome):
    with INSERTION_LOCK:
        curr = SESSION.query(Welcome).get(str(chat_id))
        if not curr:
            curr = Welcome(str(chat_id), should_welcome=should_welcome)
        else:
            curr.should_welcome = should_welcome

        SESSION.add(curr)
        SESSION.commit()


def set_gdbye_preference(chat_id, should_goodbye):
    with INSERTION_LOCK:
        curr = SESSION.query(Welcome).get(str(chat_id))
        if not curr:
            curr = Welcome(str(chat_id), should_goodbye=should_goodbye)
        else:
            curr.should_goodbye = should_goodbye

        SESSION.add(curr)
        SESSION.commit()


def set_custom_welcome(
    chat_id, custom_content, custom_welcome, welcome_type, buttons=None
):
    if buttons is None:
        buttons = []

    with INSERTION_LOCK:
        welcome_settings = SESSION.query(Welcome).get(str(chat_id))
        if not welcome_settings:
            welcome_settings = Welcome(str(chat_id), True)

        if custom_welcome or custom_content:
            welcome_settings.custom_content = custom_content
            welcome_settings.custom_welcome = custom_welcome
            welcome_settings.welcome_type = welcome_type.value

        else:
            welcome_settings.custom_welcome = DEFAULT_WELCOME
            welcome_settings.welcome_type = Types.TEXT.value

        SESSION.add(welcome_settings)

        with WELC_BTN_LOCK:
            prev_buttons = (
                SESSION.query(WelcomeButtons)
                .filter(WelcomeButtons.chat_id == str(chat_id))
                .all()
            )
            for btn in prev_buttons:
                SESSION.delete(btn)

            for b_name, url, same_line in buttons:
                button = WelcomeButtons(chat_id, b_name, url, same_line)
                SESSION.add(button)

        SESSION.commit()


def get_custom_welcome(chat_id):
    welcome_settings = SESSION.query(Welcome).get(str(chat_id))
    ret = DEFAULT_WELCOME
    if welcome_settings and welcome_settings.custom_welcome:
        ret = welcome_settings.custom_welcome

    SESSION.close()
    return ret


def set_custom_gdbye(chat_id, custom_goodbye, goodbye_type, buttons=None):
    if buttons is None:
        buttons = []

    with INSERTION_LOCK:
        welcome_settings = SESSION.query(Welcome).get(str(chat_id))
        if not welcome_settings:
            welcome_settings = Welcome(str(chat_id), True)

        if custom_goodbye:
            welcome_settings.custom_leave = custom_goodbye
            welcome_settings.leave_type = goodbye_type.value

        else:
            welcome_settings.custom_leave = DEFAULT_GOODBYE
            welcome_settings.leave_type = Types.TEXT.value

        SESSION.add(welcome_settings)

        with LEAVE_BTN_LOCK:
            prev_buttons = (
                SESSION.query(GoodbyeButtons)
                .filter(GoodbyeButtons.chat_id == str(chat_id))
                .all()
            )
            for btn in prev_buttons:
                SESSION.delete(btn)

            for b_name, url, same_line in buttons:
                button = GoodbyeButtons(chat_id, b_name, url, same_line)
                SESSION.add(button)

        SESSION.commit()


def get_custom_gdbye(chat_id):
    welcome_settings = SESSION.query(Welcome).get(str(chat_id))
    ret = DEFAULT_GOODBYE
    if welcome_settings and welcome_settings.custom_leave:
        ret = welcome_settings.custom_leave

    SESSION.close()
    return ret


def get_welc_buttons(chat_id):
    try:
        return (
            SESSION.query(WelcomeButtons)
            .filter(WelcomeButtons.chat_id == str(chat_id))
            .order_by(WelcomeButtons.id)
            .all()
        )
    finally:
        SESSION.close()


def get_gdbye_buttons(chat_id):
    try:
        return (
            SESSION.query(GoodbyeButtons)
            .filter(GoodbyeButtons.chat_id == str(chat_id))
            .order_by(GoodbyeButtons.id)
            .all()
        )
    finally:
        SESSION.close()


def clean_service(chat_id: Union[str, int]) -> bool:
    try:
        chat_setting = SESSION.query(CleanServiceSetting).get(str(chat_id))
        if chat_setting:
            return chat_setting.clean_service
        return False
    finally:
        SESSION.close()


def set_clean_service(chat_id: Union[int, str], setting: bool):
    with CS_LOCK:
        chat_setting = SESSION.query(CleanServiceSetting).get(str(chat_id))
        if not chat_setting:
            chat_setting = CleanServiceSetting(chat_id)

        chat_setting.clean_service = setting
        SESSION.add(chat_setting)
        SESSION.commit()


def migrate_chat(old_chat_id, new_chat_id):
    with INSERTION_LOCK:
        chat = SESSION.query(Welcome).get(str(old_chat_id))
        if chat:
            chat.chat_id = str(new_chat_id)

        with WELC_BTN_LOCK:
            chat_buttons = (
                SESSION.query(WelcomeButtons)
                .filter(WelcomeButtons.chat_id == str(old_chat_id))
                .all()
            )
            for btn in chat_buttons:
                btn.chat_id = str(new_chat_id)

        with LEAVE_BTN_LOCK:
            chat_buttons = (
                SESSION.query(GoodbyeButtons)
                .filter(GoodbyeButtons.chat_id == str(old_chat_id))
                .all()
            )
            for btn in chat_buttons:
                btn.chat_id = str(new_chat_id)

        SESSION.commit()
