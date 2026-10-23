# SDD — Refatoração para uso local

**Status:** refatoração e comando `config` implementados; integração real com Anki e provedor de IA pendente de verificação manual
**Data:** 22/10/2026
**Escopo:** configuração, geração de cards, envio ao Anki e experiência de instalação

## 1. Contexto e objetivo

O projeto transforma palavras em inglês em notas do Anki com frases, traduções e áudio. Hoje, valores necessários para executar o programa estão espalhados ou fixos no código: provedor e modelo de IA, caminho do banco Kindle, baralho e tipo de nota do Anki. As dependências também não constam em `pyproject.toml`.

O objetivo desta refatoração é permitir que uma pessoa clone o projeto, configure seus dados localmente e use os fluxos existentes de palavra única, lote e Kindle sem editar arquivos Python. A organização deve continuar pequena: configuração centralizada, serviços com responsabilidades claras e `main.py` coordenando a interface de terminal.

## 2. Requisitos funcionais

### RF-01 — Configuração local

- A aplicação deve ler variáveis de ambiente e, opcionalmente, um arquivo `.env` na raiz do projeto.
- Variáveis do ambiente devem prevalecer sobre valores do `.env`.
- O repositório deve conter `.env.example`, sem chaves reais; `.env` deve continuar ignorado pelo Git.
- Configurações inválidas devem produzir mensagem clara antes de começar a gerar cards.
- O cliente de IA deve ser criado após a leitura da configuração, não durante a importação do módulo.

| Variável | Padrão | Regra |
| --- | --- | --- |
| `AI_API_KEY` | nenhum | Obrigatória; aceitar `OPENAI_API_KEY` como alternativa legada |
| `AI_MODEL` | `gpt-4o-mini` para a URL padrão | Obrigatória quando `AI_BASE_URL` for definida |
| `AI_BASE_URL` | URL padrão do cliente OpenAI | URL base de API compatível com Chat Completions |
| `CARD_DIFFICULTY` | `equilibrado` | `facil`, `equilibrado` ou `avancado` |
| `CARD_COUNT` | `2` | Inteiro `1`, `2` ou `3` |
| `ANKI_DECK` | `Inglês` | Nome do baralho |
| `ANKI_NOTE_MODEL` | `Omissão de Palavras` | Tipo de nota do Anki |
| `ANKI_URL` | `http://localhost:8765` | URL do AnkiConnect |
| `KINDLE_DB_PATH` | vazio | Caminho opcional sugerido para importação |

O tipo de nota deve ter os campos `Texto` e `Verso Extra`. Tornar os nomes desses campos configuráveis está fora do escopo desta etapa.

### RF-02 — Provedor de IA

- A integração deve aceitar chave, modelo e URL base de um provedor que implemente a API **OpenAI Chat Completions**.
- A ausência de `AI_BASE_URL` deve usar a OpenAI, mantendo o comportamento atual.
- A aplicação não deve prometer suporte a APIs com protocolo próprio. Para elas, será necessário um adaptador posterior.
- Falhas de autenticação, rede ou formato da resposta devem ser mostradas como erro da palavra atual, sem encerrar todo o lote.

### RF-03 — Presets de geração

| Dificuldade | Níveis orientativos no prompt |
| --- | --- |
| `facil` | A2/B1 |
| `equilibrado` | B1/B2 |
| `avancado` | B2/C1 |

- O prompt deve pedir exatamente `CARD_COUNT` frases, cada uma com tradução em português brasileiro.
- Cada frase deve gerar um card, preservando o formato atual de nota cloze e áudio.
- A resposta deve ser validada antes de enviar qualquer card: JSON válido, lista com a quantidade solicitada, `sentence` e `translation` como textos não vazios.
- O significado entre parênteses, como `match(fósforo)`, deve continuar orientando a geração.
- Os níveis são orientações para a IA, não uma classificação automática garantida.

### RF-04 — Envio e registro

