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
    "Sleeping": {"id": 1219962903260696596, "label": " Sleeping", "emoji": "<:balaicouille:1477568806288363610>"},
}


intents = discord.Intents.default()
intents.members = True # Nécessaire pour display_name
bot = commands.Bot(command_prefix="/", intents=intents)

# --- SETUP BOT & INTENTS ---
intents = discord.Intents.default()
intents.members = True 
intents.message_content = True # Ajouté pour éviter le Warning et stabiliser la session
bot = commands.Bot(command_prefix="/", intents=intents)

# --- 1. CLASSE POUR LE BOUTON ---
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
            
            # Réponse immédiate pour éviter le timeout de 3 secondes
            await interaction.response.send_message(f"🚀 Envoi des 10 alertes pour **{self.role_name}** lancé !", ephemeral=True)

            for i in range(10):
                await perco_channel.send(
                    content=f"{role_mention} **ALERTE {i+1}/10 : Percepteur attaqué !** (Pingé par **{user_display_name}**)",
                    allowed_mentions=discord.AllowedMentions(roles=True) 
                )
                # Pause de 0.8s : Meilleur compromis entre vitesse et sécurité anti-spam
                await asyncio.sleep(0.8) 
            
        except discord.errors.HTTPException as e:
            if e.status == 429:
                print("🛑 Rate limit détecté par Discord (Spam trop rapide).")

# --- 2. CLASSE VIEW (Persistante) ---
class PingAttackView(View):
    def __init__(self):
        super().__init__(timeout=None) # Important pour que les boutons marchent tout le temps
        for role_key, role_data in ROLES_PING.items():
            self.add_item(PingButton(
                role_id=role_data["id"], 
                role_name=role_key, 
                label=role_data["label"], 
                emoji_btn=role_data["emoji"]
            ))

# --- 3. ÉVÉNEMENTS ---
@bot.event
async def on_ready():
    print(f"✅ Bot opérationnel : {bot.user}")
    
    # On réactive la vue pour que les anciens boutons fonctionnent encore après reboot
    bot.add_view(PingAttackView())
    
    try:
        # Synchro sur le serveur cible
        await bot.tree.sync(guild=target_guild) 
        print(f"✅ Commandes slash synchronisées sur le serveur.")
    except Exception as e:
        print(f"❌ Erreur Sync : {e}")

# --- 4. COMMANDE SETUP ---
@bot.tree.command(name="setup_ping_button", description="Envoie l'embed d'alerte avec bouton.", guild=target_guild)
@app_commands.default_permissions(administrator=True) 
async def setup_ping_button(interaction: discord.Interaction):
    setup_embed = discord.Embed(
        title="📢 Alerte Percepteur",
        description="**CLIQUEZ SUR LE BOUTON CI-DESSOUS** pour alerter l'alliance (10 pings).",
        color=discord.Color.red()
    )
    if SETUP_IMAGE_URL:
        setup_embed.set_image(url=SETUP_IMAGE_URL)
    
    # On envoie le message avec la View
    await interaction.channel.send(embed=setup_embed, view=PingAttackView())
    await interaction.response.send_message("✅ Panneau d'alerte envoyé avec succès.", ephemeral=True)

# --- LANCEMENT ---
keep_alive()
try:
    bot.run(token)
except Exception as e:
    print(f"❌ Erreur fatale au lancement : {e}")
