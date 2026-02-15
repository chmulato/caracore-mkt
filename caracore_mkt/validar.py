# -*- coding: utf-8 -*-
"""Validação face (F), gram (G), retro (LinkedIn)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

from .config import FACE_DIR, GRAM_DIR, RETRO_DIR, SALA_ASSETS_IMG, SALA_DIR

RE_FACE_HTML = re.compile(r"^\d{4}_\d{2}_\d{2}_.+_\(\d+\)_F\.html$")
RE_GRAM_HTML = re.compile(r"^\d{4}_\d{2}_\d{2}_.+_\(\d+\)_G\.html$")
RE_ARTICLE_HTML = re.compile(r"^\d{4}_\d{2}_\d{2}_article_(\d+)\.html$")

ERRORS: list[str] = []
WARNINGS: list[str] = []


def log_err(msg: str) -> None:
    ERRORS.append(msg)
    print(f"  [ERRO] {msg}", file=sys.stderr)


def log_warn(msg: str) -> None:
    WARNINGS.append(msg)
    print(f"  [AVISO] {msg}", file=sys.stderr)


def check_face() -> None:
    if not FACE_DIR.is_dir():
        log_err(f"Pasta face não encontrada: {FACE_DIR}")
        return
    artefatos_dir = FACE_DIR / "artefatos"
    if not artefatos_dir.is_dir():
        log_warn(f"Pasta face/artefatos/ não existe: {artefatos_dir}")
        return
    for p in artefatos_dir.glob("*.html"):
        if not RE_FACE_HTML.match(p.name):
            log_err(f"Face: nome fora do padrão (esperado YYYY_MM_DD_*_(nn)_F.html): {p.name}")
    if not (FACE_DIR / "facebook.html").is_file():
        log_warn(f"Face: listagem não encontrada: {FACE_DIR / 'facebook.html'}")


def check_gram() -> None:
    if not GRAM_DIR.is_dir():
        log_err(f"Pasta gram não encontrada: {GRAM_DIR}")
        return
    artefatos_dir = GRAM_DIR / "artefatos"
    if not artefatos_dir.is_dir():
        log_warn(f"Pasta gram/artefatos/ não existe: {artefatos_dir}")
        return
    for p in artefatos_dir.glob("*.html"):
        if not RE_GRAM_HTML.match(p.name):
            log_err(f"Gram: nome fora do padrão (esperado YYYY_MM_DD_*_(nn)_G.html): {p.name}")
    if not (GRAM_DIR / "instagram.html").is_file():
        log_warn(f"Gram: listagem não encontrada: {GRAM_DIR / 'instagram.html'}")


def check_retro() -> None:
    if not RETRO_DIR.is_dir():
        log_err(f"Pasta retro não encontrada: {RETRO_DIR}")
        return
    articles_dir = RETRO_DIR / "articles"
    if not articles_dir.is_dir():
        log_warn(f"Pasta retro/articles/ não existe: {articles_dir}")
        return
    if not (RETRO_DIR / "articles.html").is_file():
        log_warn(f"Retro: listagem não encontrada: {RETRO_DIR / 'articles.html'}")


def check_sala_assets() -> None:
    if not SALA_ASSETS_IMG.is_dir():
        log_warn(f"Pasta de imagens não existe: {SALA_ASSETS_IMG}")


def check_html_prompt_box(html_path: Path) -> bool:
    try:
        text = html_path.read_text(encoding="utf-8", errors="replace")
        return (
            "Texto para colar na IA" in text
            or "texto para colar na ia" in text.lower()
            or "prompt-box" in text
            or 'class="prompt-box"' in text
        )
    except Exception:
        return False


def run_validar_sala() -> int:
    """Executa validação completa. Retorna 0 se OK, 1 se erros."""
    ERRORS.clear()
    WARNINGS.clear()
    check_face()
    check_gram()
    check_retro()
    check_sala_assets()
    for artefatos_dir, pattern in [
        (FACE_DIR / "artefatos", "*_F.html"),
        (GRAM_DIR / "artefatos", "*_G.html"),
    ]:
        if artefatos_dir.is_dir():
            for p in artefatos_dir.glob(pattern):
                if not check_html_prompt_box(p):
                    log_warn(f"Artefato sem caixa 'Texto para colar na IA': {p.name}")
    return 1 if ERRORS else 0
