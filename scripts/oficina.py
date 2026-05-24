#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cara Core MKT - Orquestrador da oficina.
Organiza a execucao dos scripts operacionais em um unico ponto de entrada.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT / "scripts"
DEFAULT_RELEASES_DIR = Path("D:/dev/caracore-mkt-releases")
DEFAULT_TOKEN_FILE = ROOT / "token.txt"
DEFAULT_REPO = "chmulato/caracore-mkt-releases"

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

DELIVERY_INCLUDE = [
    "caracore_mkt",
    "scripts",
    "requirements.txt",
    "README.txt",
    "LICENSE",
    "CTO_VALIDACAO_MKT.txt",
]

DELIVERY_EXCLUDE_NAMES = {
    ".git",
    ".github",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "token.txt",
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


def _safe_version(version: str) -> str:
    clean = version.strip().replace(" ", "-")
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-"
    if not clean or any(ch not in allowed for ch in clean):
        raise ValueError("Versao invalida. Use apenas letras, numeros, ponto, underscore e hifen.")
    return clean


def _iter_files_for_delivery() -> list[Path]:
    selected: list[Path] = []
    for item in DELIVERY_INCLUDE:
        path = ROOT / item
        if not path.exists():
            continue
        if path.is_file():
            selected.append(path)
            continue
        for candidate in path.rglob("*"):
            if candidate.is_dir():
                continue
            if any(part in DELIVERY_EXCLUDE_NAMES for part in candidate.parts):
                continue
            selected.append(candidate)
    return selected


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def run_delivery(version: str | None, releases_dir: str | None, dry_run: bool) -> int:
    try:
        version_label = _safe_version(version) if version else dt.date.today().isoformat()
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    target_root = Path(releases_dir).expanduser().resolve() if releases_dir else DEFAULT_RELEASES_DIR
    downloads_dir = target_root / "docs" / "downloads"
    artifact_name = f"caracore-mkt-python-source-{version_label}.zip"
    artifact_path = downloads_dir / artifact_name

    if not (target_root / ".git").exists():
        print(f"Repositorio de releases nao encontrado em: {target_root}", file=sys.stderr)
        return 2

    files = _iter_files_for_delivery()
    if not files:
        print("Nenhum arquivo encontrado para delivery.", file=sys.stderr)
        return 2

    print("=" * 70)
    print("Delivery MKT - Empacotamento Python")
    print(f"Versao: {version_label}")
    print(f"Destino: {artifact_path}")
    print(f"Arquivos no pacote: {len(files)}")
    print("=" * 70)

    if dry_run:
        print("Dry-run ativo: ZIP nao foi gerado.")
        return 0

    downloads_dir.mkdir(parents=True, exist_ok=True)
    if artifact_path.exists():
        artifact_path.unlink()

    with zipfile.ZipFile(artifact_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            zf.write(f, arcname=f.relative_to(ROOT))
    sha256 = _sha256_file(artifact_path)
    sha_file = artifact_path.with_suffix(artifact_path.suffix + ".sha256")
    sha_file.write_text(f"{sha256}  {artifact_path.name}\n", encoding="utf-8")

    print("Artefato gerado com sucesso.")
    print(f"Arquivo: {artifact_path}")
    print(f"SHA256: {sha256}")
    print(f"Checksum: {sha_file}")
    print("\nProximo passo sugerido:")
    print("1) Commit/push no repo de releases")
    print("2) Executar workflow Publish MKT Release com a tag da versao")
    return 0


def _read_token(token_file: str | None) -> str:
    path = Path(token_file).expanduser().resolve() if token_file else DEFAULT_TOKEN_FILE
    if not path.exists():
        raise FileNotFoundError(f"Token nao encontrado em: {path}")
    raw = path.read_text(encoding="utf-8").strip()
    if "=" in raw:
        _, token = raw.split("=", 1)
        token = token.strip().strip("\"'").strip()
    else:
        token = raw
    if not token:
        raise ValueError(f"Token vazio em: {path}")
    return token


def _http_json(method: str, url: str, token: str, payload: dict | None = None) -> dict:
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url=url, method=method, data=data)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if data is not None:
        req.add_header("Content-Type", "application/json")

    with urllib.request.urlopen(req) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body) if body else {}


def _http_delete(url: str, token: str) -> None:
    req = urllib.request.Request(url=url, method="DELETE")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    with urllib.request.urlopen(req) as resp:
        resp.read()


def _resolve_tag(version: str) -> str:
    return version if version.startswith("v") else f"v{version}"


def validate_token(repo: str | None, token_file: str | None) -> int:
    repo_name = repo or DEFAULT_REPO
    try:
        token = _read_token(token_file)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    try:
        data = _http_json("GET", f"https://api.github.com/repos/{repo_name}", token)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(f"Token invalido/sem acesso ({exc.code}).", file=sys.stderr)
        print(body, file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"Falha de rede ao validar token: {exc}", file=sys.stderr)
        return 1

    perms = data.get("permissions") or {}
    print("Token validado com sucesso.")
    print(f"Repo: {data.get('full_name', repo_name)}")
    print(f"Permissoes: push={perms.get('push')} pull={perms.get('pull')}")
    if perms.get("push") is not True:
        print("Aviso: token sem permissao de escrita (push).", file=sys.stderr)
        return 1
    return 0


