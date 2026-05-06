# Kindle to Anki Automation

Repositório referente a uma aplicação em Python responsável por **gerar cards completos do Anki a partir de palavras em inglês**.
A aplicação cria frases com IA, gera áudio em inglês, envia o conteúdo para o Anki via AnkiConnect e ainda permite importar palavras de um banco SQLite do Kindle.
O projeto foi desenvolvido para estudo, automação e testes, com foco em praticidade no uso diário.

---

## Sumário

- [Instruções para execução do sistema](#instruções-para-execução-do-sistema)
- [Tecnologias e ferramentas utilizadas](#tecnologias-e-ferramentas-utilizadas)
- [Arquitetura do projeto](#arquitetura-do-projeto)
- [Fluxo de funcionamento](#fluxo-de-funcionamento)
- [Observações importantes](#observações-importantes)

---

## Instruções para execução do sistema

### Pré-requisitos

- Python 3.13 ou superior
- Anki aberto com o **AnkiConnect** instalado
- Chave da OpenAI configurada na variável de ambiente `OPENAI_API_KEY`

### Instalação das dependências

```bash
pip install openai requests gtts
```

### Configuração da chave da OpenAI

No PowerShell:

```powershell
$env:OPENAI_API_KEY="sua_chave_aqui"
```

### Execução da aplicação

```bash
python main.py
```

### Uso no terminal

- Digite uma palavra para gerar os cards normalmente
- Digite `kindle` para importar palavras de um arquivo SQLite do Kindle
- Digite `sair` para encerrar a aplicação

---

## Tecnologias e ferramentas utilizadas

- **Linguagem**: Python
- **IA**: OpenAI API
- **Texto para fala**: gTTS
- **Integração com Anki**: AnkiConnect
- **Banco de dados**: SQLite
- **Requisições HTTP**: requests

---

## Arquitetura do projeto

### Estrutura principal

- `main.py` - controla o fluxo da aplicação
- `services/ai_service.py` - gera frases com IA
- `services/tts_service.py` - cria o áudio em inglês
- `services/anki_service.py` - envia os cards para o Anki
- `services/kindle_service.py` - lê palavras do banco SQLite do Kindle
- `services/word_service.py` - salva as palavras já processadas

### Fluxo da aplicação

1. O usuário informa uma palavra ou um banco do Kindle
2. O sistema gera frases em inglês e tradução em português
3. O áudio da frase é criado automaticamente
4. O card é enviado para o Anki
5. A palavra é salva para evitar duplicidade

### Estrutura de dados local

- `words.json` - armazena as palavras já processadas
- `audio/` - guarda os áudios gerados durante a execução

---

## Fluxo de funcionamento

### Geração manual

1. Digite uma palavra no terminal
2. A IA gera duas frases
3. O sistema cria o áudio
4. O card é enviado ao Anki

### Importação do Kindle

1. Digite `kindle`
2. Informe o caminho do arquivo `.db`
3. O sistema extrai as palavras válidas
4. Cada palavra passa pelo mesmo processo de geração de card

---

## Observações importantes

- O Anki precisa estar aberto com o AnkiConnect ativo
- A chave da OpenAI não deve ser compartilhada
- O arquivo `words.json` evita repetir palavras já processadas
- A pasta `audio/` recebe arquivos temporários gerados pela aplicação

---
