#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cara Core MKT — Script 3: Transportar o trabalho para as salas face, gram, retro.
Python Baseline (Microsoft Store).
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from caracore_mkt.config import FACE_DIR, GRAM_DIR, RETRO_DIR, ENTREGA_DIR
from caracore_mkt.mensagens import mensagem_amigavel_erro, mensagem_amigavel_ok

SCRIPT_NOME = "transportar_para_salas.py (Script 3 — Transportar para as salas)"

ENTREGA_FACE = ENTREGA_DIR / "face"
ENTREGA_GRAM = ENTREGA_DIR / "gram"
ENTREGA_RETRO = ENTREGA_DIR / "retro"
DEST_FACE = FACE_DIR / "artefatos"
DEST_GRAM = GRAM_DIR / "artefatos"
DEST_RETRO = RETRO_DIR / "articles"


def copiar_origem_destino(origem: Path, destino: Path) -> tuple[int, list[str]]:
    erros = []
    n = 0
    if not origem.is_dir():
        return 0, [f"Pasta de entrega não encontrada: {origem}"]
    destino.mkdir(parents=True, exist_ok=True)
    for f in origem.iterdir():
        if f.is_file():
            try:
                shutil.copy2(f, destino / f.name)
                n += 1
            except Exception as e:
                erros.append(f"{f.name}: {e}")
    return n, erros


def main() -> int:
    try:
        print("=" * 60)
        print("SALA DE NOTÍCIAS — Transportar trabalho para as salas")
        print("=" * 60)
        print()
        print("Origem: sala/entrega/ (face, gram, retro)")
        print("Destino: face/artefatos/, gram/artefatos/, retro/articles/")
        print()

        if not ENTREGA_DIR.is_dir():
            print("A pasta sala/entrega/ não existe. Crie e coloque dentro:")
            print("  entrega/face/   — arquivos para Facebook")
            print("  entrega/gram/   — arquivos para Instagram")
            print("  entrega/retro/  — arquivos para LinkedIn (retro)")
            print()
            print(mensagem_amigavel_erro("Pasta de entrega não encontrada.", "Crie a pasta sala/entrega/ com as subpastas face, gram e retro.", SCRIPT_NOME))
            return 1

        total = 0
        erros_geral = []
        for origem, destino, nome in [
            (ENTREGA_FACE, DEST_FACE, "Facebook (face)"),
            (ENTREGA_GRAM, DEST_GRAM, "Instagram (gram)"),
            (ENTREGA_RETRO, DEST_RETRO, "LinkedIn (retro)"),
        ]:
            n, erros = copiar_origem_destino(origem, destino)
            erros_geral.extend(erros)
            if n > 0:
                print(f"  {nome}: {n} arquivo(s) copiado(s) para {destino.name}/")
            total += n

        if erros_geral:
            print()
            print(mensagem_amigavel_erro("Alguns arquivos não puderam ser copiados.", "; ".join(erros_geral[:3]) + ("..." if len(erros_geral) > 3 else ""), SCRIPT_NOME), file=sys.stderr)
            return 1

        if total == 0:
            print("Nenhum arquivo na pasta de entrega. Coloque os arquivos em sala/entrega/face/, gram/, retro/")
            return 0

        print()
        print("Total:", total, "arquivo(s) transportado(s).")
        print()
        print("Mensagem para enviar na sala:")
        print(mensagem_amigavel_ok("Trabalho transportado para as salas.", f"{total} arquivo(s) copiado(s) para face, gram e retro."))
        return 0

    except Exception as e:
        print(mensagem_amigavel_erro("Algo inesperado ao transportar os arquivos.", str(e), SCRIPT_NOME), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
