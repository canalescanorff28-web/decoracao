# -*- coding: utf-8 -*-
import re
from urllib.parse import quote, urlencode


def normalize_phone(value):
    return re.sub(r"\D", "", value or "")


def whatsapp_send_url(phone, message):
    """
    URL oficial gratuita de handoff para o WhatsApp.

    A query inteira é serializada no servidor em UTF-8 e sai como ASCII
    percent-encoded. Isso evita que JavaScript, DOM, service worker ou
    redirecionadores intermediários precisem manipular os emojis.
    """
    phone = normalize_phone(phone)
    if not phone:
        return ""

    query = urlencode(
        {
            "phone": phone,
            "text": message or "",
        },
        encoding="utf-8",
        errors="strict",
        quote_via=quote,
        safe="",
    )
    return f"https://api.whatsapp.com/send?{query}"


def wa_link(phone, message):
    # Compatibilidade com partes antigas do projeto.
    return whatsapp_send_url(phone, message)


def brl(value):
    text = f"{value:,.2f}"
    return text.replace(",", "X").replace(".", ",").replace("X", ".")


def _clean_message_text(value):
    text = str(value or "").replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def format_order(order):
    lines = [
        "🌸✨ NOVA SOLICITAÇÃO DE DECORAÇÃO ✨🌸",
        f"🧾 Pedido: {order.code}",
        "",
        "━━━━━━━━━━━━━━━━━━━━",
        "👤 DADOS DO CLIENTE",
        "━━━━━━━━━━━━━━━━━━━━",
        f"🙋 Nome: {_clean_message_text(order.customer_name)}",
        f"📱 WhatsApp: {_clean_message_text(order.customer_whatsapp)}",
        "",
        "━━━━━━━━━━━━━━━━━━━━",
        "🎉 DETALHES DO EVENTO",
        "━━━━━━━━━━━━━━━━━━━━",
    ]

    if order.event_type:
        lines.append(f"🎊 Tipo de evento: {_clean_message_text(order.get_event_type_display())}")
    if order.event_theme:
        lines.append(f"🎨 Tema da festa: {_clean_message_text(order.event_theme)}")
    if order.celebrant_name:
        lines.append(f"🎂 Aniversariante / homenageado: {_clean_message_text(order.celebrant_name)}")
    if order.celebrant_age is not None:
        lines.append(f"🎈 Idade: {order.celebrant_age}")
    if order.event_date:
        lines.append(f"📅 Data: {order.event_date.strftime('%d/%m/%Y')}")
    if order.guest_count:
        lines.append(f"👥 Convidados: {order.guest_count}")

    if order.event_location:
        lines += [
            "",
            "📍 LOCAL DO EVENTO",
            f"🏠 {_clean_message_text(order.event_location)}",
        ]

    lines += [
        "",
        "━━━━━━━━━━━━━━━━━━━━",
        "💡 INSPIRAÇÕES ESCOLHIDAS",
        "━━━━━━━━━━━━━━━━━━━━",
    ]

    for index, item in enumerate(order.items.all(), start=1):
        lines.append(f"🎀 {index}. {_clean_message_text(item.title_snapshot)}")
        lines.append(f"💰 Valor de referência: R$ {brl(item.unit_price_snapshot)}")
        lines.append("")

    if order.keep_choices or order.keep_details:
        lines.append("💗 O QUE DESEJA MANTER DA INSPIRAÇÃO")
        for value in order.keep_choices or []:
            lines.append(f"✓ {_clean_message_text(value)}")
        if order.keep_details:
            lines.append(f"💬 {_clean_message_text(order.keep_details)}")
        lines.append("")

    if order.change_choices or order.change_details:
        lines.append("🎨 O QUE DESEJA PERSONALIZAR / ADAPTAR")
        for value in order.change_choices or []:
            lines.append(f"✓ {_clean_message_text(value)}")
        if order.change_details:
            lines.append(f"💬 {_clean_message_text(order.change_details)}")
        lines.append("")

    if order.notes:
        lines += [
            "📝 OBSERVAÇÕES IMPORTANTES",
            f"💬 {_clean_message_text(order.notes)}",
            "",
        ]

    lines += [
        "━━━━━━━━━━━━━━━━━━━━",
        "💰 INVESTIMENTO DE REFERÊNCIA",
        "━━━━━━━━━━━━━━━━━━━━",
        f"✨ R$ {brl(order.total_reference)}",
        "",
        "ℹ️ O valor acima é uma referência baseada na(s) inspiração(ões) escolhida(s).",
        "O orçamento final poderá variar conforme:",
        "🎨 tema e nível de personalização",
        "📐 tamanho e estrutura da montagem",
        "🎀 itens e detalhes escolhidos",
        "📍 local do evento",
        "📅 data e disponibilidade",
        "",
        "💞 PRÓXIMO PASSO",
        "Escolha Aline Nayane ou Érika Carina para continuar o atendimento e alinhar os detalhes finais.",
        "",
        "🌷 Aline Nayane & Érika Carina",
        "Decoração • momentos especiais com personalidade ✨",
    ]

    return "\n".join(lines)

def customer_ack(order):
    return "\n".join([
        f"🌷 Olá, {_clean_message_text(order.customer_name)}!",
        "",
        f"Recebemos sua solicitação {order.code} com sucesso. ✨",
        "",
        "🎨 Vamos analisar a inspiração escolhida, o tema da festa e todos os detalhes da personalização.",
        "📅 Em seguida, alinhamos disponibilidade e orçamento final por aqui.",
        "",
        "💕 Aline Nayane & Érika Carina • Decoração",
    ])


def customer_confirmed(order):
    return "\n".join([
        f"✨ Olá, {_clean_message_text(order.customer_name)}!",
        "",
        f"Sua solicitação {order.code} foi confirmada. 🎉",
        "Agora vamos seguir com os próximos detalhes da sua decoração.",
        "",
        "🌷 Aline Nayane & Érika Carina • Decoração",
    ])


def customer_finished(order):
    return "\n".join([
        f"💗 Olá, {_clean_message_text(order.customer_name)}!",
        "",
        f"A solicitação {order.code} foi finalizada.",
        "Agradecemos muito pela confiança em nosso trabalho. ✨",
        "",
        "🌷 Aline Nayane & Érika Carina • Decoração",
    ])
