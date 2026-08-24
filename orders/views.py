import json
from decimal import Decimal
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from catalog.models import Decoration, SiteSettings
from .models import Order, OrderItem
from .whatsapp import format_order, customer_ack, send_text, wa_link

@require_GET
def health(request):
    return JsonResponse({"ok": True, "service": "catalogo-decor"})

def _clean_phone(value):
    return "".join(ch for ch in (value or "") if ch.isdigit())

@require_POST
def create_order(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"ok": False, "error": "JSON inválido."}, status=400)

    name = (data.get("name") or "").strip()
    phone = _clean_phone(data.get("whatsapp"))
    ids = data.get("items") or []
    consent = bool(data.get("consent_whatsapp"))

    if len(name) < 2:
        return JsonResponse({"ok": False, "error": "Informe seu nome."}, status=400)
    if len(phone) < 10:
        return JsonResponse({"ok": False, "error": "Informe um WhatsApp válido com DDD."}, status=400)
    if not ids:
        return JsonResponse({"ok": False, "error": "Escolha pelo menos uma decoração."}, status=400)

    decos = list(Decoration.objects.filter(id__in=ids, active=True))
    if not decos:
        return JsonResponse({"ok": False, "error": "Nenhuma decoração válida foi selecionada."}, status=400)

    event_date = data.get("event_date") or None
    notes = (data.get("notes") or "").strip()[:2000]

    with transaction.atomic():
        order = Order.objects.create(
            customer_name=name,
            customer_whatsapp=phone,
            event_date=event_date,
            notes=notes,
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
    owner_link = wa_link(site.owner_whatsapp, message)

    owner_result = {"ok": False}
    if site.owner_whatsapp:
        owner_result = send_text(site.owner_whatsapp, message)
        if owner_result.get("ok"):
            order.owner_notified = True

    customer_result = {"ok": False}
    if consent:
        customer_result = send_text(phone, customer_ack(order))
        if customer_result.get("ok"):
            order.customer_notified = True

    if order.owner_notified or order.customer_notified:
        order.save(update_fields=["owner_notified", "customer_notified", "updated_at"])

    return JsonResponse({
        "ok": True,
        "order_code": order.code,
        "status": order.status,
        "total_reference": str(order.total_reference),
        "owner_whatsapp_link": owner_link,
        "automation": {
            "owner": owner_result.get("ok", False),
            "customer": customer_result.get("ok", False),
        }
    }, status=201)

@require_GET
def order_status(request, code):
    try:
        order = Order.objects.get(code=code)
    except Order.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Pedido não encontrado."}, status=404)
    return JsonResponse({
        "ok": True,
        "code": order.code,
        "customer_name": order.customer_name,
        "status": order.get_status_display(),
        "total_reference": str(order.total_reference),
        "updated_at": order.updated_at.isoformat(),
    })
