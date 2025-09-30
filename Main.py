import os
import discord
from discord import app_commands
from discord.ext import commands
from keep_alive import keep_alive
import asyncio

token = os.environ['TOKEN_BOT_DISCORD']

# Salon des alertes répétées
PERCO_CHANNEL_ID = 1241543017358299208
# Salon de confirmation
CONFIRM_CHANNEL_ID = 1241543162078695595
# Salon de remerciement
THANKS_CHANNEL_ID = 1307417706898784267
# ID du rôle à mentionner
ROLE_ID = 1219962903260696596
# ID serveur discord
TARGET_GUILD_ID = 1213932847518187561

target_guild = discord.Object(id=TARGET_GUILD_ID)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")
    try:
        # Étape A : Vider les commandes GLOBALES (supprime l'ancienne version)
        bot.tree.clear_commands(guild=None) # Ceci supprime les commandes globales

        # Étape B : Synchroniser la bonne version pour la guilde cible
        synced = await bot.tree.sync(guild=target_guild) 
        print(f"✅ Commandes slash synchronisées ({len(synced)} commande(s))")
        
    except Exception as e:
        print(f"❌ Erreur lors de la synchronisation : {e}")

@bot.tree.command(name="perco", description="Déclenche une alerte percepteur", guild=target_guild)
async def perco(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)  # Répond rapidement pour éviter le timeout

    perco_channel = bot.get_channel(PERCO_CHANNEL_ID)
    confirm_channel = bot.get_channel(CONFIRM_CHANNEL_ID)
    thanks_channel = bot.get_channel(THANKS_CHANNEL_ID)

    if not all([perco_channel, confirm_channel, thanks_channel]):
        await interaction.followup.send("❌ Un ou plusieurs salons sont introuvables.", ephemeral=True)
        return

    # Message avec mention du rôle
    alert_message = (
        "Un de nos percepteurs est attaqué ! 😡\n"
        f"Prenez les armes <@&{ROLE_ID}> ! ⚔️"
    )

    # Envoi de 22 messages dans le canal d’alerte
    for _ in range(22):
        await perco_channel.send(alert_message, allowed_mentions=discord.AllowedMentions(roles=True))
        await asyncio.sleep(0.2)  # Pause anti-rate limit

    # Confirmation publique
    await confirm_channel.send("L'alerte est bien lancée !")

    # Remerciement à l’utilisateur dans un autre salon
    await thanks_channel.send(f"Merci à {interaction.user.mention} de nous avoir prévenu 🫂")

    # Réponse éphémère à l’utilisateur
    await interaction.followup.send("✅ Alerte envoyée, confirmation et remerciement publiés.", ephemeral=True)

keep_alive()
bot.run(token)
