import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")

VERIFY_ROLE = 1484208135299272828
STAFF_ROLE = 1480241245367308355

SESSION_CHANNEL = 1480241245312778466

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# ---------------- START ----------------

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")

    except Exception as e:
        print(e)



# Permission Check

def has_staff_role(interaction: discord.Interaction):

    role = discord.utils.get(
        interaction.user.roles,
        id=STAFF_ROLE
    )

    return role is not None



# ---------------- VERIFY ----------------


class VerifyButton(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)


    @discord.ui.button(
        label="Verify",
        style=discord.ButtonStyle.green,
        emoji="✅"
    )
    async def verify(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        role = interaction.guild.get_role(
            VERIFY_ROLE
        )

        if role in interaction.user.roles:
            await interaction.response.send_message(
                "You are already verified!",
                ephemeral=True
            )
            return


        await interaction.user.add_roles(role)

        await interaction.response.send_message(
            "✅ You have been verified!",
            ephemeral=True
        )



@bot.tree.command(
    name="verify",
    description="Send the verification message"
)
async def verify(interaction: discord.Interaction):

    embed = discord.Embed(
        title="Los Angeles State Roleplay Verification",
        description=
        "Click the button below to verify and gain access to the server.",
        color=0x00ff00
    )

    embed.set_footer(
        text="Los Angeles State Roleplay"
    )

    await interaction.response.send_message(
        embed=embed,
        view=VerifyButton()
    )



# ---------------- SESSION ----------------


class JoinServer(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)


    @discord.ui.button(
        label="Join Server",
        style=discord.ButtonStyle.link,
        url="https://erlc.gg/LARPPp",
        emoji="🎮"
    )
    async def join(
        self,
        interaction,
        button
    ):
        pass



@bot.tree.command(
    name="session",
    description="Start a roleplay session"
)
async def session(interaction: discord.Interaction):

    if not has_staff_role(interaction):
        await interaction.response.send_message(
            "❌ You do not have permission.",
            ephemeral=True
        )
        return


    embed = discord.Embed(
        title="Los Angeles State Roleplay Session",
        color=0x0066ff
    )

    embed.add_field(
        name="Host",
        value=interaction.user.mention,
        inline=False
    )

    embed.add_field(
        name="Server Name",
        value="Los Angeles State Roleplay",
        inline=False
    )

    embed.add_field(
        name="Server Type",
        value="VC Only",
        inline=False
    )

    embed.add_field(
        name="Server Code",
        value="LARPPp",
        inline=False
    )


    embed.set_footer(
        text="Los Angeles State Roleplay"
    )


    channel = bot.get_channel(
        SESSION_CHANNEL
    )


    await channel.send(
        embed=embed,
        view=JoinServer()
    )


    await interaction.response.send_message(
        "✅ Session posted!",
        ephemeral=True
    )



bot.run(TOKEN)
@bot.tree.command(
    name="giveaway",
    description="Create a giveaway"
)
@app_commands.describe(
    prize="Giveaway prize",
    winners="Number of winners",
    time="Giveaway time"
)
async def giveaway(
    interaction: discord.Interaction,
    prize: str,
    winners: int,
    time: str
):

    if not has_staff_role(interaction):
        await interaction.response.send_message(
            "❌ You do not have permission.",
            ephemeral=True
        )
        return


    embed = discord.Embed(
        title="🎉 Giveaway",
        color=0xffd700
    )

    embed.add_field(
        name="Prize:",
        value=prize,
        inline=False
    )

    embed.add_field(
        name="Winners:",
        value=str(winners),
        inline=False
    )

    embed.add_field(
        name="Time:",
        value=time,
        inline=False
    )

    embed.set_footer(
        text="Los Angeles State Roleplay Giveaway"
    )


    await interaction.response.send_message(
        embed=embed
    )
