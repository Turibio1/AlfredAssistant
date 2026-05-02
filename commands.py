import discord
from discord.ext import commands
import yt_dlp
import asyncio
from collections import deque
import google.generativeai as genai
import os

async def ask_gemini(query):
    """Faz uma pergunta ao Gemini AI e retorna um embed com a resposta"""

    print(f"[GEMINI] Comando iniciado: {query}")

    # Verifica se a API key está configurada
    api_key = os.getenv('GEMINI_API_KEY')
    print(f"[GEMINI] API Key carregada: {bool(api_key)}")
    
    if not api_key:
        print("[GEMINI] Erro: API Key não encontrada")
        embed = discord.Embed(
            title="❌ Erro",
            description='**API Key do Gemini não configurada!**\n\n'
            'Para usar este comando:\n'
            '1. Acesse: https://makersuite.google.com/app/apikey\n'
            '2. Crie uma API key gratuita\n'
            '3. Adicione ao seu arquivo `.env`:\n'
            '```\n'
            'GEMINI_API_KEY=sua_api_key_aqui\n'
            'DISCORD_TOKEN=seu_token_discord\n'
            '```',
            color=0xff0000
        )
        return embed

    try:
        # Configura o Gemini
        print("[GEMINI] Configurando genai...")
        genai.configure(api_key=api_key)
        print("[GEMINI] genai configurado")

        print("[GEMINI] Criando modelo...")
        # Tenta usar gemini-2.5-flash primeiro, depois fallback para outros
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        print("[GEMINI] Modelo criado: gemini-2.5-flash")

        # Executa em thread separada para não bloquear o bot
        print("[GEMINI] Preparando para chamar generate_content...")
        loop = asyncio.get_event_loop()
        print("[GEMINI] Event loop obtido")
        
        print(f"[GEMINI] Chamando generate_content com pergunta: {query[:50]}...")
        response = await asyncio.wait_for(
            loop.run_in_executor(None, lambda: model.generate_content(query)),
            timeout=30  # Timeout de 30 segundos
        )
        print(f"[GEMINI] Resposta recebida: {response.text[:100]}...")

        # Limita a resposta a 2000 caracteres (limite do Discord)
        resposta = response.text[:1990] + "..." if len(response.text) > 1990 else response.text

        print("[GEMINI] Criando embed...")
        # Cria embed com a resposta
        embed = discord.Embed(
            title="🤖 Resposta do Gemini",
            description=resposta,
            color=0x4285f4  # Cor do Google
        )
        print("[GEMINI] Embed criado")

        return embed

    except asyncio.TimeoutError:
        print("[GEMINI] ERRO: Timeout na chamada da API")
        embed = discord.Embed(
            title="⏱️ Timeout",
            description='Gemini demorou muito para responder (timeout de 30s). Tente novamente!',
            color=0xffa500
        )
        return embed
    except Exception as e:
        error_msg = str(e)
        print(f"[GEMINI] ERRO: {type(e).__name__}: {error_msg}")
        
        # Tratamento especial para erro de quota
        if "429" in error_msg or "quota" in error_msg.lower() or "ResourceExhausted" in str(type(e)):
            print("[GEMINI] Cota gratuita excedida!")
            embed = discord.Embed(
                title="❌ Cota Excedida",
                description='**Cota da API Gemini excedida!**\n\n'
                'A sua quota gratuita diária foi atingida.\n\n'
                '**Opções:**\n'
                '1. Espere até amanhã (as quotas diárias redefinem à meia-noite UTC)\n'
                '2. Adicione um método de pagamento à sua conta Google para mais quota\n'
                '3. Acesse: https://ai.google.dev/gemini-api/docs/rate-limits',
                color=0xff0000
            )
            return embed
        else:
            import traceback
            traceback.print_exc()
            embed = discord.Embed(
                title="❌ Erro",
                description=f'Erro ao consultar Gemini: {error_msg[:100]}',
                color=0xff0000
            )
            return embed