- O serviço do Anki deve verificar o HTTP e o campo `error` da resposta do AnkiConnect. Só uma resposta com ID de nota válido conta como card criado.
- Áudios temporários devem ser removidos após cada tentativa de envio, inclusive quando ocorrer erro.
- A palavra só deve entrar em `words.json` quando todos os cards solicitados forem criados.
- Se parte dos cards for criada, o programa deve informar `criados/solicitados` e alertar que uma nova tentativa pode criar cards adicionais. O usuário pode conferi-los no Anki antes de repetir.
- O processamento em lote deve continuar nas palavras seguintes após uma falha isolada.

### RF-05 — Entrada e Kindle

- Palavra única, `lote`/`batch`, `kindle` e `sair` devem continuar disponíveis.
- O comando `kindle` deve pedir o caminho do `.db`; Enter usa `KINDLE_DB_PATH` quando configurado. Não deve existir caminho pessoal fixo no código.
- No lote, entradas com espaço antes dos parênteses, como `match (fósforo)`, devem ser avisadas e ignoradas integralmente, sem processar `match` separadamente.
- A interface deve descrever apenas separadores que realmente aceita. Como `input()` lê uma linha, entrada multilinha não será anunciada nesta etapa.

### RF-06 — Alterar presets pelo terminal

- O comando `config`, digitado no prompt `Palavra:`, deve abrir um menu com os valores atuais de dificuldade e quantidade de cards.
- O menu deve oferecer `1) Dificuldade`, `2) Quantidade de cards` e `3) Voltar`. A escolha de dificuldade deve mostrar `1) Fácil (A2/B1)`, `2) Equilibrado (B1/B2)` e `3) Avançado (B2/C1)`. A quantidade deve aceitar `1`, `2` ou `3`.
- Uma escolha válida deve passar a valer para a próxima palavra processada na mesma execução e ser salva em `.env` para execuções futuras. O menu deve confirmar o novo valor sem exigir reinício.
- Ao salvar, somente `CARD_DIFFICULTY` ou `CARD_COUNT` deve ser alterada. Chaves de API, demais variáveis e comentários do `.env` devem ser preservados. Se não houver `.env`, criar um arquivo local apenas com o valor alterado.
- Entrada inválida ou cancelamento deve voltar ao menu sem alterar a configuração. Falha ao gravar o arquivo deve ser mostrada e não deve aplicar a mudança em memória.
- Variáveis de ambiente do sistema continuam tendo prioridade sobre `.env`. Se a opção escolhida estiver definida no ambiente do processo antes da leitura do `.env`, o menu deve explicar essa prioridade e não deve gravar uma mudança que seria ignorada na próxima execução.
- O menu não deve exibir nem editar chave de API, modelo, URL ou dados do Anki. O comando `config` passa a ser reservado e deixa de ser interpretado como palavra.

## 3. Requisitos não funcionais

- Instalação reproduzível com dependências declaradas em `pyproject.toml` e instruções no README.
- Nenhuma chave, caminho pessoal ou dado de usuário deve ser incluído nos arquivos versionados.
- Mensagens de erro devem indicar qual etapa falhou (configuração, IA, áudio, Anki ou Kindle), sem imprimir a chave de API.
- A refatoração deve preservar as alterações locais já existentes, incluindo o comando de lote, as regras atuais do prompt e as tentativas de geração de áudio.

## 4. Organização proposta

| Arquivo | Responsabilidade após a refatoração |
| --- | --- |
| `config.py` | Ler e validar configuração; definir presets |
| `main.py` | Ler comandos, coordenar uma palavra ou lote, abrir o menu `config` e mostrar resultados |
| `services/ai_service.py` | Montar prompt, chamar a API e validar frases |
| `services/anki_service.py` | Montar nota, enviar e validar resposta do AnkiConnect |
| `services/tts_service.py` | Gerar áudio; manter tentativas e limpar arquivo temporário de falhas |
| `services/kindle_service.py` | Ler palavras do SQLite, sem conhecer a interface de terminal |
| `services/word_service.py` | Consultar e registrar palavras concluídas |

Não serão criadas interfaces abstratas, hierarquias de provedores, banco novo ou framework de linha de comando. A configuração pode ser passada como um objeto simples às funções que precisam dela.

