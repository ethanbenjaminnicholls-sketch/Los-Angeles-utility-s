import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import random
from datetime import datetime
import os

# ─── CONFIG ───────────────────────────────────────────────
DISCORD_TOKEN      = os.environ["MTUyOTY0OTg0NjA3MDI4NDM1OQ.GlnUZm.vyGdZvve2jFaW4J8zxqArmCvn47OWVjXRKgUk8"]

# Verify
VERIFY_CHANNEL_ID  = 1527458422138736660
VERIFIED_ROLE_ID   = 1484208135299272828
MEMBER_ROLE_ID     = 1480241245312778466

# Session / Giveaway
STAFF_ROLE_ID      = 1480241245367308355
SESSION_CHANNEL_ID = 1480256695589666917
SERVER_OWNER_ID    = 1435042585583554570
# ──────────────────────────────────────────────────────────

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

synced = False

# Active giveaways: { message_id -> { entries, winners, prize } }
giveaways = {}


# ─── VIEWS ────────────────────────────────────────────────

class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="✅ Verify",
        style=discord.ButtonStyle.green,
        custom_id="verify_button"
    )
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(VERIFIED_ROLE_ID)
        member_role = interaction.guild.get_role(MEMBER_ROLE_ID)

        if role is None:
            await interaction.response.send_message("❌ Verified role not found.", ephemeral=True)
            return

        if role in interaction.user.roles:
            await interaction.response.send_message("✅ You are already verified!", ephemeral=True)
            return

        roles_to_add = [r for r in [role, member_role] if r is not None]
        await interaction.user.add_roles(*roles_to_add)
        await interaction.response.send_message(
            "🎉 You have been successfully verified! Welcome to **Los Angeles State Roleplay**.",
            ephemeral=True
        )


class JoinButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(
            discord.ui.Button(
                label="🚔 Quick Join",
                style=discord.ButtonStyle.link,
                url="https://erlc.gg/join/LARPPp"
            )
        )


