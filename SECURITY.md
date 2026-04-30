# 🔒 Segurança - Alfred Assistant

## ⚠️ **IMPORTANTE: Nunca commite tokens ou chaves API!**

### ❌ **Arquivos que NUNCA devem ser commitados:**
- `.env` - Contém tokens do Discord e Gemini
- `*.key` - Chaves SSH
- `config.json` - Configurações sensíveis

### ✅ **Como configurar corretamente:**

1. **Crie `.env` localmente:**
```env
DISCORD_TOKEN=seu_token_aqui
GEMINI_API_KEY=sua_api_key_aqui
```

2. **No Replit:** Use **Secrets** (não crie `.env`)
3. **No servidor:** Configure variáveis de ambiente

### 🛡️ **Verificações de segurança:**

- [ ] `.env` está no `.gitignore`
- [ ] Tokens não estão no código
- [ ] Repositório é privado (recomendado)
- [ ] Não há arquivos `.key` ou `.pem` commitados

### 🚨 **Se você committou algo sensível por engano:**

```bash
# Remover arquivo do Git (mas manter localmente)
git rm --cached .env

# Ou se quiser remover completamente
git rm .env
git commit -m "Remove sensitive file"
git push
```

### 🔐 **Permissões do Bot Discord:**

Certifique-se de que o bot tem apenas as permissões necessárias:
- Send Messages
- Use Slash Commands
- Connect (voz)
- Speak (voz)

**Nunca dê permissões de administrador ao bot!**

---

**Segurança em primeiro lugar!** 🛡️