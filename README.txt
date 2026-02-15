================================================================================
Cara Core MKT — Oficina (software em Python)
================================================================================
O Seed e o MKT são da Cara Core; não vendemos.

PREMISSA (eficência operacional)
  A estratégia é pública porque o diferencial não é o plano, é a execução.
  Ninguém paga boleto por caridade e ninguém trabalha de graça. Ter a ideia é
  fácil; rodar o tráfego, tratar o lead e otimizar o funil todo dia é o que
  ninguém quer fazer. O software existe para automatizar o trabalho que humanos
  negligenciam por preguiça ou cansaço. Validação CTO (automação, saída
  acionável, custo, escalabilidade): CTO_VALIDACAO_MKT.txt.

Oficina da Sala de Notícias: scripts para iniciar trabalho, validar, transportar
e validar entrega em face, gram e retro. Produto Cara Core MKT (uso interno).

PYTHON BASELINE — Microsoft Store
  Use a versão correta do Python instalada pela Microsoft Store (baseline).
  Assim o comportamento é o mesmo em todos os ambientes.
  Verificar: py --version  ou  python --version

ESTRUTURA DO PROJETO (D:\dev\caracore-mkt)
  caracore-mkt/
    README.txt           — este arquivo
    requirements.txt    — dependências (stdlib apenas, ou mínimas)
    caracore_mkt/       — pacote Python
      __init__.py
      config.py         — caminhos (sala, repo, face, gram, retro)
      planilha.py       — leitura/escrita da planilha da sala
      mensagens.py      — mensagens amigáveis (WhatsApp, Telegram, e-mail)
      validar.py        — validação face, gram, retro
    scripts/            — pontos de entrada (6 scripts)
      iniciar_trabalho.py
      validar_trabalho_executado.py
      validar_sala.py
      transportar_para_salas.py
      validar_entrega_face.py
      validar_entrega_gram.py
      validar_entrega_retro.py

ONDE FICA A SALA (HTML, planilha, regis)
  Por padrão a oficina procura o repositório do site como pasta irmã:
    D:\dev\caracore-mkt\   ← oficina (este projeto Python)
    D:\dev\caracore-site\  ← repositório (contém sala/, face/, gram/, retro/)
  Caminhos configuráveis por variáveis de ambiente:
    CARACORE_REPO = caminho para a raiz do repo (ex.: D:\dev\caracore-site)
    CARACORE_SALA = caminho da pasta sala (padrão: CARACORE_REPO\sala)
  Assim a oficina e o conteúdo da sala podem estar em pastas diferentes.

COMO RODAR
  Na pasta D:\dev\caracore-mkt (ou com CARACORE_REPO e CARACORE_SALA definidos):

  py -3 scripts\iniciar_trabalho.py
  py -3 scripts\validar_trabalho_executado.py
  py -3 scripts\validar_sala.py
  py -3 scripts\transportar_para_salas.py
  py -3 scripts\validar_entrega_face.py
  py -3 scripts\validar_entrega_gram.py
  py -3 scripts\validar_entrega_retro.py

  Ou: python scripts/iniciar_trabalho.py  (conforme o Python baseline).

Cara Core Informática · Produto Cara Core MKT (não vendemos)