class GiveawayButton(discord.ui.View):
    def __init__(self, message_id: int):
        super().__init__(timeout=None)
        self.message_id = message_id

    @discord.ui.button(label="🎉 Enter Giveaway", style=discord.ButtonStyle.green)
    async def enter(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.defer(ephemeral=True)
        except discord.errors.HTTPException:
            return

        giveaway = giveaways.get(self.message_id)

        if giveaway is None:
            await interaction.followup.send("❌ This giveaway has ended.", ephemeral=True)
            return

        if interaction.user.id in giveaway["entries"]:
            await interaction.followup.send("❌ You are already entered!", ephemeral=True)
            return

        giveaway["entries"].append(interaction.user.id)
        await interaction.followup.send("✅ You have entered the giveaway!", ephemeral=True)


# ─── HELPERS ──────────────────────────────────────────────

async def staff_only(interaction: discord.Interaction) -> bool:
    role = interaction.guild.get_role(STAFF_ROLE_ID)
    if role not in interaction.user.roles:
        await interaction.followup.send(
            embed=discord.Embed(
                title="❌ No Permission",
                description="You do not have permission to use this command.",
                color=discord.Color.red()
            ),
            ephemeral=True
        )
        return False
    return True


# ─── EVENTS ───────────────────────────────────────────────

@bot.event
async def on_ready():
    global synced
    bot.add_view(VerifyView())
    if not synced:
        await bot.tree.sync()
        synced = True
        print("✅ Slash commands synced.")
    print(f"✅ Logged in as {bot.user}")


# ─── COMMANDS ─────────────────────────────────────────────

@bot.tree.command(name="sendverify", description="Send the verification panel.")
@commands.has_permissions(administrator=True)
async def sendverify(interaction: discord.Interaction):
    channel = interaction.guild.get_channel(VERIFY_CHANNEL_ID)

    if channel is None:
        await interaction.response.send_message("❌ Verification channel not found.", ephemeral=True)
        return

    embed = discord.Embed(
        title="🔒 Los Angeles State Roleplay Verification",
        description=(
            "Welcome to **Los Angeles State Roleplay!**\n\n"
            "To gain access to all server channels, click the **Verify** button below.\n\n"
            "By verifying, you agree to follow all server rules.\n\n"
            "**Click the button below to continue.**"
        ),
        color=discord.Color.blue()
    )
    embed.set_footer(text="Los Angeles State Roleplay")
    if interaction.guild.icon:
        embed.set_thumbnail(url=interaction.guild.icon.url)

    await channel.send(embed=embed, view=VerifyView())
    await interaction.response.send_message(
        f"✅ Verification panel sent to {channel.mention}.", ephemeral=True
    )


@bot.tree.command(name="session", description="Start a Los Angeles State Roleplay session.")
async def session(interaction: discord.Interaction):
    try:
        await interaction.response.defer(ephemeral=True)
    except discord.errors.HTTPException:
        return

    if not await staff_only(interaction):
        return

    channel = bot.get_channel(SESSION_CHANNEL_ID)
    if channel is None:
        await interaction.followup.send("❌ Session channel not found.", ephemeral=True)
        return

    embed = discord.Embed(
        title="🚨 Los Angeles State Roleplay Session",
        description="A new ER:LC session has started!",
        color=discord.Color.blue(),
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="👤 Host",          value=interaction.user.mention,               inline=False)
    embed.add_field(name="🔗 Join Code",     value="`LARPPp`",                             inline=False)
    embed.add_field(name="🏙️ Server Name",  value="Los Angeles State Roleplay | VC Only",  inline=False)
    embed.add_field(name="👑 Server Owner",  value=f"<@{SERVER_OWNER_ID}>",                inline=False)
    embed.set_footer(text="Los Angeles State Roleplay")

    await channel.send(embed=embed, view=JoinButton())
    await interaction.followup.send("✅ Session has been sent!", ephemeral=True)


@bot.tree.command(name="giveaway", description="Start a giveaway.")
@app_commands.describe(
    prize="The giveaway prize",
    time="How long the giveaway lasts (example: 10m, 1h, 1d)",
    winners="Number of winners"
)
async def start_giveaway(interaction: discord.Interaction, prize: str, time: str, winners: int):
    try:
        await interaction.response.defer(ephemeral=True)
    except discord.errors.HTTPException:
        return

    if not await staff_only(interaction):
        return

    seconds = 0
    if time.endswith("m"):
        seconds = int(time[:-1]) * 60
    elif time.endswith("h"):
        seconds = int(time[:-1]) * 3600
    elif time.endswith("d"):
        seconds = int(time[:-1]) * 86400
    else:
        await interaction.followup.send(
            "❌ Invalid time format. Use for example: `10m`, `1h`, or `1d`",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title="🎉 Giveaway",
        description="Click the button below to enter!",
        color=discord.Color.gold(),
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="🎁 Prize",   value=prize,        inline=False)
    embed.add_field(name="⏰ Ends In", value=time,         inline=False)
    embed.add_field(name="🏆 Winners", value=str(winners), inline=False)
    embed.set_footer(text=f"Started by {interaction.user}")

    message = await interaction.channel.send(embed=embed)
    giveaways[message.id] = {"entries": [], "winners": winners, "prize": prize}
    await message.edit(view=GiveawayButton(message.id))
    await interaction.followup.send("✅ Giveaway started!", ephemeral=True)

    await asyncio.sleep(seconds)

    giveaway_data = giveaways.pop(message.id, None)
    if not giveaway_data:
        return

    entries = giveaway_data["entries"]
    if not entries:
        await interaction.channel.send("❌ Giveaway ended with no entries.")
    else:
        count = min(giveaway_data["winners"], len(entries))
        selected = random.sample(entries, count)
        mentions = ", ".join(f"<@{uid}>" for uid in selected)
        end_embed = discord.Embed(
            title="🎉 Giveaway Ended",
            description=f"Congratulations {mentions}!",
            color=discord.Color.green()
        )
        end_embed.add_field(name="Prize", value=giveaway_data["prize"], inline=False)
        await interaction.channel.send(embed=end_embed)


# ─── RUN ──────────────────────────────────────────────────

bot.run(DISCORD_TOKEN)