# Configuração do yt-dlp para áudio
YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'extractaudio': True,
    'audioformat': 'mp3',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

# Classe para gerenciar fila de músicas por servidor
class MusicQueue:
    def __init__(self):
        self.queue = deque()
        self.current_song = None
        self.loop = False

    def add_song(self, title, url, requester):
        """Adiciona música à fila"""
        self.queue.append({
            'title': title,
            'url': url,
            'requester': requester
        })

    def get_next_song(self):
        """Pega próxima música da fila"""
        if self.loop and self.current_song:
            return self.current_song
        elif self.queue:
            return self.queue.popleft()
        return None

    def clear_queue(self):
        """Limpa a fila"""
        self.queue.clear()
        self.current_song = None

    def get_queue_list(self):
        """Retorna lista da fila"""
        return list(self.queue)

# Dicionário para armazenar filas por servidor
music_queues = {}

def get_music_queue(guild_id):
    """Pega ou cria fila para o servidor"""
    if guild_id not in music_queues:
        music_queues[guild_id] = MusicQueue()
    return music_queues[guild_id]

# Funções de comandos (recebem o bot como parâmetro)

async def setup_commands(bot: commands.Bot):
    """Registra todos os comandos no bot"""

    @bot.command()
    async def oi(ctx: commands.Context):
        nome = ctx.author.name
        await ctx.reply(f'Olá, {nome}!')

    @bot.tree.command(name='ping')
    async def ping(interaction: discord.Interaction):
        await interaction.response.send_message('Pong!')

    async def play_next_song(voice_client, interaction):
        """Toca próxima música da fila"""
        guild_id = interaction.guild.id
        queue = get_music_queue(guild_id)

        next_song = queue.get_next_song()
        if next_song:
            queue.current_song = next_song
            voice_client.play(
                discord.FFmpegPCMAudio(next_song['url'], **FFMPEG_OPTIONS),
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    play_next_song(voice_client, interaction), bot.loop
                ) if not e else None
            )

            # Notifica no canal de texto
            try:
                channel = interaction.channel
                embed = discord.Embed(
                    title="🎵 Tocando Agora",
                    description=f"**{next_song['title']}**\nSolicitado por: {next_song['requester']}",
                    color=0x00ff00
                )
                await channel.send(embed=embed)
            except:
                pass  # Ignora erro se não conseguir enviar

    @bot.tree.command(name='play', description='Adiciona música à fila do YouTube')
    async def play(interaction: discord.Interaction, url: str):
        """Adiciona música do YouTube à fila"""

        # Verifica se o usuário está em um canal de voz
        if not interaction.user.voice:
            await interaction.response.send_message('❌ Você precisa estar em um canal de voz!')
            return

        channel = interaction.user.voice.channel
        voice_client = interaction.guild.voice_client

        # Verifica se o bot já está conectado em outro canal
        if voice_client:
            if voice_client.channel != channel:
                await voice_client.move_to(channel)
        else:
            # Conecta ao canal de voz
            try:
                voice_client = await channel.connect()
            except Exception as e:
                await interaction.response.send_message(f'❌ Erro ao conectar: {e}')
                return

        await interaction.response.defer()  # Resposta adiada para processamento

        try:
            # Extrai informações do vídeo
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)

                if 'entries' in info:  # Se for uma playlist
                    info = info['entries'][0]

                title = info['title']
                url_audio = info['url']

            # Adiciona à fila
            guild_id = interaction.guild.id
            queue = get_music_queue(guild_id)
            queue.add_song(title, url_audio, interaction.user.mention)

            # Se não está tocando, começa a tocar
            if not voice_client.is_playing() and not voice_client.is_paused():
                await play_next_song(voice_client, interaction)
                await interaction.followup.send(f'🎵 Tocando: **{title}**')
            else:
                # Calcula posição na fila
                position = len(queue.get_queue_list())
                await interaction.followup.send(f'✅ Adicionado à fila: **{title}** (posição #{position})')

        except Exception as e:
            await interaction.followup.send(f'❌ Erro ao adicionar música: {str(e)}')

    @bot.tree.command(name='queue', description='Mostra a fila de músicas atual')
    async def queue_command(interaction: discord.Interaction):
        """Mostra a fila de músicas"""
        guild_id = interaction.guild.id
        queue = get_music_queue(guild_id)

        if not queue.current_song and not queue.get_queue_list():
            await interaction.response.send_message('📭 A fila está vazia!')
            return

        embed = discord.Embed(
            title="🎵 Fila de Músicas",
            color=0x0099ff
        )

        # Música atual
        if queue.current_song:
            embed.add_field(
                name="🎶 Tocando Agora",
                value=f"**{queue.current_song['title']}**\n{queue.current_song['requester']}",
                inline=False
            )

        # Próximas músicas
        queue_list = queue.get_queue_list()
        if queue_list:
            queue_text = ""
            for i, song in enumerate(queue_list[:10], 1):  # Mostra até 10 músicas
                queue_text += f"`{i}.` **{song['title']}** - {song['requester']}\n"

            if len(queue_list) > 10:
                queue_text += f"... e mais {len(queue_list) - 10} músicas"

            embed.add_field(
                name="📋 Próximas",
                value=queue_text,
                inline=False
            )
        else:
            embed.add_field(
                name="📋 Próximas",
                value="Nenhuma música na fila",
                inline=False
            )

        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name='skip', description='Pula para a próxima música')
    async def skip(interaction: discord.Interaction):
        """Pula a música atual"""
        voice_client = interaction.guild.voice_client

        if not voice_client or not (voice_client.is_playing() or voice_client.is_paused()):
            await interaction.response.send_message('❌ Não há música tocando!')
            return

        voice_client.stop()  # Para a música atual, o callback tocará a próxima
        await interaction.response.send_message('⏭️ Música pulada!')

    @bot.tree.command(name='stop', description='Para a música e limpa a fila')
    async def stop(interaction: discord.Interaction):
        """Para a reprodução e limpa a fila"""
        voice_client = interaction.guild.voice_client
        guild_id = interaction.guild.id
        queue = get_music_queue(guild_id)

        if voice_client and (voice_client.is_playing() or voice_client.is_paused()):
            voice_client.stop()
            queue.clear_queue()
            await interaction.response.send_message('⏹️ Música parada e fila limpa!')
        else:
            await interaction.response.send_message('❌ Não há música tocando!')

    @bot.tree.command(name='leave', description='Sai do canal de voz')
    async def leave(interaction: discord.Interaction):
        """Desconecta do canal de voz"""
        voice_client = interaction.guild.voice_client
        guild_id = interaction.guild.id
        queue = get_music_queue(guild_id)

        if voice_client:
            voice_client.stop()
            queue.clear_queue()
            await voice_client.disconnect()
            await interaction.response.send_message('👋 Sai do canal de voz!')
        else:
            await interaction.response.send_message('❌ Não estou em nenhum canal de voz!')

    @bot.tree.command(name='loop', description='Ativa/desativa loop da música atual')
    async def loop_command(interaction: discord.Interaction):
        """Ativa ou desativa o loop da música atual"""
        guild_id = interaction.guild.id
        queue = get_music_queue(guild_id)

        queue.loop = not queue.loop
        status = "ativado" if queue.loop else "desativado"
        await interaction.response.send_message(f'🔄 Loop {status}!')

    @bot.tree.command(name='gemini', description='Converse com o Gemini AI')
    async def gemini_command(interaction: discord.Interaction, pergunta: str):
        """Faz uma pergunta ao Gemini AI"""

        print(f"[GEMINI] Comando iniciado: {pergunta}")

        await interaction.response.defer()  # Resposta adiada para processamento

        embed = await ask_gemini(pergunta)
        embed.set_footer(text=f"Pergunta de {interaction.user.name}")

        print("[GEMINI] Enviando resposta para Discord...")
        await interaction.followup.send(embed=embed)
        print("[GEMINI] Resposta enviada com sucesso!")
