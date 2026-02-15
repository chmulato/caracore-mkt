#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cara Core MKT — Script 1: Iniciar o trabalho do dia.
Python Baseline (Microsoft Store). Atualiza a planilha e abre a sala no navegador.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Raiz do projeto caracore-mkt
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from caracore_mkt.config import PLANILHA_HEADER
from caracore_mkt.planilha import (
    agora_iso,
    escrever_planilha,
    hoje,
    ler_linhas_planilha,
    ler_trabalho_do_dia,
    ultimo_acumulado_cc,
)
from caracore_mkt.mensagens import mensagem_amigavel_erro
from caracore_mkt.util import abrir_sala_no_navegador


def main() -> int:
    script_nome = "iniciar_trabalho.py (Script 1 — Iniciar trabalho)"
    try:
        tarefa = ler_trabalho_do_dia()
        horas_previstas = "1"
        acumulado = ultimo_acumulado_cc()

        linhas = ler_linhas_planilha()
        nova_linha = {k: "" for k in PLANILHA_HEADER}
        nova_linha["data"] = hoje()
        nova_linha["tarefa_do_dia"] = tarefa
        nova_linha["horas_previstas"] = horas_previstas
        nova_linha["acumulado_cc"] = str(acumulado).replace(".", ",")
        nova_linha["inicio_sessao"] = agora_iso()
        linhas.append(nova_linha)
        escrever_planilha(linhas)

        abrir_sala_no_navegador()

        print("=" * 60)
        print("SALA DE NOTÍCIAS — Início do trabalho registrado")
        print("=" * 60)
        print()
        print("Trabalho do dia:")
        print("  ", tarefa[:200] + "..." if len(tarefa) > 200 else "  " + tarefa)
        print()
        print("Horas a executar (previstas):", horas_previstas)
        print("Início da sessão:", nova_linha["inicio_sessao"])
        print("Acumulado CC até agora:", acumulado)
        print()
        print("A planilha foi atualizada. A sala foi aberta no navegador.")
        print("Ao terminar, use o script que valida e encerra o trabalho.")
        print("=" * 60)
        return 0

    except FileNotFoundError as e:
        print(mensagem_amigavel_erro("Arquivo não encontrado.", str(e), script_nome), file=sys.stderr)
        return 1
    except PermissionError as e:
        print(mensagem_amigavel_erro("Sem permissão para escrever na planilha ou abrir a pasta.", str(e), script_nome), file=sys.stderr)
        return 1
    except Exception as e:
        print(mensagem_amigavel_erro("Algo inesperado aconteceu ao iniciar o trabalho.", str(e), script_nome), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
