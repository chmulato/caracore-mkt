#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cara Core MKT — Script 2: Validar o trabalho executado e encerrar sessão.
Python Baseline (Microsoft Store). Atualiza a planilha com trabalho feito, horas, valor CC.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from caracore_mkt.config import PLANILHA_HEADER
from caracore_mkt.planilha import (
    agora_iso,
    escrever_planilha,
    ler_linhas_planilha,
    ler_valor_hora_cc,
    ultimo_acumulado_cc,
)
from caracore_mkt.mensagens import mensagem_amigavel_erro, mensagem_amigavel_ok
from caracore_mkt.validar import run_validar_sala

SCRIPT_NOME = "validar_trabalho_executado.py (Script 2 — Validar e encerrar)"


def main() -> int:
    try:
        print("=" * 60)
        print("SALA DE NOTÍCIAS — Validar trabalho executado")
        print("=" * 60)
        print()
        print("Rodando a validação geral (face, gram, retro)...")
        print()

        codigo = run_validar_sala()

        if codigo != 0:
            msg = mensagem_amigavel_erro(
                "A validação encontrou erros. Corrija os arquivos ou nomes indicados e rode de novo.",
                "Script validar_sala retornou erros. Veja as mensagens acima.",
                SCRIPT_NOME,
            )
            print()
            print("Mensagem para enviar no WhatsApp/Telegram/e-mail:")
            print("-" * 40)
            print(msg)
            print("-" * 40)
            return 1

        print()
        print("Validação OK. Agora vamos registrar o fim da sessão na planilha.")
        print()

        linhas = ler_linhas_planilha()
        if not linhas:
            print(mensagem_amigavel_erro("Nenhuma sessão iniciada hoje na planilha.", "Rode primeiro o script iniciar_trabalho.py.", SCRIPT_NOME), file=sys.stderr)
            return 1

        idx = None
        for i in range(len(linhas) - 1, -1, -1):
            if linhas[i].get("inicio_sessao") and not linhas[i].get("fim_sessao"):
                idx = i
                break
        if idx is None:
            print(mensagem_amigavel_erro("Nenhuma sessão em aberto na planilha.", "Rode primeiro o script iniciar_trabalho.py.", SCRIPT_NOME), file=sys.stderr)
            return 1

        trabalho_feito = input("Descrição do trabalho feito (resumo): ").strip()
        if not trabalho_feito:
            trabalho_feito = "Publicação e validação conforme plano."

        horas_str = input("Horas trabalhadas (ex: 1,5 ou 1.5): ").strip()
        try:
            horas_trabalhadas = float(horas_str.replace(",", "."))
        except ValueError:
            horas_trabalhadas = 0.0

        valor_hora = ler_valor_hora_cc()
        valor_sessao = round(horas_trabalhadas * valor_hora, 2)
        acumulado_anterior = ultimo_acumulado_cc()
        acumulado_novo = round(acumulado_anterior + valor_sessao, 2)

        linhas[idx]["trabalho_feito"] = trabalho_feito
        linhas[idx]["horas_trabalhadas"] = str(horas_trabalhadas).replace(".", ",")
        linhas[idx]["valor_sessao_cc"] = str(valor_sessao).replace(".", ",")
        linhas[idx]["acumulado_cc"] = str(acumulado_novo).replace(".", ",")
        linhas[idx]["fim_sessao"] = agora_iso()

        escrever_planilha(linhas)

        print()
        print("=" * 60)
        print("Sessão encerrada. Planilha atualizada.")
        print("=" * 60)
        print("Horas trabalhadas:", horas_trabalhadas)
        print("Valor desta sessão (CC):", valor_sessao)
        print("Acumulado CC:", acumulado_novo)
        print()
        msg_ok = mensagem_amigavel_ok("Trabalho validado e sessão encerrada.", f"Horas: {horas_trabalhadas} | Valor sessão CC: {valor_sessao} | Acumulado CC: {acumulado_novo}")
        print("Mensagem para enviar na sala (WhatsApp/Telegram/e-mail):")
        print("-" * 40)
        print(msg_ok)
        print("-" * 40)
        return 0

    except Exception as e:
        print(mensagem_amigavel_erro("Algo inesperado ao validar ou atualizar a planilha.", str(e), SCRIPT_NOME), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
