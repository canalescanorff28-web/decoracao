import json
from urllib.parse import quote
from datetime import date
from decimal import Decimal

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_POST

from catalog.models import Decoration, SiteSettings
from .models import Order, OrderItem
from .whatsapp import format_order, wa_link, whatsapp_send_url


def _json(payload, *, status=200):
    response = JsonResponse(
        payload,
        status=status,
        json_dumps_params={"ensure_ascii": False},
    )
    response["Cache-Control"] = "no-store"
    return response


def _whatsapp_number(site, decorator):
    decorator = (decorator or "").strip().lower()
    if decorator == "aline":
        return site.decorator_one_whatsapp
    if decorator == "erika":
        return site.decorator_two_whatsapp
    return ""


def _whatsapp_redirect(request, phone, message):
    """
    Evita colocar a mensagem inteira no cabeçalho HTTP Location.

    Em alguns proxies, uma URL de WhatsApp com muitos emojis e dados do pedido
    ultrapassa o limite de tamanho do header e vira 5xx. O alvo fica no corpo
    HTML e o navegador faz a navegação automaticamente.
    """
    target = whatsapp_send_url(phone, message)
    if not target:
        return _json(
            {"ok": False, "error": "WhatsApp não configurado."},
            status=404,
        )

    response = render(
        request,
        "orders/whatsapp_handoff.html",
        {"target": target},
        status=200,
    )
    response["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response["Pragma"] = "no-cache"
    response["Referrer-Policy"] = "no-referrer"
    response["X-Robots-Tag"] = "noindex, nofollow"
    return response


@require_GET
@never_cache
def contact_whatsapp(request, decorator):
    site = SiteSettings.current()
    phone = _whatsapp_number(site, decorator)
    name = (
        site.decorator_one_name
        if decorator == "aline"
        else site.decorator_two_name
    )

    message = (
        f"Olá, {name}! 😊\n\n"
        "Vim pelo site de Aline Nayane & Érika Carina e gostaria de "
        "conversar sobre uma decoração. 🎈✨"
    )
    return _whatsapp_redirect(request, phone, message)


@require_GET
@never_cache
def order_whatsapp_redirect(request, code, decorator):
    try:
        order = Order.objects.prefetch_related("items").get(code=code)
    except Order.DoesNotExist:
        return _json(
            {"ok": False, "error": "Solicitação não encontrada."},
            status=404,
        )

    site = SiteSettings.current()
    phone = _whatsapp_number(site, decorator)
    message = format_order(order)
    return _whatsapp_redirect(request, phone, message)


@require_GET
@never_cache
def health(request):
    return _json({
        "ok": True,
        "service": "aline-erika-decor",
        "mode": "free-whatsapp-selector",
    })


def _clean_phone(value):
    return "".join(ch for ch in (value or "") if ch.isdigit())


def _text(data, key, limit):
    return str(data.get(key) or "").strip()[:limit]


def _choice_list(data, key, allowed):
    raw = data.get(key) or []
    if not isinstance(raw, list):
        return []
    clean = []
    for value in raw:
        value = str(value or "").strip()
        if value in allowed and value not in clean:
            clean.append(value)
    return clean


def _decimal_coordinate(data, key, minimum, maximum):
    raw = str(data.get(key) or "").strip()
    if not raw:
        return None
    try:
        value = Decimal(raw)
    except Exception:
        return None
    if value < Decimal(str(minimum)) or value > Decimal(str(maximum)):
        return None
    return value


def _compose_event_location(data):
    venue = _text(data, "event_venue", 120)
    street = _text(data, "event_street", 180)
    number = _text(data, "event_number", 40)
    neighborhood = _text(data, "event_neighborhood", 120)
    city = _text(data, "event_city", 120)
    state = _text(data, "event_state", 80)
    complement = _text(data, "event_complement", 120)
    reference = _text(data, "event_reference", 180)
    postcode = _text(data, "event_postcode", 20)

    parts = []
    if venue:
        parts.append(venue)

    street_line = street
    if number:
        street_line = f"{street_line}, nº {number}" if street_line else f"Nº {number}"
    if street_line:
        parts.append(street_line)

    if neighborhood:
        parts.append(f"Bairro {neighborhood}")

    city_state = city
    if state:
        city_state = f"{city} - {state}" if city else state
    if city_state:
        parts.append(city_state)

    if complement:
        parts.append(f"Complemento: {complement}")
    if reference:
        parts.append(f"Referência: {reference}")
    if postcode:
        parts.append(f"CEP {postcode}")

    # Compatibilidade: aceita o campo antigo caso o navegador ainda esteja em cache.
    if not parts:
        legacy = _text(data, "event_location", 500)
        if legacy:
            parts.append(legacy)

    return " • ".join(parts)[:500]


@require_POST
def create_order(request):
    if len(request.body) > 50_000:
        return _json(
            {"ok": False, "error": "Solicitação muito grande."},
            status=413,
        )

    try:
        data = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return _json(
            {"ok": False, "error": "Dados da solicitação inválidos."},
            status=400,
        )

    if _text(data, "website", 200):
        return _json(
            {"ok": False, "error": "Não foi possível validar a solicitação."},
            status=400,
        )

    name = _text(data, "name", 120)
    phone = _clean_phone(data.get("whatsapp"))
    event_theme = _text(data, "event_theme", 180)
    event_type = _text(data, "event_type", 30)
    ids = data.get("items") or []
    consent = bool(data.get("consent_whatsapp"))

    allowed_keep = {
        "Estrutura da montagem",
        "Painéis",
        "Mesas e mobiliário",
        "Arco de balões",
        "Flores e folhagens",
        "Iluminação",
        "Disposição dos elementos",
        "Paleta de cores",
        "Tema / personagens",
    }
    allowed_change = {
        "Trocar tema / personagens",
        "Mudar cores",
        "Alterar painéis",
        "Alterar balões",
        "Alterar mesas / mobiliário",
        "Adicionar nome / idade",
        "Adicionar flores",
        "Adicionar iluminação",
        "Redimensionar a montagem",
    }

    keep_choices = _choice_list(data, "keep_choices", allowed_keep)
    change_choices = _choice_list(data, "change_choices", allowed_change)

    guest_count = None
    raw_guests = str(data.get("guest_count") or "").strip()
    if raw_guests:
        try:
            guest_count = int(raw_guests)
            if guest_count < 1 or guest_count > 100000:
                raise ValueError
        except ValueError:
            return _json(
                {"ok": False, "error": "Quantidade de convidados inválida."},
                status=400,
            )

    event_latitude = _decimal_coordinate(data, "event_latitude", -90, 90)
    event_longitude = _decimal_coordinate(data, "event_longitude", -180, 180)
    event_location = _compose_event_location(data)

    if len(name) < 2:
        return _json({"ok": False, "error": "Informe seu nome."}, status=400)

    if not 10 <= len(phone) <= 13:
        return _json(
            {"ok": False, "error": "Informe um WhatsApp válido com DDD."},
            status=400,
        )

    if len(event_theme) < 2:
        return _json(
            {"ok": False, "error": "Informe o tema real da sua festa."},
            status=400,
        )

    valid_event_types = {choice[0] for choice in Order.EVENT_TYPE_CHOICES}
    if event_type and event_type not in valid_event_types:
        return _json(
            {"ok": False, "error": "Tipo de evento inválido."},
            status=400,
        )

    if not consent:
        return _json(
            {
                "ok": False,
                "error": "Autorize o contato pelo WhatsApp para enviar a solicitação.",
            },
            status=400,
        )

    if not isinstance(ids, list) or not ids:
        return _json(
            {"ok": False, "error": "Escolha pelo menos uma inspiração."},
            status=400,
        )

    if len(ids) > 10:
        return _json(
            {"ok": False, "error": "Selecione no máximo 10 inspirações por solicitação."},
            status=400,
        )

    try:
        clean_ids = list(dict.fromkeys(int(x) for x in ids))
    except (TypeError, ValueError):
        return _json(
            {"ok": False, "error": "Seleção de inspirações inválida."},
            status=400,
        )

    decos_by_id = {
        d.id: d
        for d in Decoration.objects.filter(id__in=clean_ids, active=True)
    }
    decos = [decos_by_id[i] for i in clean_ids if i in decos_by_id]

    if len(decos) != len(clean_ids):
        return _json(
            {
                "ok": False,
                "error": (
                    "Uma inspiração selecionada não está mais disponível. "
                    "Atualize a página e escolha novamente."
                ),
            },
            status=409,
        )

    event_date = None
    raw_date = _text(data, "event_date", 20)
    if raw_date:
        try:
            event_date = date.fromisoformat(raw_date)
        except ValueError:
            return _json(
                {"ok": False, "error": "Data do evento inválida."},
                status=400,
            )

        if event_date < date.today():
            return _json(
                {"ok": False, "error": "A data do evento não pode estar no passado."},
                status=400,
            )

    celebrant_age = None
    raw_age = _text(data, "celebrant_age", 4)
    if raw_age:
        try:
            celebrant_age = int(raw_age)
            if celebrant_age < 0 or celebrant_age > 130:
                raise ValueError
        except ValueError:
            return _json(
                {"ok": False, "error": "Idade inválida."},
                status=400,
            )

    with transaction.atomic():
        order = Order.objects.create(
            customer_name=name,
            customer_whatsapp=phone,
            event_type=event_type,
            event_theme=event_theme,
            celebrant_name=_text(data, "celebrant_name", 120),
            celebrant_age=celebrant_age,
            event_date=event_date,
            event_location=event_location,
            event_venue=_text(data, "event_venue", 120),
            event_city=_text(data, "event_city", 120),
            event_state=_text(data, "event_state", 80),
            event_neighborhood=_text(data, "event_neighborhood", 120),
            event_street=_text(data, "event_street", 180),
            event_number=_text(data, "event_number", 40),
            event_complement=_text(data, "event_complement", 120),
            event_reference=_text(data, "event_reference", 180),
            event_postcode=_text(data, "event_postcode", 20),
            event_latitude=event_latitude,
            event_longitude=event_longitude,
            guest_count=guest_count,
            keep_choices=keep_choices,
            change_choices=change_choices,
            keep_details=_text(data, "keep_details", 3000),
            change_details=_text(data, "change_details", 3000),
            notes=_text(data, "notes", 2500),
            consent_whatsapp=consent,
        )

        total = Decimal("0")
        for deco in decos:
            OrderItem.objects.create(
                order=order,
                decoration=deco,
                title_snapshot=deco.title,
                unit_price_snapshot=deco.price,
                quantity=1,
            )
            total += deco.price

        order.total_reference = total
        order.save(update_fields=["total_reference", "updated_at"])

    site = SiteSettings.current()
    message = format_order(order)

    fallback_number = (
        site.decorator_one_whatsapp
        or site.decorator_two_whatsapp
    )
    owner_link = (
        wa_link(fallback_number, message)
        if fallback_number
        else ""
    )

    return _json(
        {
            "ok": True,
            "order_code": order.code,
            "status": order.status,
            "total_reference": str(order.total_reference),
            "owner_whatsapp_link": owner_link,
            "whatsapp_message": message,
            # Compatibilidade com JavaScript antigo.
            "whatsapp_message_encoded": quote(message, safe=""),
            # Fluxo novo: o navegador transporta somente uma rota ASCII curta.
            "whatsapp_routes": {
                "aline": f"/api/orders/{order.code}/whatsapp/aline/",
                "erika": f"/api/orders/{order.code}/whatsapp/erika/",
            },
            "delivery_mode": "server-side-whatsapp-handoff",
        },
        status=201,
    )


@require_GET
@never_cache
def order_status(request, code):
    try:
        order = Order.objects.only(
            "code",
            "status",
            "total_reference",
            "updated_at",
        ).get(code=code)
    except Order.DoesNotExist:
        return _json(
            {"ok": False, "error": "Solicitação não encontrada."},
            status=404,
        )

    return _json({
        "ok": True,
        "code": order.code,
        "status": order.get_status_display(),
        "total_reference": str(order.total_reference),
        "updated_at": order.updated_at.isoformat(),
    })
