import json
from datetime import date
from decimal import Decimal

from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_POST

from catalog.models import Decoration, SiteSettings
from .models import Order, OrderItem
from .whatsapp import format_order, wa_link


def _json(payload, *, status=200):
    response = JsonResponse(
        payload,
        status=status,
        json_dumps_params={"ensure_ascii": False},
    )
    response["Cache-Control"] = "no-store"
    return response


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
            event_location=_text(data, "event_location", 220),
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
            "delivery_mode": "free-whatsapp-selector",
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