def validate_release(version: str, repo: str | None, token_file: str | None, releases_dir: str | None) -> int:
    try:
        version_label = _safe_version(version)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    repo_name = repo or DEFAULT_REPO
    tag = _resolve_tag(version_label)
    artifact_name = f"caracore-mkt-python-source-{version_label}.zip"
    target_root = Path(releases_dir).expanduser().resolve() if releases_dir else DEFAULT_RELEASES_DIR
    artifact_path = target_root / "docs" / "downloads" / artifact_name
    sha_path = artifact_path.with_suffix(artifact_path.suffix + ".sha256")

    print("=" * 70)
    print("Validacao de release")
    print(f"Repo: {repo_name}")
    print(f"Tag: {tag}")
    print(f"Artefato local: {artifact_path}")
    print("=" * 70)

    if not artifact_path.exists():
        print("Artefato local ausente.", file=sys.stderr)
        return 1
    if not sha_path.exists():
        print("Arquivo de checksum ausente.", file=sys.stderr)
        return 1

    try:
        token = _read_token(token_file)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    try:
        release = _http_json("GET", f"https://api.github.com/repos/{repo_name}/releases/tags/{tag}", token)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            print("Release ainda nao existe no GitHub para essa tag.")
            return 1
        body = exc.read().decode("utf-8", errors="replace")
        print(f"Falha ao validar release ({exc.code}).", file=sys.stderr)
        print(body, file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"Falha de rede ao validar release: {exc}", file=sys.stderr)
        return 1

    assets = release.get("assets") or []
    names = {a.get("name") for a in assets}
    ok_zip = artifact_name in names
    ok_sha = sha_path.name in names
    print(f"Release URL: {release.get('html_url', '(indisponivel)')}")
    print(f"Asset ZIP presente: {ok_zip}")
    print(f"Asset SHA256 presente: {ok_sha}")
    return 0 if (ok_zip and ok_sha) else 1


