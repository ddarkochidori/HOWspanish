import discord
from discord.ext import commands
import json
import asyncio
import datetime
import random
import re

# --- CONFIGURACIÓN PRINCIPAL (¡AJUSTAR ESTO!) ---
TOKEN = 'MTQ0NTExMjMyNTM3NDczODQ4Mg.GSze8k.uS7Xc2M4vIQ-Ix_g25EQD13XQeHSTkwivfvMKk'  # 🛑 ¡REEMPLAZA ESTO CON TU TOKEN REAL!
PREFIX = '!!' 

# IDs de ROLES DE STAFF (¡Debes reemplazar estos números!)
STAFF_ROLE_ID = 1413900760156213343  # Rol general de STAFF/Moderador
MOD_ROLE_ID = 1413900760156213342    # Rol de Mods o Administradores
OWNER_ROLE_ID = 1413900760164470908  # Rol de Owner/Dueño (Si existe un rol)
# ID de la Categoría donde se crearán los Tickets (0 si no usas una específica)
TICKET_CATEGORY_ID = 0 

# --- BASE DE DATOS Y PERMISOS ---

# Permisos requeridos para los comandos de moderación
MOD_PERMS = {
    'kick': discord.Permissions.kick_members,
    'ban': discord.Permissions.ban_members,
    'timeout': discord.Permissions.moderate_members,
    'purge': discord.Permissions.manage_messages,
    'warn': discord.Permissions.moderate_members,
    'sorteo': discord.Permissions.manage_messages 
}

# Lista de palabras prohibidas (Ampliada y normalizada)
PROHIBITED_WORDS = [
    "p*ta", "zorra", "m*erda", "f*ck", "fuck you", "c*caína", "heroína", "matate", "suicida", "nazi", "gore", 
    "porno", "nsfw", "te voy a matar", "doxearte", "hakearte", "free nitro", "gratis nitro", "estafa", "virus", 
    "troyano", "chupa pija", "idiota", "come vergas", "neko fuck", "malparido", "perro hp", "marihuana", 
    "la concha de tu hermana", "come mierda", "retrasado", "hijo de puta", "puto", "maricon", "cabron", 
    "gilipollas", "tonto", "asshole", "bitch", "cunt", "faggot", "slut", "whore", "paki", "kike", "nigger",
    "retard", "autist", "chinga", "verga", "pene", "coño", "culo", "vagina", "mierda"
] 

# Diccionario para almacenar las advertencias {server_id: {user_id: count}}
try:
    with open('warnings.json', 'r') as f:
        warnings_data = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    warnings_data = {}

# --- FORMULARIO DE POSTULACIÓN DE STAFF (DIVIDIDO PARA EVITAR ERROR 50035) ---

STAFF_FORM_PART1 = """# 📝 Formulario de Postulación para Staff de Megami の国 (Parte 1/3)
> Completa este formulario con la mayor honestidad y detalle posible. Las respuestas incompletas, vagas o copiadas serán descartadas automáticamente.

## 📋 INFORMACIÓN GENERAL
1. Nombre (o nickname en Discord):
2. ID de Discord (usuario#0000):
3. Edad:
4. País y zona horaria:
5. Horarios disponibles (días y horas, especificar):
6. ¿A qué puesto postulas? (Moderador / Administrador / Soporte / Community Manager):

## 🧠 EXPERIENCIA Y CONOCIMIENTOS
7. ¿Has sido staff anteriormente? Explica en qué servidores, tamaño de estos y tus funciones específicas.
8. ¿Qué diferencia hay entre un moderador reactivo y uno proactivo?
9. Enumera y explica al menos 5 herramientas de moderación de Discord o bots que conozcas."""

STAFF_FORM_PART2 = """# 📝 Formulario de Postulación (Parte 2/3)

10. Describe el procedimiento correcto ante:
    a) Raid masivo con bots.
    b) Conflicto grave entre dos miembros veteranos.
    c) Usuario que incumple normas pero es amigo del dueño.

## 🧩 SITUACIONES HIPOTÉTICAS (ANÁLISIS COMPLEJO)
11. Un usuario con advertencias previas insulta a otro miembro, pero luego se disculpa públicamente. ¿Cómo actúas? Justifica tu decisión.
12. Detectas que otro staff abusa de su poder pero es muy querido en el servidor. ¿Qué harías paso a paso?
13. Un miembro acusa falsamente a otro de acoso y presenta capturas editadas. ¿Cómo procedes?

## 💚 PSICOLOGÍA Y MANEJO DE COMUNIDAD
14. ¿Cómo mantendrías un ambiente sano sin caer en autoritarismo?
15. ¿Qué harías si la comunidad se vuelve tóxica hacia un grupo específico?
16. Define con tus palabras: liderazgo, imparcialidad y empatía dentro de un staff."""