## 5. Sequência de implementação

1. Declarar dependências e adicionar `.env.example` e carregamento validado da configuração.
2. Passar a configuração ao serviço de IA; aplicar presets e validar a resposta completa.
3. Passar a configuração ao serviço do Anki; verificar confirmação de cada card.
4. Ajustar a coordenação em `main.py`, a limpeza dos áudios e o caminho do Kindle.
5. Corrigir o parser do lote e alinhar suas mensagens ao comportamento real.
6. Atualizar o README com instalação, configuração, comandos e limitações de compatibilidade.

### Implementação de RF-06

1. Ajustar `config.py` para distinguir valores definidos no ambiente do processo dos valores lidos do `.env`, mantendo a precedência atual. Concentrar ali a gravação validada dos dois presets.
2. Adicionar em `main.py` um menu pequeno para o comando `config`. Após uma gravação bem-sucedida, atualizar o objeto de configuração da sessão e voltar ao prompt `Palavra:`.
3. Atualizar o README com o comando e um exemplo de escolha, sem mudar o procedimento de configuração das APIs.
4. Testar menu, persistência, aplicação imediata, cancelamento, erro de gravação e prioridade das variáveis do sistema. Executar novamente os testes existentes e um teste manual do terminal.

## 6. Verificação e critérios de aceite

| Cenário | Resultado esperado |
| --- | --- |
| Instalação em ambiente limpo | Dependências instaladas a partir do projeto; execução sem editar Python |
| Configuração ausente ou inválida | Mensagem objetiva antes da primeira chamada externa |
| Outro endpoint compatível | Chave, modelo e URL base usados na chamada; nenhuma dependência de chave OpenAI |
| Cada preset de dificuldade e quantidade | Prompt contém os valores escolhidos; resposta de tamanho diferente é rejeitada |
| JSON incompleto da IA | Nenhum card enviado; palavra não registrada |
| AnkiConnect retorna `error` ou falha HTTP | Card não contado como sucesso; áudio temporário removido |
| Falha após envio parcial | Resumo mostra quantidade criada; palavra não registrada; lote continua |
| Kindle sem caminho padrão | Programa solicita caminho ao usuário |
| Lote com `match (fósforo)` | Entrada inteira rejeitada e avisada; `match` não é processada |
| Palavra já registrada | Nenhum novo card enviado |

### Critérios de aceite adicionais para RF-06

| Cenário | Resultado esperado |
| --- | --- |
| `config` → dificuldade → `3` | Próxima palavra usa `avancado`; `.env` contém `CARD_DIFFICULTY=avancado` |
| `config` → quantidade → `1` | Próxima palavra gera 1 card; `.env` contém `CARD_COUNT=1` |
| Reiniciar o programa | Valores salvos no menu continuam ativos |
| `.env` com chave, outras opções e comentários | Somente a opção escolhida muda; demais linhas permanecem intactas |
| `.env` ausente e chave fornecida pelo sistema | Arquivo `.env` é criado com o preset escolhido |
| Opção inválida, cancelamento ou erro de gravação | Configuração em memória e arquivo permanecem sem alteração |
| `CARD_COUNT` ou `CARD_DIFFICULTY` definido no sistema | Menu informa a prioridade da variável externa e não grava valor ineficaz |

Os testes automatizados devem usar respostas simuladas da IA e do AnkiConnect para os cenários de validação e erro. Um teste manual com Anki aberto confirma a integração completa; não deve fazer parte da suíte automática.

## 7. Fora do escopo

- Suporte nativo a provedores com formatos de API diferentes de Chat Completions.
- Retomada automática de uma palavra após envio parcial.
- Mudança do formato de `words.json` ou migração dos dados existentes.
- Interface gráfica, publicação de pacote ou execução em servidor.
- Otimização de lotes grandes e leitura incremental do banco Kindle, salvo se a verificação revelar problema concreto.
- Edição de chave de API, provedor, modelo e dados do Anki pelo menu `config`.
