import discord
from discord.ext import commands
import commands as cmd_module
import events as evt_module
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configuração do bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# ORQUESTRAÇÃO CENTRAL
async def main():
    """Função principal que configura tudo"""
    async with bot:
        # Carrega commands e events
        await cmd_module.setup_commands(bot)
        await evt_module.setup_events(bot)

        # Obtém token do Discord
        token = os.getenv('DISCORD_TOKEN')
        if not token:
            print("❌ ERRO: DISCORD_TOKEN não encontrado no arquivo .env")
            print("Copie .env.example para .env e configure suas chaves API")
            return

        # Inicia o bot
        await bot.start(token)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
