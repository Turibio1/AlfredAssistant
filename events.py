import discord
from discord.ext import commands
from commands import ask_gemini

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
        
        if message.content.startswith('!'):
            query = message.content[1:].strip()
            if query:
                embed = await ask_gemini(query)
                embed.set_footer(text=f"Pergunta de {message.author.name}")
                await message.channel.send(embed=embed)
            return
        
        await bot.process_commands(message)
    
    @bot.event
    async def on_member_join(member):
        channel = discord.utils.get(member.guild.text_channels, name='geral')
        if channel:
            await channel.send(f'Bem-vindo(a) ao servidor, {member.mention}!\n 🚨 ATENÇÃO🚨 \nQuem quiser adicionar algum amigo ou colega no servidor para estudar ou passar o tempo pode adicionar de boa, não tem problema ser alguém que a gente não conheça, é até bom pra fazer novas conexões, só não façam virar bagunça.\n O intuíto desse servidor é ser algo que a gente possa usar pra fazer qualquer coisa no discord, sem precisar ficar criando outros servidores e salas diferentes (porque o meu já virou uma bagunça).\n Deixei nós 6 como admins pra poder criar salas, mudar regras e etc. Depois eu crio cargos novos conforme as necessidades forem surgindo.')
