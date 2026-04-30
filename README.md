# 🤖 Alfred Assistant - Bot Discord

Bot Discord completo com sistema de música e integração com Gemini AI.

## 🚀 Funcionalidades

### 🎵 Sistema de Música
- `/play <url>` - Toca música do YouTube
- `/queue` - Mostra fila de músicas
- `/skip` - Pula para próxima música
- `/stop` - Para música e limpa fila
- `/leave` - Sai do canal de voz
- `/loop` - Ativa/desativa loop

### 🤖 Gemini AI
- `/gemini <pergunta>` - Converse com IA do Google

### 📝 Comandos Gerais
- `/ping` - Testa latência
- `!oi` - Saudação simples

## ⚙️ Configuração

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar APIs

#### Discord Bot Token
1. Acesse [Discord Developer Portal](https://discord.com/developers/applications)
2. Crie uma aplicação
3. Vá em "Bot" e copie o token

#### Gemini API Key (Gratuita)
1. Acesse [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Crie uma API key gratuita
3. Copie a chave

### 3. Arquivo .env
Configure o arquivo `.env`:
```env
DISCORD_TOKEN=seu_token_discord_aqui
GEMINI_API_KEY=sua_api_key_gemini_aqui
```

### 4. Permissões do Bot
No Discord Developer Portal, ative estas intents:
- ✅ Message Content Intent
- ✅ Server Members Intent

E dê estas permissões ao bot:
- Send Messages
- Use Slash Commands
- Connect (voz)
- Speak (voz)

## 🎯 Como Usar

### Música
```bash
/play never gonna give you up
/play https://www.youtube.com/watch?v=dQw4w9WgXcQ
/queue
/skip
```

### Gemini AI
```bash
/gemini Qual é a capital do Brasil?
/gemini Me explique como funciona a fotosíntese
```

## 🏃‍♂️ Executar

```bash
python main.py
```

## 📋 Estrutura do Projeto

```
├── main.py          # Arquivo principal
├── commands.py      # Comandos do bot
├── events.py        # Eventos do bot
├── .env            # Configurações (não subir pro Git)
├── .env.example    # Exemplo de configuração
└── README.md       # Este arquivo
```

## 🔧 Tecnologias

- **discord.py** - Framework Discord
- **yt-dlp** - Download de áudio YouTube
- **google-generativeai** - API Gemini
- **python-dotenv** - Carregamento de variáveis ambiente

## 📄 Licença

Este projeto é open source. Use como quiser!

---

**Criado com ❤️ para a comunidade Discord**