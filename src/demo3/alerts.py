"""DEMO 3 - Alertas por consola, archivo, email (SMTP) y webhook (Slack/Discord)."""
import os
import smtplib
from datetime import datetime
from email.message import EmailMessage

import requests

from src.common.config import REPORTS_DIR, log


def format_alert(changes, old_snap: dict, new_snap: dict, limit: int = 15) -> str:
    high = [c for c in changes if c.severity == "HIGH"]
    head = [f"PRICE MONITOR – {len(high)} alertas importantes de {len(changes)} cambios"]
    if new_snap.get("simulated"):
        head.append("⚠️ DATOS SIMULADOS PARA DEMOSTRACIÓN")
    head.append(f"Comparación: snapshot #{old_snap['id']} → #{new_snap['id']}")
    lines = []
    for c in high[:limit]:
        if c.kind in ("PRICE_DROP", "PRICE_INCREASE"):
            lines.append(f"- {c.kind} {c.pct:+.1f}%: {c.title[:60]} ({c.old_price:.2f} → {c.new_price:.2f})")
        else:
            lines.append(f"- {c.kind}: {c.title[:60]}")
    if len(high) > limit:
        lines.append(f"... y {len(high) - limit} más (ver reporte)")
    return "\n".join(head + [""] + (lines or ["Sin alertas importantes."]))


def _write_file(text: str) -> str:
    path = REPORTS_DIR / f"alert_{datetime.now():%Y%m%d_%H%M%S}.txt"
    path.write_text(text, encoding="utf-8")
    return str(path)


def _send_email(subject: str, body: str) -> None:
    host, to = os.getenv("SMTP_HOST"), os.getenv("ALERT_EMAIL_TO")
    if not host or not to:
        return
    msg = EmailMessage()
    msg["Subject"], msg["From"], msg["To"] = subject, os.getenv("SMTP_USER", ""), to
    msg.set_content(body)
    with smtplib.SMTP(host, int(os.getenv("SMTP_PORT", "587")), timeout=30) as s:
        s.starttls()
        s.login(os.getenv("SMTP_USER", ""), os.getenv("SMTP_PASSWORD", ""))
        s.send_message(msg)
    log.info("Email de alerta enviado a %s", to)


def _send_webhook(body: str) -> None:
    url = os.getenv("WEBHOOK_URL")
    if not url:
        return
    key = "content" if os.getenv("WEBHOOK_KIND", "slack").lower() == "discord" else "text"
    requests.post(url, json={key: body[:1900]}, timeout=15).raise_for_status()
    log.info("Webhook enviado")


def notify_text(subject: str, body: str) -> None:
    """Envía un texto por todos los canales; un canal que falla no detiene a los otros."""
    print("\n" + "=" * 60 + f"\n{subject}\n{body}\n" + "=" * 60)
    for name, fn in (("archivo", lambda: log.info("Alerta guardada en %s", _write_file(subject + "\n\n" + body))),
                     ("email", lambda: _send_email(subject, body)),
                     ("webhook", lambda: _send_webhook(subject + "\n" + body))):
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            log.error("Canal %s falló: %s", name, str(exc)[:150])


def dispatch(changes, old_snap: dict, new_snap: dict) -> None:
    if not any(c.severity == "HIGH" for c in changes):
        log.info("Sin alertas HIGH: no se envía notificación.")
        return
    notify_text("Price Monitor – Alertas", format_alert(changes, old_snap, new_snap))