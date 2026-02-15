# -*- coding: utf-8 -*-
"""
Cara Core MKT — Configuração de caminhos.
Sala e repositório podem ser definidos por variáveis de ambiente.
"""
from pathlib import Path
import os

_PKG = Path(__file__).resolve().parent
_PROJECT = _PKG.parent
_DEFAULT_REPO = _PROJECT.parent / "caracore-site"

REPO_ROOT = Path(os.environ.get("CARACORE_REPO", str(_DEFAULT_REPO)))
SALA_DIR = Path(os.environ.get("CARACORE_SALA", str(REPO_ROOT / "sala")))

FACE_DIR = REPO_ROOT / "face"
GRAM_DIR = REPO_ROOT / "gram"
RETRO_DIR = REPO_ROOT / "retro"
SALA_ASSETS_IMG = SALA_DIR / "assets" / "img"

PLANILHA_PATH = SALA_DIR / "planilha_sala.csv"
TRABALHO_DO_DIA_PATH = SALA_DIR / "regis" / "trabalho_do_dia.txt"
CONFIG_PATH = SALA_DIR / "regis" / "config_sala.txt"
ENTREGA_DIR = SALA_DIR / "entrega"
FEEDBACK_FILE = SALA_DIR / "regis" / "feedback_sala.txt"

ENCODING = "utf-8"
CSV_DELIM = ";"

PLANILHA_HEADER = [
    "data",
    "tarefa_do_dia",
    "trabalho_feito",
    "horas_previstas",
    "horas_trabalhadas",
    "valor_sessao_cc",
    "acumulado_cc",
    "inicio_sessao",
    "fim_sessao",
]
