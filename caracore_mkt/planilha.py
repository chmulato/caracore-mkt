# -*- coding: utf-8 -*-
"""Leitura e escrita da planilha da sala (CSV)."""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from .config import (
    CONFIG_PATH,
    ENCODING,
    CSV_DELIM,
    PLANILHA_HEADER,
    PLANILHA_PATH,
    TRABALHO_DO_DIA_PATH,
)


def garantir_planilha_existe() -> None:
    if not PLANILHA_PATH.exists():
        PLANILHA_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(PLANILHA_PATH, "w", encoding=ENCODING, newline="") as f:
            w = csv.writer(f, delimiter=CSV_DELIM)
            w.writerow(PLANILHA_HEADER)


def ler_linhas_planilha() -> list[dict]:
    garantir_planilha_existe()
    with open(PLANILHA_PATH, "r", encoding=ENCODING, newline="") as f:
        r = csv.DictReader(f, delimiter=CSV_DELIM)
        return list(r)


def escrever_planilha(linhas: list[dict]) -> None:
    garantir_planilha_existe()
    with open(PLANILHA_PATH, "w", encoding=ENCODING, newline="") as f:
        w = csv.DictWriter(f, fieldnames=PLANILHA_HEADER, delimiter=CSV_DELIM)
        w.writeheader()
        for row in linhas:
            w.writerow({k: row.get(k, "") for k in PLANILHA_HEADER})


def ultimo_acumulado_cc() -> float:
    linhas = ler_linhas_planilha()
    if not linhas:
        return 0.0
    for row in reversed(linhas):
        try:
            return float(str(row.get("acumulado_cc", "0")).replace(",", "."))
        except ValueError:
            continue
    return 0.0


def ler_trabalho_do_dia() -> str:
    if TRABALHO_DO_DIA_PATH.exists():
        return TRABALHO_DO_DIA_PATH.read_text(encoding=ENCODING).strip()
    return "Publicar artefatos conforme plano da semana (Face, Gram ou Retro). Copiar texto, gerar imagens na IA, salvar com nome correto."


def ler_valor_hora_cc() -> float:
    if not CONFIG_PATH.exists():
        return 0.0
    for line in CONFIG_PATH.read_text(encoding=ENCODING).splitlines():
        line = line.strip()
        if line.startswith("valor_hora_cc="):
            try:
                return float(line.split("=", 1)[1].strip().replace(",", "."))
            except ValueError:
                return 0.0
    return 0.0


def agora_iso() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def hoje() -> str:
    return datetime.now().strftime("%Y-%m-%d")
