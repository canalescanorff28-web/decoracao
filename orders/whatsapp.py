import re
from urllib.parse import quote


def normalize_phone(value):
    return re.sub(r"\D", "", value or "")


def wa_link(phone, message):
    phone = normalize_phone(phone)
    if not phone:
        return ""
    return f"https://wa.me/{phone}?text={quote(message)}"


def brl(value):
    text = f"{value:,.2f}"
    return text.replace(",", "X").replace(".", ",").replace("X", ".")


def format_order(order):
    lines = [
        "✨🎈 *NOVA SOLICITAÇÃO DE DECORAÇÃO* 🎈✨",
        f"🧾 *Pedido:* {order.code}",
        "",
        "━━━━━━━━━━━━━━━━━━━━",
        "👤 *DADOS DO CLIENTE*",
        "━━━━━━━━━━━━━━━━━━━━",
        f"🙋 *Nome:* {order.customer_name}",
        f"📱 *WhatsApp:* {order.customer_whatsapp}",
        "",
        "━━━━━━━━━━━━━━━━━━━━",
        "🎉 *DETALHES DO EVENTO*",
        "━━━━━━━━━━━━━━━━━━━━",
    ]

    if order.event_type:
        lines.append(f"🎊 *Tipo:* {order.get_event_type_display()}")
    if order.event_theme:
        lines.append(f"🎨 *Tema da festa:* {order.event_theme}")
    if order.celebrant_name:
        lines.append(f"🎂 *Aniversariante / homenageado:* {order.celebrant_name}")
    if order.celebrant_age is not None:
        lines.append(f"🎈 *Idade:* {order.celebrant_age}")
    if order.event_date:
        lines.append(f"📅 *Data:* {order.event_date.strftime('%d/%m/%Y')}")
    if order.event_location:
        lines.append(f"📍 *Local:* {order.event_location}")

    lines += [
        "",
        "━━━━━━━━━━━━━━━━━━━━",
        "💡 *INSPIRAÇÕES ESCOLHIDAS*",
        "━━━━━━━━━━━━━━━━━━━━",
    ]

    for item in order.items.all():
        lines.append(
            f"💗 *{item.title_snapshot}*\\n"
            f"   💰 Referência: R$ {brl(item.unit_price_snapshot)}"
        )

    if order.keep_details:
        lines += [
            "",
            "✅ *O QUE DESEJA MANTER DA INSPIRAÇÃO*",
            f"💬 {order.keep_details}",
        ]

    if order.change_details:
        lines += [
            "",
            "🎨 *O QUE DESEJA ADAPTAR / MUDAR*",
            f"💬 {order.change_details}",
        ]

    if order.notes:
        lines += [
            "",
            "📝 *OBSERVAÇÕES IMPORTANTES*",
            f"💬 {order.notes}",
        ]

    lines += [
        "",
        "━━━━━━━━━━━━━━━━━━━━",
        "💰 *RESUMO DO ORÇAMENTO*",
        "━━━━━━━━━━━━━━━━━━━━",
        f"✨ *Total de referência:* R$ {brl(order.total_reference)}",
        "",
        "ℹ️ _Este é um valor de referência da(s) inspiração(ões) escolhida(s)._",
        "O valor final poderá variar conforme:",
        "• 🎨 tema e nível de personalização",
        "• 📐 tamanho da montagem",
        "• 🎀 itens e detalhes escolhidos",
        "• 📍 local do evento",
        "• 📅 data e disponibilidade",
        "",
        "💞 *Próximo passo:* alinhar os detalhes diretamente com a decoradora escolhida.",
        "",
        "🌷 _Solicitação registrada pelo site_",
        "*Aline Nayane & Érika Carina • Decoração* ✨",
    ]

    return "\\n".join(lines)


def customer_ack(order):
    return (
        f"Olá, {order.customer_name}! 💕 Recebemos sua solicitação {order.code} pelo nosso site. "
        "Vamos analisar a inspiração escolhida, o tema da sua festa e os detalhes da personalização. "
        "Em seguida alinhamos disponibilidade e orçamento final por aqui."
    )


def customer_confirmed(order):
    return (
        f"Olá, {order.customer_name}! ✨ Sua solicitação {order.code} foi marcada como confirmada. "
        "Vamos seguir com os próximos detalhes da sua decoração por aqui."
    )


def customer_finished(order):
    return (
        f"Olá, {order.customer_name}! 💗 A solicitação {order.code} foi finalizada. "
        "Aline Nayane & Érica Carina agradecem pela confiança!"
    )
