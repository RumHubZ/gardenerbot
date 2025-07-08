print("🚀 Bot file started...")

import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from datetime import timedelta

# Load token and guild ID from .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

# Setup intents and bot
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=",", intents=intents)

LEBRON_GIF_URL = "https://tenor.com/view/lebron-lebron-james-diddy-diddy-party-sean-combs-gif-4104351489513445035"  # <-- Put your LeBron gif link here

# Sync slash commands on bot ready
@bot.event
async def on_ready():
    try:
        print("Bot is ready, syncing slash commands...")
        await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
        print("✅ Slash commands synced to your server!")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

# /lebron command
@bot.tree.command(name="lebron", description="Send a LeBron gif and change your nickname to LeBron", guild=discord.Object(id=GUILD_ID))
async def lebron(interaction: discord.Interaction):
    member = interaction.user
    try:
        await member.edit(nick="LeBron")
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to change your nickname!", ephemeral=True)
        return
    except discord.HTTPException:
        await interaction.response.send_message("❌ Failed to change your nickname.", ephemeral=True)
        return

    await interaction.response.send_message(LEBRON_GIF_URL)

# Prefix command version
@bot.command(name="lebron")
async def lebron_prefix(ctx):
    member = ctx.author
    try:
        await member.edit(nick="LeBron")
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to change your nickname!")
        return
    except discord.HTTPException:
        await ctx.send("❌ Failed to change your nickname.")
        return

    await ctx.send(LEBRON_GIF_URL)

# Lebronify Command
@bot.command(name="lebronify")
async def lebronify(ctx, target: discord.Member = None):
    if not target:
        await ctx.send("❌ You need to mention someone to LeBronify, like `,lebronify @user`.")
        return

    try:
        await target.edit(nick="LeBron")

        embed = discord.Embed(
            title="🏀 LeBronification Complete!",
            description=f"{target.mention} has been LeBronified.",
            color=0x563d7c
        )
        embed.set_image(url=LEBRON_GIF_URL)

        await ctx.send(embed=embed)
    except discord.Forbidden:
        await ctx.send(f"❌ I don't have permission to change {target.mention}'s nickname.")
    except discord.HTTPException:
        await ctx.send(f"❌ Failed to change {target.mention}'s nickname.")

# Kill Command
@bot.command(name="kill")
@commands.has_permissions(ban_members=True)
async def kill(ctx, target: discord.Member = None, *, reason: str = None):
    if not target:
        await ctx.send("❌ You need to mention someone to kill, like `,kill @user`.")
        return

    try:
        await target.ban(reason=reason)
        await ctx.send(f"💀 {target.mention} has been banned from existence.")
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to ban that user.")
    except discord.HTTPException as e:
        await ctx.send(f"❌ Ban failed: {e}")

# BAN command
@bot.tree.command(name="ban", description="Ban a member from the server", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(user="Member to ban", reason="Reason for ban")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str = None):
    try:
        await user.ban(reason=reason)
        await interaction.response.send_message(f"🚫 Banned {user.mention}. Reason: {reason or 'No reason provided.'}")
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to ban that user.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ An error occurred: {e}", ephemeral=True)

# KICK command
@bot.tree.command(name="kick", description="Kick a member from the server", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(user="Member to kick", reason="Reason for kick")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, user: discord.Member, reason: str = None):
    try:
        await user.kick(reason=reason)
        await interaction.response.send_message(f"👢 Kicked {user.mention}. Reason: {reason or 'No reason provided.'}")
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to kick that user.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ An error occurred: {e}", ephemeral=True)

# TIMEOUT command
@bot.tree.command(name="timeout", description="Timeout a member", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(user="Member to timeout", duration="Duration in minutes", reason="Reason for timeout")
@app_commands.checks.has_permissions(moderate_members=True)
async def timeout(interaction: discord.Interaction, user: discord.Member, duration: int, reason: str = None):
    try:
        if not (1 <= duration <= 1440):
            await interaction.response.send_message("❌ Duration must be between 1 and 1440 minutes.", ephemeral=True)
            return
        until = discord.utils.utcnow() + timedelta(minutes=duration)
        await user.timeout(until=until, reason=reason)
        await interaction.response.send_message(
            f"⏲️ Timed out {user.mention} for {duration} minutes. Reason: {reason or 'No reason provided.'}"
        )
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to timeout that user.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ An error occurred: {e}", ephemeral=True)

# Error handler for permission errors
@ban.error
@kick.error
@timeout.error
async def on_app_command_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
    else:
        await interaction.response.send_message(f"❌ An error occurred: {error}", ephemeral=True)

# Run the bot
bot.run(TOKEN)