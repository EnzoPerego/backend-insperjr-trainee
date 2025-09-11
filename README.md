# Backend InsperJr Trainee - Restaurante de Delivery

Backend da aplicação de restaurante de delivery desenvolvido com FastAPI e MongoDB.

## 🚀 Como executar

### Pré-requisitos
- **Python** (versão 3.9+)
- **Git** (para baixar o projeto)
- **MongoDB Atlas** (banco de dados na nuvem)

### Passo a passo

1. **Instale o Python** (se não tiver):
   - Acesse: https://www.python.org/downloads/
   - Baixe a versão **3.9+** (recomendada)
   - Execute o instalador e **marque "Add Python to PATH"**

2. **Configure o MongoDB Atlas:**
   - Acesse: https://www.mongodb.com/cloud/atlas
   - Crie uma conta gratuita
   - Crie um cluster gratuito
   - Configure Network Access (0.0.0.0/0)
   - Crie um usuário e anote a senha
   - Copie a string de conexão

3. **Baixe o projeto:**
   - Clone o repositório ou baixe o ZIP
   - Extraia em uma pasta de sua escolha

4. **Abra o Terminal/Prompt de Comando:**
   - **Windows**: Pressione `Win + R`, digite `cmd` e pressione Enter
   - **Mac**: Pressione `Cmd + Espaço`, digite "Terminal" e pressione Enter
   - **Linux**: Pressione `Ctrl + Alt + T`

5. **Navegue até a pasta do projeto:**
   ```bash
   cd caminho/para/backend-insperjr-trainee
   ```

6. **Crie e ative o ambiente virtual:**
   ```bash
   # Criar ambiente virtual
   python -m venv venv
   
   # Ativar ambiente virtual
   # Windows:
   venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```

7. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```
   ⏳ *Aguarde terminar (pode demorar alguns minutos na primeira vez)*

8. **Configure as variáveis de ambiente:**
   - Abra o arquivo `.env`
   - Substitua `<username>` e `<password>` pela sua string de conexão do MongoDB
   - Exemplo: `mongodb+srv://seuusuario:suasenha@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority`

9. **Execute o projeto:**
   ```bash
   python src/main.py
   ```
   ou
   ```bash
   fastapi run src/main.py
   ```

10. **Abra no navegador:**
    - **API**: http://localhost:8000
    - **Documentação**: http://localhost:8000/docs
    - **ReDoc**: http://localhost:8000/redoc

### ✅ Se tudo der certo, você verá:
- No terminal: `Uvicorn running on http://0.0.0.0:8000`
- No navegador: A documentação interativa da API

### 🆘 Problemas comuns:
- **"python não é reconhecido"**: Reinstale o Python e marque "Add to PATH"
- **"pip não é reconhecido"**: Reinstale o Python (pip vem junto)
- **"porta já está em uso"**: Feche outros programas na porta 8000
- **Erro de conexão MongoDB**: Verifique a string de conexão no `.env`
- **Ambiente virtual não ativa**: Execute `source venv/bin/activate` (Mac/Linux) ou `venv\Scripts\activate` (Windows)

## 📁 Estrutura

```
src/
├── main.py          # Aplicação FastAPI principal
├── models/          # Modelos de dados (MongoDB)
└── routes/          # Endpoints da API
```

## 🛠️ Scripts

- `python src/main.py` - Executar aplicação
- `fastapi run src/main.py` - Executar com FastAPI CLI
- `pip install -r requirements.txt` - Instalar dependências

## 🔧 Tecnologias

- **FastAPI** - Framework web moderno e rápido
- **MongoDB** - Banco de dados NoSQL
- **MongoEngine** - ODM para MongoDB
- **Python 3.9+** - Linguagem de programação
- **Uvicorn** - Servidor ASGI

## 📚 Documentação

- **FastAPI**: https://fastapi.tiangolo.com/
- **MongoEngine**: https://docs.mongoengine.org/
- **MongoDB Atlas**: https://www.mongodb.com/cloud/atlas