def publish_release(
    version: str,
    release_name: str | None,
    repo: str | None,
    token_file: str | None,
    releases_dir: str | None,
    prerelease: bool,
    dry_run: bool,
) -> int:
    try:
        version_label = _safe_version(version)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    repo_name = repo or DEFAULT_REPO
    artifact_name = f"caracore-mkt-python-source-{version_label}.zip"
    target_root = Path(releases_dir).expanduser().resolve() if releases_dir else DEFAULT_RELEASES_DIR
    artifact_path = target_root / "docs" / "downloads" / artifact_name
    tag = _resolve_tag(version_label)
    final_release_name = release_name or f"Cara Core MKT {tag}"
    sha_path = artifact_path.with_suffix(artifact_path.suffix + ".sha256")

    if not artifact_path.exists():
        print(f"Artefato nao encontrado: {artifact_path}", file=sys.stderr)
        print("Rode antes: --delivery --versao <versao>", file=sys.stderr)
        return 2
    if not sha_path.exists():
        print(f"Checksum nao encontrado: {sha_path}", file=sys.stderr)
        print("Rode novamente o delivery para gerar checksum.", file=sys.stderr)
        return 2

    print("=" * 70)
    print("Publicacao GitHub Releases")
    print(f"Repo: {repo_name}")
    print(f"Tag: {tag}")
    print(f"Release: {final_release_name}")
    print(f"Arquivo: {artifact_path}")
    print("=" * 70)
    if dry_run:
        print("Dry-run ativo: release nao foi publicada.")
        return 0

    try:
        token = _read_token(token_file)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    api_base = f"https://api.github.com/repos/{repo_name}"
    try:
        release = _http_json("GET", f"{api_base}/releases/tags/{tag}", token)
        release_id = release.get("id")
        if release_id:
            release = _http_json(
                "PATCH",
                f"{api_base}/releases/{release_id}",
                token,
                payload={
                    "name": final_release_name,
                    "prerelease": prerelease,
                },
            )
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            body = exc.read().decode("utf-8", errors="replace")
            print(f"Falha ao consultar release ({exc.code}).", file=sys.stderr)
            print(body, file=sys.stderr)
            return 1
        release = _http_json(
            "POST",
            f"{api_base}/releases",
            token,
            payload={
                "tag_name": tag,
                "name": final_release_name,
                "prerelease": prerelease,
                "generate_release_notes": True,
            },
        )
    except urllib.error.URLError as exc:
        print(f"Falha de rede ao criar/consultar release: {exc}", file=sys.stderr)
        return 1
    release_id = release.get("id")
    if not release_id:
        print("Release sem id retornado pela API.", file=sys.stderr)
        return 1
    try:
        assets = _http_json("GET", f"{api_base}/releases/{release_id}/assets", token)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(f"Falha ao listar assets ({exc.code}).", file=sys.stderr)
        print(body, file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"Falha de rede ao listar assets: {exc}", file=sys.stderr)
        return 1

    existing_assets: dict[str, int] = {}
    for asset in assets if isinstance(assets, list) else []:
        name = asset.get("name")
        aid = asset.get("id")
        if isinstance(name, str) and isinstance(aid, int):
            existing_assets[name] = aid

    for name in (artifact_name, sha_path.name):
        asset_id = existing_assets.get(name)
        if asset_id:
            try:
                _http_delete(f"{api_base}/releases/assets/{asset_id}", token)
            except urllib.error.HTTPError as exc:
                body = exc.read().decode("utf-8", errors="replace")
                print(f"Falha ao remover asset antigo '{name}' ({exc.code}).", file=sys.stderr)
                print(body, file=sys.stderr)
                return 1
            except urllib.error.URLError as exc:
                print(f"Falha de rede ao remover asset antigo '{name}': {exc}", file=sys.stderr)
                return 1

    upload_url = str(release.get("upload_url", "")).split("{", 1)[0]
    if not upload_url:
        print("Resposta da API sem upload_url.", file=sys.stderr)
        return 1

    for file_path, content_type in ((artifact_path, "application/zip"), (sha_path, "text/plain")):
        upload_qs = urllib.parse.urlencode({"name": file_path.name})
        upload_target = f"{upload_url}?{upload_qs}"
        req = urllib.request.Request(url=upload_target, method="POST", data=file_path.read_bytes())
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("X-GitHub-Api-Version", "2022-11-28")
        req.add_header("Content-Type", content_type)
        try:
            with urllib.request.urlopen(req) as resp:
                resp.read()
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            print(f"Falha ao enviar asset '{file_path.name}' ({exc.code}).", file=sys.stderr)
            print(body, file=sys.stderr)
            return 1
        except urllib.error.URLError as exc:
            print(f"Falha de rede ao enviar asset '{file_path.name}': {exc}", file=sys.stderr)
            return 1

    print("Release publicada com sucesso.")
    print(f"URL: {release.get('html_url', '(indisponivel)')}")
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
    p.add_argument(
        "--delivery",
        action="store_true",
        help="Gera e entrega o ZIP versionado dos scripts Python no repo de releases.",
    )
    p.add_argument(
        "--versao",
        metavar="VERSAO",
        help="Versao para o nome do artefato (ex: 2026-05-24 ou v1.0.0).",
    )
    p.add_argument(
        "--releases-dir",
        metavar="CAMINHO",
        help=f"Caminho do repo de releases (padrao: {DEFAULT_RELEASES_DIR}).",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Mostra o plano do delivery sem gravar ZIP.",
    )
    p.add_argument(
        "--publicar-release",
        action="store_true",
        help="Publica no GitHub Releases usando token.txt da oficina.",
    )
    p.add_argument(
        "--token-file",
        metavar="CAMINHO",
        help=f"Caminho do token (padrao: {DEFAULT_TOKEN_FILE}).",
    )
    p.add_argument(
        "--repo",
        metavar="OWNER/REPO",
        help=f"Repositorio de destino da release (padrao: {DEFAULT_REPO}).",
    )
    p.add_argument(
        "--release-name",
        metavar="NOME",
        help="Nome da release no GitHub.",
    )
    p.add_argument(
        "--prerelease",
        action="store_true",
        help="Publica como pre-release.",
    )
    p.add_argument(
        "--validar-token",
        action="store_true",
        help="Valida token e permissoes no repo de releases.",
    )
    p.add_argument(
        "--validar-release",
        action="store_true",
        help="Valida se a release e os assets da versao existem no GitHub.",
    )
    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.delivery:
        return run_delivery(args.versao, args.releases_dir, args.dry_run)

    if args.publicar_release:
        if not args.versao:
            print("Informe --versao para publicar release.", file=sys.stderr)
            return 2
        return publish_release(
            version=args.versao,
            release_name=args.release_name,
            repo=args.repo,
            token_file=args.token_file,
            releases_dir=args.releases_dir,
            prerelease=args.prerelease,
            dry_run=args.dry_run,
        )

    if args.validar_token:
        return validate_token(repo=args.repo, token_file=args.token_file)

    if args.validar_release:
        if not args.versao:
            print("Informe --versao para validar release.", file=sys.stderr)
            return 2
        return validate_release(
            version=args.versao,
            repo=args.repo,
            token_file=args.token_file,
            releases_dir=args.releases_dir,
        )

    if args.listar or (
        not args.rodar
        and not args.lote
        and not args.delivery
        and not args.publicar_release
        and not args.validar_token
        and not args.validar_release
    ):
        list_tasks()
        return 0

    if args.rodar:
        return run_one(args.rodar)

    if args.lote:
        return run_lote(args.lote)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
