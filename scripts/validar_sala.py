#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cara Core MKT — Validação geral (face, gram, retro).
Python Baseline (Microsoft Store). Rodar no final da sessão.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from caracore_mkt.config import REPO_ROOT
from caracore_mkt.validar import ERRORS, WARNINGS, run_validar_sala


def main() -> int:
    print("Sala de Notícias — Validação face (F), gram (G), retro (LinkedIn depois do 86)")
    print(f"Repositório: {REPO_ROOT}")
    print()

    codigo = run_validar_sala()

    if codigo != 0:
        print()
        print("Corrija os erros acima e rode o script novamente.")
        return 1
    if WARNINGS:
        print()
        print("Validação concluída com avisos (nenhum erro bloqueante).")
        return 0
    print()
    print("Validação OK. Trabalho executado com sucesso.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
