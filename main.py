import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import random
from datetime import datetime
import os

from keep_alive import keep_alive

# ── Config ────────────────────────────────────────────────────────────────────
TOKEN = os.environ.get("DISCORD_TOKEN")

STAFF_ROLE_ID = 1480241245367308355
SESSION_CHANNEL_ID = 1480256695589666917
SERVER_OWNER_ID = 1435042585583554570

# ── Bot setup ─────────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Stores active giveaways { message_id: { entries, winners, prize } }
giveaways = {}


# ── UI Views ──────────────────────────────────────────────────────────────────

class JoinButton(discord.ui.View):
    """Persistent Quick Join button for session announcements."""

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
    """Enter Giveaway button attached to a specific giveaway message."""

    def __init__(self, message_id):
        super().__init__(timeout=None)
        self.message_id = message_id

    @discord.ui.button(label="🎉 Enter Giveaway", style=discord.ButtonStyle.green)
    async def enter(self, interaction: discord.Interaction, button: discord.ui.Button):
        giveaway = giveaways.get(self.message_id)

        if giveaway is None:
            await interaction.response.send_message(
                "❌ This giveaway has ended.",
                ephemeral=True
            )
            return

        if interaction.user.id in giveaway["entries"]:
            await interaction.response.send_message(
                "❌ You are already entered!",
                ephemeral=True
            )
            return

        giveaway["entries"].append(interaction.user.id)

        await interaction.response.send_message(
            "✅ You have entered the giveaway!",
            ephemeral=True
        )


# ── Helpers ───────────────────────────────────────────────────────────────────

async def staff_only(interaction: discord.Interaction) -> bool:
    """Return True if the user has the staff role, otherwise send an error and return False."""
    role = interaction.guild.get_role(STAFF_ROLE_ID)

    if role not in interaction.user.roles:
        embed = discord.Embed(
            title="❌ No Permission",
            description="You do not have permission to use this command.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return False

    return True


# ── Events ────────────────────────────────────────────────────────────────────

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(e)

    print(f"{bot.user} is online!")


# ── Slash Commands ────────────────────────────────────────────────────────────

@bot.tree.command(
    name="session",
    description="Start a Los Angeles State Roleplay session."
)
async def session(interaction: discord.Interaction):
    if not await staff_only(interaction):
        return

    channel = bot.get_channel(SESSION_CHANNEL_ID)

    if channel is None:
        await interaction.response.send_message(
            "❌ Session channel not found.",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title="🚨 Los Angeles State Roleplay Session",
        description="A new ER:LC session has started!",
        color=discord.Color.blue(),
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="👤 Host",         value=interaction.user.mention, inline=False)
    embed.add_field(name="🔗 Join Code",    value="`LARPPp`",               inline=False)
    embed.add_field(name="🏙️ Server Name", value="Los Angeles State Roleplay | VC Only", inline=False)
    embed.add_field(name="👑 Server Owner", value=f"<@{SERVER_OWNER_ID}>",  inline=False)
    embed.set_footer(text="Los Angeles State Roleplay")

    await channel.send(embed=embed, view=JoinButton())
    await interaction.response.send_message("✅ Session has been sent!", ephemeral=True)


@bot.tree.command(
    name="giveaway",
    description="Start a giveaway."
)
@app_commands.describe(
    prize="The giveaway prize",
    time="How long the giveaway lasts (example: 10m, 1h, 1d)",
    winners="Number of winners"
)
async def giveaway(interaction: discord.Interaction, prize: str, time: str, winners: int):
    if not await staff_only(interaction):
        return

    # Parse duration
    seconds = 0
    if time.endswith("m"):
        seconds = int(time[:-1]) * 60
    elif time.endswith("h"):
        seconds = int(time[:-1]) * 3600
    elif time.endswith("d"):
        seconds = int(time[:-1]) * 86400
    else:
        await interaction.response.send_message(
            "❌ Invalid time format. Use for example: `10m`, `1h`, or `1d`",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title="🎉 Giveaway",
        description="React using the button below to enter!",
        color=discord.Color.gold(),
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="🎁 Prize",    value=prize,        inline=False)
    embed.add_field(name="⏰ Ends In",  value=time,         inline=False)
    embed.add_field(name="🏆 Winners",  value=str(winners), inline=False)
    embed.set_footer(text=f"Started by {interaction.user}")

    await interaction.response.send_message("✅ Giveaway started!", ephemeral=True)

    message = await interaction.channel.send(embed=embed)

    giveaways[message.id] = {
        "entries": [],
        "winners": winners,
        "prize": prize
    }

    await message.edit(view=GiveawayButton(message.id))

    # Wait for the giveaway to end
    await asyncio.sleep(seconds)

    giveaway_data = giveaways.pop(message.id, None)

    if not giveaway_data:
        return

    entries = giveaway_data["entries"]

    if len(entries) == 0:
        await interaction.channel.send("❌ Giveaway ended with no entries.")
    else:
        winners_count = min(giveaway_data["winners"], len(entries))
        selected = random.sample(entries, winners_count)
        winner_mentions = [f"<@{uid}>" for uid in selected]

        end_embed = discord.Embed(
            title="🎉 Giveaway Ended",
            description=f"Congratulations {', '.join(winner_mentions)}!",
            color=discord.Color.green()
        )
        end_embed.add_field(name="Prize", value=giveaway_data["prize"], inline=False)

        await interaction.channel.send(embed=end_embed)


# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not TOKEN:
        raise ValueError(
            "DISCORD_TOKEN secret is not set. "
            "Add it in the Secrets tab (the padlock icon)."
        )

    keep_alive()
    bot.run(TOKEN)
