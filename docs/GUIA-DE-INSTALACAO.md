# Guia completo de instalação e uso

Este guia leva uma pessoa que está começando do zero até a criação do primeiro card. Os comandos principais são para **Windows com PowerShell**; há comandos para macOS/Linux quando mudam. Execute os comandos na pasta do projeto, onde estão `main.py`, `pyproject.toml` e `.env.example`.

## O que o programa faz

Você informa uma palavra em inglês. O programa pede a uma API de IA frases e traduções, gera um MP3 com gTTS e envia notas de omissão de palavras ao Anki pelo complemento AnkiConnect. A importação de palavras de um banco SQLite do Kindle é opcional.

| Componente | Para que serve | É necessário? |
| --- | --- | --- |
| Anki Desktop | Guarda e apresenta os cards | Sim |
| AnkiConnect | Recebe os cards enviados pelo programa ao Anki local | Sim; é o único complemento obrigatório do Anki |
| Python 3.13 ou superior | Executa o programa e instala suas dependências | Sim |
| Chave de uma API de IA | Gera frases e traduções | Sim |
| gTTS | Gera o áudio em inglês; vem com as dependências Python do projeto | Sim, mas a instalação é automática no passo 6 |
| Banco SQLite do Kindle | Fornece palavras para importar | Não |

Você precisa de internet para instalar os programas, chamar a API de IA e gerar o áudio. Uma conta AnkiWeb é opcional para usar o Anki localmente. **AnkiConnect não exige chave de API na configuração local padrão**: a chave colocada no `.env` é a do *provedor de IA*.

## 1. Instale o Anki no computador