STAFF_FORM_PART3 = """# 📝 Formulario de Postulación (Parte 3/3)

## 📚 CONOCIMIENTO DE NORMATIVA
17. Redacta 3 normas claras y profesionales que implementarías en un servidor grande.
18. ¿Por qué es importante la consistencia al aplicar sanciones?
19. Explica la diferencia entre advertencia, mute, kick y ban, y cuándo usar cada una.

## ⭐ PRUEBA DE COMPROMISO
20. ¿Por qué quieres formar parte del staff de este servidor y qué aportarías que otros no?
21. Si no eres seleccionado, ¿cómo reaccionarías?
22. ¿Cuánto tiempo mínimo podrías comprometerte semanalmente?

## 📝 PREGUNTA FILTRO (OBLIGATORIA)
23. Describe un error que hayas cometido como moderador (o en cualquier rol de responsabilidad) y qué aprendiste de el."""

# --- FUNCIONES DE UTILIDAD ---

def save_warnings():
    """Guarda el estado actual de las advertencias en el archivo JSON."""
    with open('warnings.json', 'w') as f:
        json.dump(warnings_data, f, indent=4)

def check_mod_perms(command_name):
    """Verifica si el autor del mensaje tiene el permiso de moderación requerido."""
    async def predicate(ctx):
        if MOD_PERMS.get(command_name) is None:
            return True 
        
        if ctx.author.guild_permissions >= MOD_PERMS[command_name]:
            return True
        else:
            await ctx.send(f'❌ **Permiso Denegado:** Necesitas el permiso de `{MOD_PERMS[command_name].name}` para usar este comando.')
            return False
    return commands.check(predicate)

def parse_time(time_str):
    """Convierte una cadena de tiempo (ej: 10m, 1h) a segundos."""
    match = re.match(r'(\d+)([smhd])', time_str, re.I)
    if not match:
        return None
    amount, unit = match.groups()
    amount = int(amount)
    
    if unit.lower() == 's': return amount
    elif unit.lower() == 'm': return amount * 60
    elif unit.lower() == 'h': return amount * 3600
    elif unit.lower() == 'd': return amount * 86400
    return None

