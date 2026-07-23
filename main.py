# Starter Discord bot template
# Replace TOKEN env var DISCORD_TOKEN

import os, discord
from discord.ext import commands

TOKEN=os.getenv("DISCORD_TOKEN")
STAFF_ROLE_ID=1480241245367308355
SESSION_CHANNEL_ID=1480256695589666917
VERIFY_CHANNEL_ID=1527458422138736660
VERIFY_ROLE_IDS=[1484208135299272828,1480241245312778466]

intents=discord.Intents.default()
intents.members=True
bot=commands.Bot(command_prefix="!",intents=intents)

class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="✅ Verify",style=discord.ButtonStyle.green,custom_id="verify")
    async def verify(self,interaction:discord.Interaction,button:discord.ui.Button):
        roles=[interaction.guild.get_role(r) for r in VERIFY_ROLE_IDS]
        await interaction.user.add_roles(*[r for r in roles if r])
        await interaction.response.send_message("Verified!",ephemeral=True)

@bot.event
async def on_ready():
    bot.add_view(VerifyView())
    await bot.tree.sync()
    print(bot.user)

@bot.tree.command(name="sendverify")
async def sendverify(interaction:discord.Interaction):
    if STAFF_ROLE_ID not in [r.id for r in interaction.user.roles]:
        return await interaction.response.send_message("No permission",ephemeral=True)
    ch=interaction.guild.get_channel(VERIFY_CHANNEL_ID)
    e=discord.Embed(title="Verify",description="Verify by clicking the button below to get access to all channels for Los Angeles State Roleplay.",color=discord.Color.blue())
    await ch.send(embed=e,view=VerifyView())
    await interaction.response.send_message("Sent!",ephemeral=True)

bot.run(TOKEN)