1. Abra o [site oficial do Anki](https://apps.ankiweb.net/) e baixe o **Anki Desktop** para seu sistema operacional. Use o aplicativo para computador, pois o programa precisa conversar com um Anki aberto na mesma máquina.
2. No Windows, execute o instalador baixado e abra o Anki. No macOS/Linux, siga as instruções de instalação mostradas no site do Anki para sua plataforma.
3. Conclua a configuração inicial do Anki e deixe sua janela aberta. Se aparecer uma solicitação de atualização, conclua-a antes de instalar o complemento.

O [manual oficial de instalação do Anki no Windows](https://docs.ankiweb.net/platform/windows/installing.html) traz detalhes adicionais caso a instalação do aplicativo falhe.

## 2. Instale o AnkiConnect (a “API do Anki”)

1. No Anki Desktop, abra **Ferramentas → Complementos** (em inglês, **Tools → Add-ons**).
2. Clique em **Obter complementos** / **Get Add-ons** ou **Browse & Install**.
3. Digite o código **`2055492159`** e confirme. É o código do [AnkiConnect](https://ankiweb.net/shared/info/2055492159).
4. Feche **e abra novamente** o Anki para carregar o complemento. Depois, mantenha o Anki aberto enquanto usa este programa.

O [guia do AnkiConnect](https://github.com/amikey/anki-connect/blob/master/README.md) documenta a instalação e o endereço local padrão `http://localhost:8765`. Para verificar a comunicação, abra o PowerShell com o Anki aberto e execute:

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8765' -Method Post -ContentType 'application/json' -Body '{"action":"version","version":6}'
```

A resposta deve conter `error` vazio (`null`) e um número em `result`. Se houver erro de conexão, confirme que o Anki está aberto, que o complemento está habilitado em **Ferramentas → Complementos** e que o Anki foi reiniciado. O programa usa a versão 6 do protocolo; se o complemento indicar que não a suporta, atualize o AnkiConnect.

## 3. Prepare o baralho e o tipo de nota no Anki

O programa usa, por padrão, o baralho **`Inglês`** e o tipo de nota **`Omissão de Palavras`**. Ele envia conteúdo para dois campos com nomes **exatos**: **`Texto`** e **`Verso Extra`**. O nome do baralho e do tipo de nota podem mudar no `.env`; os nomes dos dois campos são fixos no código.

1. Na tela principal do Anki, crie um baralho chamado `Inglês` usando **Criar baralho** / **Create Deck**. Se já tiver um baralho com outro nome, anote o nome exato para usar em `ANKI_DECK`.
2. Abra **Ferramentas → Gerenciar tipos de nota** / **Tools → Manage Note Types**. Veja se existe `Omissão de Palavras` e selecione **Campos** / **Fields** para conferir os nomes `Texto` e `Verso Extra`.
3. Se o tipo de nota não existir, adicione ou clone um tipo **Cloze / Omissão de palavras** do próprio Anki. Dê a ele um nome à sua escolha e configure os campos para que se chamem exatamente `Texto` e `Verso Extra`. Se sua interface estiver em inglês, os campos originais podem aparecer como `Text` e `Back Extra`/`Extra`: renomeie os campos na cópia criada.
4. Em **Cartões** / **Cards**, confira o modelo: a frente deve conter `{{cloze:Texto}}`. O verso deve conter `{{cloze:Texto}}` e `{{Verso Extra}}`. Se você renomeou campos e o modelo não foi atualizado automaticamente, ajuste essas referências. Salve o tipo de nota.
5. Caso tenha criado um tipo com outro nome, coloque esse nome exato em `ANKI_NOTE_MODEL` no passo 8.

**Use um tipo Cloze como base**, pois o programa envia trechos no formato `{{c1::frase}}`. Um tipo de nota Básico não gera corretamente esse card. O [manual do Anki sobre tipos de nota e campos](https://docs.ankiweb.net/editing.html#adding-a-note-type) e o [manual de modelos Cloze](https://docs.ankiweb.net/templates/generation.html#cloze) mostram onde ajustar esses itens.

## 4. Instale Python 3.13 ou superior

Baixe o Python no [site oficial](https://www.python.org/downloads/) e instale uma versão **3.13 ou superior**. No Windows, confirme que o Python Launcher (`py`) está disponível; se o instalador oferecer a opção de adicionar Python ao `PATH`, marque-a. Feche e reabra o terminal após a instalação.

No PowerShell, confira a versão:

```powershell
py -3.13 --version
```

Se você instalou uma versão superior e esse comando não a encontrar, use `py --version` ou `python --version`. Em macOS/Linux, use `python3 --version`. O número mostrado precisa ser **3.13 ou superior**. Nos comandos seguintes, substitua `py -3.13` pelo comando que apontar para a versão correta, se necessário.

## 5. Obtenha o projeto e abra a pasta certa

Se você já recebeu a pasta do projeto, abra-a no Explorador de Arquivos, clique na barra de endereço, digite `powershell` e pressione Enter. Confirme que `main.py` está nessa pasta:

```powershell
Get-ChildItem main.py, pyproject.toml, .env.example
```

Se ainda não tem a pasta, baixe o ZIP do [repositório no GitHub](https://github.com/Henrique20o/kindle-to-anki-automation), extraia-o e abra a pasta extraída que contém `main.py`. Se já usa Git, pode cloná-lo pelo terminal:

```powershell
git clone https://github.com/Henrique20o/kindle-to-anki-automation.git
Set-Location .\kindle-to-anki-automation
```

Para macOS/Linux, entre na pasta equivalente com `cd caminho/da/pasta`. Os comandos dos próximos passos assumem que o terminal já está nessa pasta.

## 6. Crie o ambiente Python e instale as dependências

No **PowerShell**, dentro da pasta do projeto:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
```

Se o passo 4 apontou outra versão do Python, use o mesmo comando na primeira linha. A segunda linha usa diretamente o Python do ambiente do projeto, então **não é necessário ativar o ambiente** nem alterar a política de execução do PowerShell. A instalação baixa as bibliotecas `openai`, `requests`, `gTTS` e `python-dotenv` declaradas em `pyproject.toml`.

Em **macOS/Linux**:

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -e .
```

Se a criação do ambiente reclamar de `venv` ou `pip`, instale esses componentes para sua distribuição do Python e repita o passo. Aguarde o `pip` terminar sem erro antes de prosseguir.

## 7. Obtenha uma chave da API de IA

### Opção A: OpenAI

1. Acesse o [painel de chaves da API da OpenAI](https://platform.openai.com/api-keys) e entre ou crie uma conta.
2. Crie uma nova chave de API e copie-a no momento em que ela for exibida. Guarde-a para o próximo passo.
3. Verifique as condições de cobrança e limites no [painel de faturamento da API](https://platform.openai.com/account/billing/overview). As chamadas feitas pelo programa podem gerar custo. A [documentação oficial de início da API](https://developers.openai.com/api/docs/quickstart) explica a criação e o uso de chaves.

### Opção B: outro provedor

No painel do provedor escolhido, crie uma chave de API e encontre **o nome do modelo** e **a URL base da API**. Esta versão do programa usa a interface **OpenAI Chat Completions**; o outro provedor precisa oferecer uma API compatível. Uma API com formato próprio requer alteração no código. O gTTS usa um serviço online separado e **não** usa essa chave.

## 8. Configure o arquivo `.env`

No PowerShell, ainda na pasta do projeto:

```powershell
Copy-Item .env.example .env
notepad .env
```

Em macOS/Linux:

```bash
cp .env.example .env
```

Abra `.env` no editor de sua preferência. Troque **somente** o valor de exemplo `sua_chave_aqui` por sua chave verdadeira. Para **OpenAI**, o início do arquivo pode ficar assim (o texto abaixo é ilustrativo; não é uma chave válida):

```dotenv
AI_API_KEY=COLE_SUA_CHAVE_REAL_AQUI
CARD_DIFFICULTY=equilibrado
CARD_COUNT=2
ANKI_DECK=Inglês
ANKI_NOTE_MODEL=Omissão de Palavras
ANKI_URL=http://localhost:8765
```

Com OpenAI, `AI_MODEL` pode ficar comentado: o padrão do programa é `gpt-4o-mini`. Se escolher outro modelo ao qual sua conta tem acesso, remova o `#` da linha `AI_MODEL` e coloque o nome correto.

Para **outro provedor compatível**, informe também os valores fornecidos por ele:

```dotenv
AI_API_KEY=COLE_SUA_CHAVE_REAL_AQUI
AI_MODEL=nome-do-modelo-do-provedor
AI_BASE_URL=https://endereco-do-provedor.example/v1
```

O endereço acima é um exemplo, **não** uma URL operacional. `AI_MODEL` é obrigatório quando `AI_BASE_URL` está configurado. Em ambos os casos, confira:

- `ANKI_DECK`: nome exato do baralho preparado no passo 3.
- `ANKI_NOTE_MODEL`: nome exato do tipo Cloze preparado no passo 3.
- `ANKI_URL`: deixe `http://localhost:8765` se não mudou a configuração local do AnkiConnect.
- `CARD_DIFFICULTY`: `facil` (A2/B1), `equilibrado` (B1/B2) ou `avancado` (B2/C1).
- `CARD_COUNT`: `1`, `2` ou `3` cards por palavra.

Salve o arquivo. O `.env` é ignorado pelo Git; não publique sua chave nem a coloque em capturas de tela. Se variáveis de sistema com esses nomes já estiverem definidas, **elas prevalecem sobre o `.env`**. A variável antiga `OPENAI_API_KEY` também é aceita quando `AI_API_KEY` não estiver definida.

## 9. Entenda a configuração do áudio

Não há uma instalação separada de “questões de áudio”. O `pip install -e .` do passo 6 instala **gTTS**. A cada frase, o programa usa esse serviço para gerar um MP3 em inglês, envia o arquivo ao AnkiConnect e apaga a cópia temporária local após a tentativa de envio. O Anki gerencia o áudio recebido como mídia do card. **Nenhum outro complemento do Anki, microfone, FFmpeg ou chave de áudio é exigido por esta versão.**

A geração do áudio precisa de internet. Se falhar, confira a conexão e tente de novo. A [documentação do gTTS](https://gtts.readthedocs.io/en/latest/) descreve a geração de MP3, e o [manual de mídia do Anki](https://docs.ankiweb.net/media.html) explica como o Anki guarda e reproduz mídia.

## 10. Faça o primeiro teste completo

1. Abra o **Anki Desktop** e deixe-o aberto.
2. No PowerShell, na pasta do projeto, execute:

   ```powershell
   .\.venv\Scripts\python.exe main.py
   ```

   Em macOS/Linux: `./.venv/bin/python main.py`.
3. Quando aparecer `Palavra:`, digite `config` para conferir a dificuldade e a quantidade de cards. Para um teste pequeno, escolha **2) Quantidade de cards → 1**. A alteração é salva no `.env` e já vale para a próxima palavra. Depois escolha **3) Voltar**.
4. Digite uma palavra em inglês, por exemplo `apple`, e pressione Enter. Você também pode informar um significado específico sem espaço antes dos parênteses, como `match(fósforo)`.
5. Espere a geração da frase, do áudio e o envio ao Anki. Uma mensagem `Finalizado para 'apple'` indica que todos os cards esperados para essa palavra foram enviados e registrados.
6. No Anki, abra o baralho escolhido, localize a nota e confirme que a frase de omissão, a tradução e o áudio estão presentes. Se mudar o número de cards, esse valor vale **por palavra**.
7. Digite `sair` para encerrar o programa.

O primeiro teste chama serviços online e pode consumir créditos da API de IA. Se a palavra já estiver em `words.json`, o programa avisará que ela foi processada; escolha outra palavra para testar. Os níveis de dificuldade orientam a geração das frases, mas não são avaliados automaticamente.

## 11. Uso no dia a dia

Sempre abra o Anki primeiro. Depois, na pasta do projeto, execute `.\.venv\Scripts\python.exe main.py` no Windows ou `./.venv/bin/python main.py` em macOS/Linux. No prompt `Palavra:`:

| Digite | Resultado |
| --- | --- |
| `apple` | Gera cards para uma palavra |
| `match(fósforo)` | Informa também o significado desejado, sem espaço antes de `(` |
| `config` | Abre o menu para trocar dificuldade e quantidade de cards; salva no `.env` |
| `lote` ou `batch` | Pede várias palavras numa linha, separadas por espaço, vírgula, `;` ou `\|` |
| `kindle` | Pede o caminho de um banco SQLite do Kindle e um limite opcional de palavras |
| `sair` | Encerra o programa |

Exemplo para `lote`: `apple, book, match(fósforo)`. Para o formato com significado, **não** digite `match (fósforo)`; essa entrada é rejeitada. O menu `config` altera somente `CARD_DIFFICULTY` e `CARD_COUNT`, nunca sua chave de API. Se uma dessas configurações estiver definida como variável do sistema, o menu avisará que não pode alterá-la até essa variável ser removida.

O arquivo `words.json` registra palavras concluídas para evitar processamento repetido. Se apenas parte dos cards de uma palavra for criada, ela **não** é registrada como concluída; confira o baralho antes de repetir, pois a nova tentativa pode criar cards duplicados.

### Importação opcional do Kindle

Este recurso usa um **arquivo SQLite `.db` já disponível no computador**. Ele não baixa dados automaticamente de sua conta Kindle. Se tiver o arquivo, digite `kindle` no programa e informe seu caminho completo quando solicitado. No Windows, por exemplo: `C:\Users\SeuNome\Documents\vocab.db`. Deixe o limite em branco para tentar todas as palavras encontradas ou informe um número positivo para um teste menor.

Para guardar o caminho como padrão, acrescente ao `.env` uma linha como `KINDLE_DB_PATH=C:/Users/SeuNome/Documents/vocab.db`; depois reinicie o programa. Ao digitar `kindle`, pressione Enter no prompt do caminho para usar esse padrão. O leitor procura colunas de palavras e, quando existe uma coluna de idioma, filtra inglês. Bancos com estrutura diferente podem não produzir palavras.

## 12. Se algo não funcionar

| Sintoma | O que verificar |
| --- | --- |
| `py`/`python` não encontrado ou versão abaixo de 3.13 | Instale Python 3.13+; reabra o terminal; use o comando que mostrou a versão correta no passo 4. |
| Erro em `pip install -e .` | Confirme que está na pasta com `pyproject.toml`, que o ambiente `.venv` foi criado e que há acesso à internet. Repita a instalação com o Python dentro de `.venv`. |
| `Configure AI_API_KEY` ou `Configuração inválida` | Confira se `.env` está na pasta de `main.py`, se a chave foi substituída e se dificuldade/quantidade têm valores aceitos. |
| Erro de autenticação da IA (`401`) | Confira a chave e o provedor. Para outro provedor, confira também `AI_BASE_URL` e `AI_MODEL`. |
| Limite, cota ou faturamento da IA (`429` ou similar) | Consulte os limites e o faturamento no painel do provedor; a [documentação de erros da OpenAI](https://developers.openai.com/api/docs/guides/error-codes) explica esses códigos para OpenAI. |
| Falha de conexão com `localhost:8765` | Abra o Anki, habilite/atualize o AnkiConnect, reinicie o Anki e refaça o teste do passo 2. |
| `deck was not found`, `model was not found` ou erro de campo | Confira grafia e acentos de `ANKI_DECK`, `ANKI_NOTE_MODEL`, `Texto` e `Verso Extra`. O tipo precisa ser Cloze e o modelo precisa usar esses campos. |
| Erro ao gerar áudio ou card sem som | Confira a internet, instale as dependências do passo 6 e inspecione o campo `Texto` e a mídia da nota no Anki. |
| Palavra já processada ou card duplicado | Consulte `words.json` e o baralho. Após uma falha parcial, confira os cards existentes antes de tentar novamente. |
| Kindle: arquivo não encontrado ou nenhuma palavra | Confira o caminho do `.db`; o banco precisa ter colunas reconhecidas de palavras. Teste primeiro com a entrada manual. |

## Checklist final

- [ ] Anki Desktop instalado, aberto e com o baralho correto.
- [ ] AnkiConnect instalado pelo código `2055492159`, habilitado e respondendo ao teste local.
- [ ] Tipo de nota Cloze com campos exatos `Texto` e `Verso Extra` e modelo com `{{cloze:Texto}}`.
- [ ] Python 3.13+ e dependências instaladas no `.venv` do projeto.
- [ ] `.env` salvo com chave de IA válida e nomes do baralho/tipo de nota corretos.
- [ ] Uma palavra de teste gerou card, tradução e áudio no Anki.

Depois desses passos, basta manter o Anki aberto e iniciar o programa pelo comando do passo 10 sempre que quiser criar novos cards.
