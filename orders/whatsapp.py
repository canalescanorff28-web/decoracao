import os
import re
import requests
from urllib.parse import quote

def normalize_phone(value):
    digits = re.sub(r"\D", "", value or "")
    return digits

def wa_link(phone, message):
    phone = normalize_phone(phone)
    if not phone:
        return ""
    return f"https://wa.me/{phone}?text={quote(message)}"

def cloud_configured():
    return all([
        os.getenv("WHATSAPP_ACCESS_TOKEN"),
        os.getenv("WHATSAPP_PHONE_NUMBER_ID"),
        os.getenv("WHATSAPP_GRAPH_VERSION"),
        os.getenv("WHATSAPP_AUTO_SEND", "0") == "1",
    ])

def send_text(to, body):
    """
    Envia mensagem de texto pela WhatsApp Business Cloud API.
    Observação: fora da janela permitida pela Meta, use templates aprovados.
    """
    if not cloud_configured():
        return {"ok": False, "reason": "not_configured"}

    token = os.getenv("WHATSAPP_ACCESS_TOKEN")
    phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    version = os.getenv("WHATSAPP_GRAPH_VERSION")
    url = f"https://graph.facebook.com/{version}/{phone_id}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": normalize_phone(to),
        "type": "text",
        "text": {"body": body},
    }
    r = requests.post(
        url,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=payload,
        timeout=20,
    )
    return {"ok": r.ok, "status": r.status_code, "body": r.text[:1000]}

def format_order(order):
    lines = [
        f"🎈 Novo pedido {order.code}",
        f"Cliente: {order.customer_name}",
        f"WhatsApp: {order.customer_whatsapp}",
    ]
    if order.event_date:
        lines.append(f"Data do evento: {order.event_date.strftime('%d/%m/%Y')}")
    lines.append("")
    lines.append("Itens:")
    for item in order.items.all():
        lines.append(f"• {item.title_snapshot} — R$ {item.unit_price_snapshot:.2f}")
    lines += [
        "",
        f"Total de referência: R$ {order.total_reference:.2f}",
    ]
    if order.notes:
        lines += ["", f"Observações: {order.notes}"]
    return "\n".join(lines)

def customer_ack(order):
    return (
        f"Olá, {order.customer_name}! 💕 Recebemos sua solicitação {order.code}. "
        "Vamos analisar os detalhes e entrar em contato para confirmar disponibilidade, "
        "personalização e valor final. Obrigada pelo interesse!"
    )

def customer_status(order):
    status = order.get_status_display()
    return (
        f"Olá, {order.customer_name}! Seu pedido {order.code} foi atualizado para: "
        f"{status}. Se precisar, responda esta mensagem."
    )
