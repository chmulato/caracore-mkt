#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cara Core MKT - Orquestrador da oficina.
Organiza a execucao dos scripts operacionais em um unico ponto de entrada.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT / "scripts"

TASKS = [
    ("1", "iniciar", "iniciar_trabalho.py", "Iniciar o trabalho do dia"),
    ("2", "validar-encerrar", "validar_trabalho_executado.py", "Validar e encerrar sessao"),
    ("3", "transportar", "transportar_para_salas.py", "Transportar para as salas"),
    ("4", "validar-face", "validar_entrega_face.py", "Validar entrega Face"),
    ("5", "validar-gram", "validar_entrega_gram.py", "Validar entrega Gram"),
    ("6", "validar-retro", "validar_entrega_retro.py", "Validar entrega Retro"),
    ("7", "validar-sala", "validar_sala.py", "Validacao geral (face, gram, retro)"),
]

LOTES = {
    "abertura": ["1"],
    "operacao": ["3", "4", "5", "6"],
    "fechamento": ["7", "2"],
    "completo": ["1", "3", "4", "5", "6", "7", "2"],
}


def _task_by_key(key: str) -> tuple[str, str, str, str] | None:
    key = key.strip().lower()
    for t in TASKS:
        if key in {t[0], t[1], t[2]}:
            return t
    return None


def _run_task(task: tuple[str, str, str, str]) -> int:
    _, slug, filename, title = task
    script_path = SCRIPTS_DIR / filename
    print("=" * 70)
    print(f"Executando: {slug} - {title}")
    print(f"Script: {script_path}")
    print("=" * 70)
    proc = subprocess.run([sys.executable, str(script_path)], cwd=str(ROOT))
    return proc.returncode


def list_tasks() -> None:
    print("Cara Core MKT - Oficina organizada")
    print("\nTarefas disponiveis:")
    for n, slug, filename, title in TASKS:
        print(f"  {n}. {slug:<16} {title} ({filename})")
    print("\nLotes disponiveis:")
    for name, seq in LOTES.items():
        labels = []
        for key in seq:
            t = _task_by_key(key)
            if t:
                labels.append(t[1])
        print(f"  - {name:<10} -> {', '.join(labels)}")



def run_one(key: str) -> int:
    task = _task_by_key(key)
    if not task:
        print(f"Tarefa nao encontrada: {key}", file=sys.stderr)
        return 2
    return _run_task(task)



def run_lote(name: str) -> int:
    sequence = LOTES.get(name)
    if not sequence:
        print(f"Lote nao encontrado: {name}", file=sys.stderr)
        return 2

    print(f"Iniciando lote: {name}")
    for key in sequence:
        task = _task_by_key(key)
        if not task:
            continue
        code = _run_task(task)
        if code != 0:
            print(f"Lote interrompido em {task[1]} (codigo {code}).", file=sys.stderr)
            return code

    print(f"Lote '{name}' concluido com sucesso.")
    return 0



def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="oficina.py",
        description="Orquestrador dos scripts da oficina Cara Core MKT.",
    )
    p.add_argument(
        "--listar",
        action="store_true",
        help="Lista tarefas e lotes disponiveis.",
    )
    p.add_argument(
        "--rodar",
        metavar="TAREFA",
        help="Executa uma tarefa (numero, slug ou nome do arquivo).",
    )
    p.add_argument(
        "--lote",
        choices=sorted(LOTES.keys()),
        help="Executa um lote organizado de tarefas.",
    )
    return p



def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.listar or (not args.rodar and not args.lote):
        list_tasks()
        return 0

    if args.rodar:
        return run_one(args.rodar)

    if args.lote:
        return run_lote(args.lote)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
