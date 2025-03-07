import discord
from discord.ext import commands
import re
import yfinance as yf

from config import Session, engine
from models import Base, Transaction, GuildConfig

# Créer les tables dans la base de données si elles n'existent pas
Base.metadata.create_all(engine)
session = Session()

intents = discord.Intents.default()
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} est maintenant en ligne.")

@bot.command()
@commands.has_permissions(administrator=True)
async def setchannel(ctx, channel: discord.TextChannel):
    """Définit le channel de transactions pour ce serveur."""
    guild_id = str(ctx.guild.id)
    guild_config = session.query(GuildConfig).filter_by(guild_id=guild_id).first()
    if guild_config:
        guild_config.channel_id = str(channel.id)
    else:
        guild_config = GuildConfig(guild_id=guild_id, channel_id=str(channel.id))
        session.add(guild_config)
    session.commit()
    await ctx.send(f"Channel de transactions défini sur {channel.mention}.")

@bot.event
async def on_message(message):
    if message.author == bot.user or not message.guild:
        await bot.process_commands(message)
        return

    guild_id = str(message.guild.id)
    guild_config = session.query(GuildConfig).filter_by(guild_id=guild_id).first()
    if guild_config is None or str(message.channel.id) != guild_config.channel_id:
        await bot.process_commands(message)
        return

    pattern = r"^([+-]\d+)\s+(\w+)\s+\$(\w+)"
    match = re.match(pattern, message.content)
    if match:
        quantity_str = match.group(1)
        company = match.group(2)
        ticker = match.group(3).upper()
        try:
            quantity = int(quantity_str)
        except ValueError:
            await message.channel.send("Quantité invalide.")
            return
        try:
            stock = yf.Ticker(ticker)
            price = stock.info.get('regularMarketPrice', None)
            if price is None:
                data = stock.history(period="1d")
                price = data['Close'].iloc[-1] if not data.empty else None
        except Exception as e:
            print(f"Erreur pour {ticker} : {e}")
            await message.channel.send(f"Erreur lors de la récupération du prix pour {ticker}.")
            return

        if price is None:
            await message.channel.send(f"Impossible de récupérer le prix pour le ticker {ticker}.")
            return

        transaction = Transaction(
            guild_id=guild_id,
            user=str(message.author),
            ticker=ticker,
            quantity=quantity,
            price=price
        )
        session.add(transaction)
        session.commit()

        await message.channel.send(
            f"Transaction enregistrée : {message.author} a passé un ordre de {quantity} pour {company} ({ticker}) au prix de {price}."
        )

    await bot.process_commands(message)

bot.run("")
