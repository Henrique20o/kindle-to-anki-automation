# Kindle to Anki Automation

Cria cards no Anki a partir de palavras em inglês. A aplicação gera frases e traduções com IA, áudio em inglês com gTTS e pode importar palavras de um banco SQLite do Kindle.

**Começando do zero?** Siga o [guia completo de instalação e uso](docs/GUIA-DE-INSTALACAO.md), com Anki, AnkiConnect, chave de API, áudio, configuração e primeiro teste.

## Pré-requisitos

- Python 3.13 ou superior.
- Anki aberto com o complemento **AnkiConnect** instalado.
- Um tipo de nota no Anki com os campos `Texto` e `Verso Extra`. Os nomes padrão são baralho `Inglês` e tipo de nota `Omissão de Palavras`; ajuste esses nomes no `.env` se usar outros.
- Uma chave de API de IA. Para outros provedores, a API precisa ser compatível com **OpenAI Chat Completions**.

## Instalação

No PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
Copy-Item .env.example .env
```

Em macOS/Linux, ative o ambiente com `source .venv/bin/activate` e copie o arquivo com `cp .env.example .env`.

Edite `.env` e substitua `sua_chave_aqui` pela sua chave. O arquivo `.env` é ignorado pelo Git. Variáveis já definidas no ambiente prevalecem sobre ele. A variável antiga `OPENAI_API_KEY` também é aceita como alternativa a `AI_API_KEY`.

Execute:

```powershell
python main.py
```

## Configuração

| Variável | Padrão | Descrição |
| --- | --- | --- |
| `AI_API_KEY` | obrigatória | Chave da API de IA |
| `AI_MODEL` | `gpt-4o-mini` com OpenAI | Modelo; obrigatório ao configurar outra URL |
| `AI_BASE_URL` | URL padrão da OpenAI | URL base de outra API compatível com Chat Completions |
| `CARD_DIFFICULTY` | `equilibrado` | `facil` (A2/B1), `equilibrado` (B1/B2) ou `avancado` (B2/C1) |
| `CARD_COUNT` | `2` | `1`, `2` ou `3` cards por palavra |
| `ANKI_DECK` | `Inglês` | Nome do baralho |
| `ANKI_NOTE_MODEL` | `Omissão de Palavras` | Tipo de nota com campos `Texto` e `Verso Extra` |
| `ANKI_URL` | `http://localhost:8765` | Endereço do AnkiConnect |
| `KINDLE_DB_PATH` | vazio | Caminho opcional para o banco Kindle |

Para usar outro provedor, configure `AI_API_KEY`, `AI_MODEL` e `AI_BASE_URL` com os valores informados por ele. Esta versão usa a interface **OpenAI Chat Completions**; APIs com formato próprio exigem um adaptador. O gTTS usa um serviço online separado e não usa a chave de IA. Os níveis de dificuldade orientam o prompt, mas não são medidos automaticamente.

## Comandos no terminal

- Digite uma palavra, como `match(fósforo)`, para criar os cards.
- Digite `lote` ou `batch` para informar palavras em **uma linha**, separadas por espaço, vírgula, `;` ou `|`.
- Digite `kindle` para informar o caminho de um arquivo SQLite; Enter usa `KINDLE_DB_PATH`, se configurado.
- Digite `config` para abrir um menu numérico e alterar a dificuldade ou a quantidade de cards. A escolha vale para a próxima palavra e fica salva no `.env` para as próximas execuções.
- Digite `sair` para encerrar.

Por exemplo: digite `config`, escolha `1) Dificuldade` e depois `3) Avancado`. Para usar apenas um card por palavra, escolha `2) Quantidade de cards` e depois `1`. Enter no submenu cancela a escolha; `3) Voltar` retorna ao prompt de palavras.

Se `CARD_DIFFICULTY` ou `CARD_COUNT` estiver definida como variável do sistema, ela tem prioridade sobre o `.env`. Nesse caso, o menu informa como liberar a opção antes de alterá-la. O menu não mostra nem edita chaves de API.

No lote, escreva o significado junto à palavra: `match(fósforo)`. Entradas como `match (fósforo)` são avisadas e ignoradas por inteiro.

O arquivo local `words.json` registra palavras concluídas para evitar repetição. Os áudios são temporários. Se alguns cards forem criados e outros falharem, a palavra não é marcada como concluída; confira os cards no Anki antes de tentar novamente, pois uma nova tentativa pode criar cards adicionais.

O plano e os critérios de aceite desta refatoração estão em [docs/SDD-refatoracao.md](docs/SDD-refatoracao.md).
