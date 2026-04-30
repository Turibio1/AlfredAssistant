import discord
from discord.ext import commands

# Funções de eventos (recebem o bot como parâmetro)

async def setup_events(bot: commands.Bot):
    """Registra todos os eventos no bot"""
    
    @bot.event
    async def on_ready():
        print(f'Bot conectado como {bot.user}')
        # Sincroniza slash commands com Discord
        await bot.tree.sync()
        print('✓ Comandos sincronizados!')

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return
        
        if message.content.lower() == 'olá':
            await message.channel.send(f'Olá, {message.author.name}!')
        
        await bot.process_commands(message)
