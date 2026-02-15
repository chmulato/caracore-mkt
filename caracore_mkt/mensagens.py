# -*- coding: utf-8 -*-
"""Mensagens amigáveis para reportar na sala (WhatsApp, Telegram, e-mail)."""


def mensagem_amigavel_erro(titulo: str, detalhe: str, script: str) -> str:
    """Mensagem pronta para copiar e enviar no WhatsApp, Telegram ou e-mail da Cara Core."""
    return (
        f"[Sala de Notícias]\n"
        f"Script: {script}\n"
        f"O que aconteceu: {titulo}\n"
        f"Detalhe: {detalhe}\n"
        f"Por favor, verifique ou avise a equipe."
    )


def mensagem_amigavel_ok(titulo: str, detalhe: str) -> str:
    """Mensagem de sucesso para reportar na sala."""
    return f"[Sala de Notícias] {titulo}\n{detalhe}"