# --- CLASE PRINCIPAL DEL BOT ---
class MegamiSoporte(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True     
        intents.message_content = True 
        intents.reactions = True 
        
        super().__init__(
            command_prefix=PREFIX, 
            intents=intents,
            help_command=None 
        )

    async def on_ready(self):
        print(f'✨ Megami Soporte conectado como {self.user} (ID: {self.user.id})')
        await self.change_presence(activity=discord.Game(name=f'{PREFIX}help | Moderando la paz'))

    # --- AUTO-MODERACIÓN (FILTRO ANTI-PALABRAS) ---
    async def on_message(self, message):
        if message.author.bot:
            return

        content = message.content.lower()

        # Filtro de Palabras Prohibidas
        for word in PROHIBITED_WORDS:
            if word in content:
                try:
                    await message.delete()
                    await message.channel.send(
                        f'🚫 **¡{message.author.mention},** esa palabra está prohibida! Sanción automática aplicada.',
                        delete_after=5
                    )
                    break 
                except discord.Forbidden:
                    print(f"Error: No tengo permisos para borrar mensajes en {message.channel.name}.")
                    break

        await self.process_commands(message)

# Inicializar el bot
bot = MegamiSoporte()

# --- COMANDOS DE MODERACIÓN PURA Y FUERTE ---

@bot.command(name='ban')
@check_mod_perms('ban')
async def ban(ctx, member: discord.Member, *, reason="No especificada"):
    """Banea permanentemente a un miembro del servidor."""
    if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
        return await ctx.send("❌ No puedes banear a alguien con un rol igual o superior al tuyo.")
    try:
        await member.ban(reason=reason)
        await ctx.send(f'🔨 **{member.display_name}** ha sido baneado. Razón: *{reason}*')
    except discord.Forbidden:
        await ctx.send("❌ Error: No tengo permisos para banear a este usuario (Mi rol es inferior).")

@bot.command(name='kick')
@check_mod_perms('kick')
async def kick(ctx, member: discord.Member, *, reason="No especificada"):
    """Expulsa a un miembro del servidor."""
    if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
        return await ctx.send("❌ No puedes expulsar a alguien con un rol igual o superior al tuyo.")
    try:
        await member.kick(reason=reason)
        await ctx.send(f'👟 **{member.display_name}** ha sido expulsado. Razón: *{reason}*')
    except discord.Forbidden:
        await ctx.send("❌ Error: No tengo permisos para expulsar a este usuario (Mi rol es inferior).")

@bot.command(name='timeout', aliases=['mute', 'tiempoespera'])
@check_mod_perms('timeout')
async def timeout(ctx, member: discord.Member, minutes: int, *, reason="No especificada"):
    """Aplica un tiempo de espera (mute) a un miembro."""
    if minutes <= 0:
        return await ctx.send("❌ El tiempo debe ser mayor a 0 minutos.")
    try:
        duration = discord.utils.utcnow() + discord.timedelta(minutes=minutes)
        await member.timeout(duration, reason=reason)
        await ctx.send(f'🔇 **{member.display_name}** ha sido silenciado por **{minutes} minutos**. Razón: *{reason}*')
    except discord.Forbidden:
        await ctx.send("❌ Error: No tengo permisos para aplicar el tiempo de espera a este usuario.")
    except Exception as e:
        await ctx.send(f"❌ Error al silenciar: {e}")

@bot.command(name='purge', aliases=['clear', 'limpiar'])
@check_mod_perms('purge')
async def purge(ctx, amount: int):
    """Elimina una cantidad específica de mensajes en el canal."""
    if amount < 1 or amount > 100:
        return await ctx.send("❌ Debes especificar un número entre 1 y 100.")
    try:
        deleted = await ctx.channel.purge(limit=amount + 1) 
        await ctx.send(f'🧹 Se eliminaron **{len(deleted) - 1} mensajes** en este canal.', delete_after=5)
    except discord.Forbidden:
        await ctx.send("❌ Error: No tengo permisos para gestionar mensajes en este canal.")

@bot.command(name='warn', aliases=['advertir'])
@check_mod_perms('warn')
async def warn(ctx, member: discord.Member, *, reason="No especificada"):
    """Aplica una advertencia a un miembro y registra la acción (con sanción automática)."""
    global warnings_data
    guild_id = str(ctx.guild.id)
    user_id = str(member.id)

    if guild_id not in warnings_data: warnings_data[guild_id] = {}
    if user_id not in warnings_data[guild_id]: warnings_data[guild_id][user_id] = []
    
    warnings_data[guild_id][user_id].append({'moderator': str(ctx.author), 'reason': reason, 'timestamp': str(discord.utils.utcnow())})
    save_warnings()
    count = len(warnings_data[guild_id][user_id])
    await ctx.send(f'⚠️ **{member.display_name}** ha recibido una advertencia ({count}). Razón: *{reason}*')
    
    # Sanción Automática
    if count == 3:
        await ctx.send(f'🚨 **¡3 Advertencias!** Aplicando mute automático a {member.display_name} por 30 minutos.')
        duration = discord.utils.utcnow() + discord.timedelta(minutes=30)
        await member.timeout(duration, reason="Acumulación de 3 advertencias.")
    elif count >= 5:
        await ctx.send(f'🚨 **¡{count} Advertencias!** Aplicando ban automático a {member.display_name} por mal comportamiento persistente.')
        await member.ban(reason="Acumulación excesiva de advertencias.")
        
@bot.command(name='warnings', aliases=['verwarns'])
@check_mod_perms('warn')
async def check_warnings(ctx, member: discord.Member):
    """Muestra el historial de advertencias de un miembro."""
    guild_id = str(ctx.guild.id)
    user_id = str(member.id)
    
    if guild_id not in warnings_data or user_id not in warnings_data[guild_id]:
        return await ctx.send(f'✅ **{member.display_name}** no tiene advertencias registradas.')
        
    warns = warnings_data[guild_id][user_id]
    
    embed = discord.Embed(
        title=f"⚠️ Historial de Advertencias de {member.display_name}",
        description=f"Total: **{len(warns)}**",
        color=discord.Color.orange()
    )
    for i, warn_entry in enumerate(warns, 1):
        timestamp_short = warn_entry['timestamp'][:10] 
        embed.add_field(name=f"#{i} - Por {warn_entry['moderator']}", value=f"Razón: {warn_entry['reason']}\nFecha: {timestamp_short}", inline=False)
        
    await ctx.send(embed=embed)


# --- SISTEMA DE TICKETS (POSTULACIÓN STAFF) ---

@bot.command(name='apply', aliases=['postular'])
async def apply_staff(ctx):
    """Abre un ticket de postulación a Staff y etiqueta a los roles clave."""
    
    if discord.utils.get(ctx.guild.channels, name=f"aplicacion-{ctx.author.name.lower().replace(' ', '-')}"):
        return await ctx.send("❌ Ya tienes un ticket de postulación abierto. Por favor, sé paciente.")

    try:
        # 1. Obtener los roles de staff
        staff_roles_to_mention = []
        
        # Lista de IDs que deben tener permisos de lectura en el ticket
        permission_role_ids = [STAFF_ROLE_ID, MOD_ROLE_ID, OWNER_ROLE_ID]
        
        for role_id in permission_role_ids:
            role = ctx.guild.get_role(role_id)
            if role:
                staff_roles_to_mention.append(role.mention)
        
        if not staff_roles_to_mention:
             return await ctx.send("❌ Error: No se pudo identificar ningún rol de Staff con las IDs proporcionadas. Verifica la configuración.")
        
        # Configuración de permisos de lectura para el ticket
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }
        
        # Añadir permisos de lectura/escritura a los roles de staff
        for role_id in permission_role_ids:
            role = ctx.guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)


        # 2. Crear el canal de ticket
        channel_name = f"aplicacion-{ctx.author.name.lower().replace(' ', '-')}"
        category = discord.utils.get(ctx.guild.categories, id=TICKET_CATEGORY_ID)
        
        ticket_channel = await ctx.guild.create_text_channel(
            channel_name, 
            overwrites=overwrites, 
            category=category
        )
        
        # 3. Notificar al usuario y al staff
        await ctx.send(f"✅ ¡Tu ticket de postulación ha sido abierto en {ticket_channel.mention}!", delete_after=10)
        
        # 4. Mensaje de bienvenida con TODAS las menciones y envío del FORMULARIO DIVIDIDO
        
        mentions_string = " ".join(staff_roles_to_mention)
        await ticket_channel.send(f"**¡NUEVA POSTULACIÓN!** {mentions_string}\nEl usuario {ctx.author.mention} ha iniciado un proceso de postulación a Staff.")
        
        # Envío de las 3 partes del formulario como bloques de código Markdown
        await ticket_channel.send("```markdown\n" + STAFF_FORM_PART1 + "\n```")
        await ticket_channel.send("```markdown\n" + STAFF_FORM_PART2 + "\n```")
        await ticket_channel.send("```markdown\n" + STAFF_FORM_PART3 + "\n```")
        
        await ticket_channel.send("👆 **¡ATENCIÓN!** Por favor, copia, pega y rellena el formulario completo que aparece justo arriba (está dividido en 3 partes). Una vez que hayas respondido, el Staff lo revisará.")
        
        # Mensaje final del ticket
        embed = discord.Embed(
            title="Ticket Creado",
            description=f"Postulación a Staff por: {ctx.author.mention}",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Usa {PREFIX}close para cerrar este ticket.")
        await ticket_channel.send(embed=embed)

    except discord.Forbidden:
        await ctx.send("❌ Error: No tengo permisos para crear canales o gestionar permisos. Asegúrate de que mi rol esté por encima de todos los roles de Staff y que tengo permiso de `manage_channels`.")
    except Exception as e:
        await ctx.send(f"❌ Ocurrió un error al crear el ticket: {e}")

@bot.command(name='close')
@commands.has_permissions(manage_channels=True)
async def close_ticket(ctx):
    """Cierra el canal de ticket (solo para Staff)."""
    if not ctx.channel.name.startswith("aplicacion-"):
        return await ctx.send("❌ Este comando solo puede usarse dentro de un canal de postulación (ticket).")
    
    await ctx.send("Ticket cerrado. Este canal se eliminará en 5 segundos.")
    await asyncio.sleep(5)
    await ctx.channel.delete()


# --- SISTEMA DE SORTEOS ---

@bot.command(name='sorteo')
@check_mod_perms('sorteo')
async def giveaway(ctx, time: str, *, prize: str):
    """Inicia un sorteo con duración y premio. Ejemplo: !sorteo 1h Ganar Nitro"""
    
    seconds = parse_time(time)
    if seconds is None or seconds < 10:
        return await ctx.send("❌ Formato de tiempo inválido. Usa: 10s, 5m, 1h, 2d. (Mínimo 10 segundos).")

    end_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
    
    embed = discord.Embed(
        title=f"🎁 ¡SORTEO! - {prize}",
        description=f"Reacciona con 🎉 para participar.\nDuración: **{time}**\nTermina: <t:{int(end_time.timestamp())}:R>", 
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"Organizado por {ctx.author.display_name}")
    
    await ctx.message.delete()
    giveaway_msg = await ctx.send("🎉 **¡NUEVO SORTEO!** 🎉", embed=embed)
    await giveaway_msg.add_reaction("🎉")

    await asyncio.sleep(seconds)

    try:
        updated_msg = await ctx.channel.fetch_message(giveaway_msg.id)
    except:
        return 

    reaction = discord.utils.get(updated_msg.reactions, emoji="🎉")
    if reaction:
        participants = [user async for user in reaction.users() if user != bot.user]
    else:
        participants = []

    if not participants:
        await ctx.send(f"😔 El sorteo por **{prize}** ha terminado, pero no hay participantes válidos.")
    else:
        winner = random.choice(participants)
        
        winner_embed = discord.Embed(
            title="🎉 ¡GANADOR SELECCIONADO! 🎉",
            description=f"¡Felicidades {winner.mention}! Has ganado: **{prize}**",
            color=discord.Color.gold()
        )
        await ctx.send(f"¡Felicitaciones, {winner.mention}!", embed=winner_embed)

@bot.command(name='reroll')
@check_mod_perms('sorteo')
async def reroll_giveaway(ctx, message_id: int):
    """Vuelve a sortear un ganador de un mensaje de sorteo anterior."""
    try:
        old_msg = await ctx.channel.fetch_message(message_id)
        reaction = discord.utils.get(old_msg.reactions, emoji="🎉")
        
        if not reaction:
            return await ctx.send("❌ No se encontró la reacción '🎉' en ese mensaje.")
            
        participants = [user async for user in reaction.users() if user != bot.user]
        
        if not participants:
            return await ctx.send("😔 No hay suficientes participantes válidos para sortear de nuevo.")
            
        new_winner = random.choice(participants)
        
        prize = old_msg.embeds[0].title.replace("🎁 ¡SORTEO! - ", "") if old_msg.embeds and old_msg.embeds[0].title.startswith("🎁") else "Premio no especificado"

        reroll_embed = discord.Embed(
            title="🔄 ¡NUEVO SORTEO! (Reroll) 🔄",
            description=f"¡Felicidades {new_winner.mention}! Has ganado: **{prize}**",
            color=discord.Color.teal()
        )
        await ctx.send(f"Reroll completado. ¡El nuevo ganador es {new_winner.mention}!", embed=reroll_embed)

    except discord.NotFound:
        await ctx.send("❌ Mensaje no encontrado. Asegúrate de que el ID del mensaje es correcto y está en este canal.")
    except Exception as e:
        await ctx.send(f"❌ Error al realizar el reroll: {e}")


# --- COMANDO DE AYUDA PERSONALIZADO (HELP) ---
@bot.command(name='help', aliases=['ayuda'])
async def custom_help(ctx):
    """Muestra una lista de todos los comandos de Moderación y Soporte."""
    
    embed = discord.Embed(
        title="🌸 Megami Soporte | Comandos",
        description=f"Usa el prefijo `{bot.command_prefix}` antes de cada comando. ¡La paz es la ley!",
        color=discord.Color.red()
    )
    
    # --- SECCIÓN DE MODERACIÓN ---
    embed.add_field(
        name="🛠️ Comandos de Moderación (Sanción y Control)",
        value=(
            f"`{bot.command_prefix}ban <@usuario> [razón]` - Banea permanentemente.\n"
            f"`{bot.command_prefix}kick <@usuario> [razón]` - Expulsa.\n"
            f"`{bot.command_prefix}timeout <@usuario> <min> [razón]` - Silencia temporalmente (mute).\n"
            f"`{bot.command_prefix}purge <cantidad>` - Limpia mensajes (hasta 100).\n"
            f"`{bot.command_prefix}warn <@usuario> [razón]` - Aplica y registra advertencia (con sanción auto. a 3/5).\n"
            f"`{bot.command_prefix}warnings <@usuario>` - Muestra historial de advertencias."
        ),
        inline=False
    )
    
    # --- SECCIÓN DE UTILIDADES Y COMUNIDAD ---
    embed.add_field(
        name="⭐ Comandos de Utilidad y Comunidad",
        value=(
            f"`{bot.command_prefix}apply` - Abre un ticket para postular a Staff. (Usuarios)\n"
            f"`{bot.command_prefix}close` - Cierra el ticket de postulación. (Staff)\n"
            f"`{bot.command_prefix}sorteo <tiempo> <premio>` - Inicia un nuevo sorteo. (Staff)\n"
            f"`{bot.command_prefix}reroll <ID>` - Selecciona otro ganador para un sorteo pasado. (Staff)"
        ),
        inline=False
    )
    
    embed.set_footer(text=f"Recuerda: El filtro Anti-Palabras Prohibidas está activo 24/7.")
    
    await ctx.send(embed=embed)


# --- EJECUCIÓN DEL BOT ---
if __name__ == '__main__':
    bot.run(TOKEN)
