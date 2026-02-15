# -*- coding: utf-8 -*-
"""Utilitários: abrir sala no navegador."""
import webbrowser
from .config import SALA_DIR


def abrir_sala_no_navegador() -> None:
    url = SALA_DIR / "opera-sala.html"
    if not url.exists():
        url = SALA_DIR / "index.htm"
    webbrowser.open(url.as_uri())
