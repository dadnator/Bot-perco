import os
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button
from keep_alive import keep_alive
import asyncio

# --- VOS CONSTANTES ---
token = os.environ['TOKEN_BOT_DISCORD']
PERCO_CHANNEL_ID = 1241543017358299208
TARGET_GUILD_ID = 1213932847518187561
target_guild = discord.Object(id=TARGET_GUILD_ID)

SETUP_IMAGE_URL = "https://i.imgur.com/8setyQq.png" 

ROLES_PING = {
    "Sleeping": {"id": 1219962903260696596, "label": " Sleeping", "emoji": "🛡️"},
}


intents = discord.Intents.default()
intents.members = True # Nécessaire pour display_name
bot = commands.Bot(command_prefix="/", intents=intents)

# --- 1. CLASSE POUR LE BOUTON INDIVIDUEL ---
class PingButton(Button):
    def __init__(self, role_id: int, role_name: str, label: str, emoji_btn: str):
        super().__init__(
            label=label,
            style=discord.ButtonStyle.danger,
            emoji=emoji_btn,
            custom_id=f"ping_button_{role_name.lower().replace(' ', '_')}" 
        )
        self.role_id = role_id
        self.role_name = role_name
        
    async def callback(self, interaction: discord.Interaction):
        try:
            perco_channel = interaction.client.get_channel(PERCO_CHANNEL_ID)
            if not perco_channel:
                return await interaction.response.send_message("❌ Salon introuvable.", ephemeral=True)

            role_mention = f"<@&{self.role_id}>"
            user_display_name = interaction.user.display_name
            
            # --- MODIFICATION ICI : BOUCLE POUR 10 ENVOIS ---
            # On répond d'abord à l'interaction pour éviter le timeout de 3 secondes
            await interaction.response.send_message(f"🚀 Envoi de 10 alertes pour **{self.role_name}**...", ephemeral=True)

            for i in range(10):
                await perco_channel.send(
                    content=f"{role_mention} **ALERTE {i+1}/10 : Votre percepteur est attaqué !** (Par **{user_display_name}**)",
                    allowed_mentions=discord.AllowedMentions(roles=True) 
                )
                # Une micro-pause pour éviter de se faire bloquer par l'anti-spam de Discord
                await asyncio.sleep(0.5) 
            
        except discord.errors.HTTPException as e:
            if e.status == 429:
                print("🛑 Rate limit (spam) détecté !")

# --- 2. CLASSE VIEW ---
class PingAttackView(View):
    def __init__(self):
        super().__init__(timeout=None)
        for role_key, role_data in ROLES_PING.items():
            self.add_item(PingButton(role_id=role_data["id"], role_name=role_key, label=role_data["label"], emoji_btn=role_data["emoji"]))

# --- 3. ÉVÉNEMENTS ---
@bot.event
async def on_ready():
    print(f"✅ Bot Connecté : {bot.user}")
    
    # PAUSE DE SÉCURITÉ : Laisse le bot se stabiliser avant de synchroniser
    await asyncio.sleep(5)
    
    try:
        bot.add_view(PingAttackView())
        # UNE SEULE SYNCHRO : On synchronise uniquement sur le serveur cible
        await bot.tree.sync(guild=target_guild) 
        print(f"✅ Commandes slash synchronisées sur le serveur.")
    except Exception as e:
        print(f"❌ Erreur Sync : {e}")

# --- 4. COMMANDE SETUP ---
@bot.tree.command(name="setup_ping_button", description="Envoie l'embed avec les boutons.", guild=target_guild)
@app_commands.default_permissions(administrator=True) 
async def setup_ping_button(interaction: discord.Interaction):
    setup_embed = discord.Embed(
        title="📢 Un Perco Attaqué ",
        description="**CLIQUEZ UNE FOIS** sur le bouton pour alerter.",
        color=discord.Color.blue()
    )
    if SETUP_IMAGE_URL:
        setup_embed.set_image(url=SETUP_IMAGE_URL)
    
    await interaction.channel.send(embed=setup_embed, view=PingAttackView())
    await interaction.response.send_message("✅ Panneau envoyé.", ephemeral=True)

# --- LANCEMENT ---
keep_alive()
try:
    bot.run(token)
except Exception as e:
    print(f"❌ Erreur fatale au lancement : {e}")
