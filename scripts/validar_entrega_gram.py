#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cara Core MKT — Script 5: Validar entrega na sala gram (Instagram). Python Baseline (Microsoft Store)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from caracore_mkt.validar import ERRORS, check_gram
from caracore_mkt.mensagens import mensagem_amigavel_erro, mensagem_amigavel_ok

SCRIPT_NOME = "validar_entrega_gram.py (Script 5 — Validar entrega Gram)"


def main() -> int:
    try:
        ERRORS.clear()
        check_gram()
        if ERRORS:
            print(mensagem_amigavel_erro("A validação da sala Gram (Instagram) encontrou erros.", " ".join(ERRORS[:2]), SCRIPT_NOME), file=sys.stderr)
            return 1
        print(mensagem_amigavel_ok("Entrega Gram (Instagram) OK.", "Artefatos e nomes no padrão."))
        return 0
    except Exception as e:
        print(mensagem_amigavel_erro("Erro ao validar entrega Gram.", str(e), SCRIPT_NOME), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
