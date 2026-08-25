import json
from datetime import date
from decimal import Decimal
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from catalog.models import Decoration, SiteSettings
from .models import Order, OrderItem
from .whatsapp import format_order, wa_link


@require_GET
def health(request):
    return JsonResponse({"ok": True, "service": "aline-erica-decor", "mode": "free-whatsapp-link"})


def _clean_phone(value):
    return "".join(ch for ch in (value or "") if ch.isdigit())


def _text(data, key, limit):
    return (data.get(key) or "").strip()[:limit]


@require_POST
def create_order(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"ok": False, "error": "Dados da solicitação inválidos."}, status=400)

    name = _text(data, "name", 120)
    phone = _clean_phone(data.get("whatsapp"))
    event_theme = _text(data, "event_theme", 180)
    ids = data.get("items") or []

    if len(name) < 2:
        return JsonResponse({"ok": False, "error": "Informe seu nome."}, status=400)
    if len(phone) < 10:
        return JsonResponse({"ok": False, "error": "Informe um WhatsApp válido com DDD."}, status=400)
    if len(event_theme) < 2:
        return JsonResponse({"ok": False, "error": "Informe o tema real da sua festa."}, status=400)
    if not isinstance(ids, list) or not ids:
        return JsonResponse({"ok": False, "error": "Escolha pelo menos uma inspiração."}, status=400)

    try:
        clean_ids = list(dict.fromkeys(int(x) for x in ids))
    except (TypeError, ValueError):
        return JsonResponse({"ok": False, "error": "Seleção de inspirações inválida."}, status=400)

    decos_by_id = {d.id: d for d in Decoration.objects.filter(id__in=clean_ids, active=True)}
    decos = [decos_by_id[i] for i in clean_ids if i in decos_by_id]
    if not decos:
        return JsonResponse({"ok": False, "error": "Nenhuma inspiração válida foi selecionada."}, status=400)

    event_date = None
    raw_date = data.get("event_date") or ""
    if raw_date:
        try:
            event_date = date.fromisoformat(raw_date)
        except ValueError:
            return JsonResponse({"ok": False, "error": "Data do evento inválida."}, status=400)

    celebrant_age = None
    raw_age = str(data.get("celebrant_age") or "").strip()
    if raw_age:
        try:
            celebrant_age = int(raw_age)
            if celebrant_age < 0 or celebrant_age > 130:
                raise ValueError
        except ValueError:
            return JsonResponse({"ok": False, "error": "Idade inválida."}, status=400)

    with transaction.atomic():
        order = Order.objects.create(
            customer_name=name,
            customer_whatsapp=phone,
            event_type=_text(data, "event_type", 30),
            event_theme=event_theme,
            celebrant_name=_text(data, "celebrant_name", 120),
            celebrant_age=celebrant_age,
            event_date=event_date,
            event_location=_text(data, "event_location", 220),
            keep_details=_text(data, "keep_details", 3000),
            change_details=_text(data, "change_details", 3000),
            notes=_text(data, "notes", 2500),
            consent_whatsapp=bool(data.get("consent_whatsapp")),
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

    # Compatibilidade com clientes antigos em cache:
    # se uma versão antiga do JavaScript ainda tentar usar owner_whatsapp_link,
    # ela será direcionada para a Aline — nunca para o número pessoal antigo.
    fallback_number = site.decorator_one_whatsapp or site.decorator_two_whatsapp
    owner_link = wa_link(fallback_number, message) if fallback_number else ""

    return JsonResponse({
        "ok": True,
        "order_code": order.code,
        "status": order.status,
        "total_reference": str(order.total_reference),
        "owner_whatsapp_link": owner_link,
        "whatsapp_message": message,
        "delivery_mode": "free_whatsapp_selector",
    }, status=201)


@require_GET
def order_status(request, code):
    try:
        order = Order.objects.get(code=code)
    except Order.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Solicitação não encontrada."}, status=404)
    return JsonResponse({
        "ok": True,
        "code": order.code,
        "customer_name": order.customer_name,
        "status": order.get_status_display(),
        "event_theme": order.event_theme,
        "total_reference": str(order.total_reference),
        "updated_at": order.updated_at.isoformat(),
    })
