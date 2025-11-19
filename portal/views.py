from decimal import Decimal

from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect, render

from accounts.models import Employee

from .forms import (
    CalculatorItemFormSet,
    CalculatorSummaryForm,
    ClientForm,
    OrderForm,
    OrderItemFormSet,
)
from .models import InventoryItem, Order, OrderItem


def index(request):
    status_cards = [
        {
            "key": Order.Status.DEVELOPMENT,
            "label": "В разработке",
            "description": "Макеты, расчёты",
            "accent": "primary",
        },
        {
            "key": Order.Status.OFFICE,
            "label": "В офисе",
            "description": "Подготовка документов",
            "accent": "info",
        },
        {
            "key": Order.Status.WORKSHOP,
            "label": "В цеху",
            "description": "Производство",
            "accent": "warning",
        },
        {
            "key": Order.Status.INSTALLATION,
            "label": "Монтаж",
            "description": "Выезды и монтаж",
            "accent": "secondary",
        },
        {
            "key": Order.Status.DONE,
            "label": "Завершено",
            "description": "Сданы клиенту",
            "accent": "success",
        },
    ]

    counts = {
        card["key"]: Order.objects.filter(status=card["key"]).count() for card in status_cards
    }
    for card in status_cards:
        card["count"] = counts.get(card["key"], 0)

    recent_orders = (
        Order.objects.select_related("client")
        .prefetch_related("items")
        .order_by("-created_at")[:5]
    )
    low_stock = InventoryItem.objects.order_by("quantity_on_hand")[:5]

    context = {
        "status_cards": status_cards,
        "recent_orders": recent_orders,
        "low_stock": low_stock,
    }
    return render(request, "portal/index.html", context)


def order(request):
    summary_form = CalculatorSummaryForm(prefix="summary")
    item_formset = CalculatorItemFormSet(prefix="items")
    line_results = []
    totals = None

    if request.method == "POST":
        summary_form = CalculatorSummaryForm(request.POST, prefix="summary")
        item_formset = CalculatorItemFormSet(request.POST, prefix="items")

        if summary_form.is_valid() and item_formset.is_valid():
            subtotal = Decimal("0")
            for form in item_formset:
                if form.cleaned_data and not form.cleaned_data.get("DELETE", False):
                    data = form.cleaned_data
                    product = data.get("product")
                    quantity = data.get("quantity")
                    unit_price = data.get("unit_price")
                    line_total = quantity * unit_price
                    subtotal += line_total

                    package_usage = None
                    if product and product.package_size:
                        packages = quantity / product.package_size
                        package_usage = {
                            "label": product.get_package_label(),
                            "size": product.package_size,
                            "packages": packages,
                        }

                    line_results.append(
                        {
                            "product": product,
                            "description": data.get("description") or (product.name if product else ""),
                            "quantity": quantity,
                            "unit_price": unit_price,
                            "line_total": line_total,
                            "package_usage": package_usage,
                        }
                    )

            margin_percent = summary_form.cleaned_data.get("margin_percent") or Decimal("0")
            percent_amount = subtotal * margin_percent / Decimal("100")
            grand_total = subtotal + percent_amount

            totals = {
                "subtotal": subtotal,
                "margin_percent": margin_percent,
                "percent_amount": percent_amount,
                "grand_total": grand_total,
            }
        else:
            messages.error(request, "Проверьте заполнение строк и параметров расчёта")

    context = {
        "summary_form": summary_form,
        "item_formset": item_formset,
        "line_results": line_results,
        "totals": totals,
    }
    return render(request, "portal/order.html", context)


def wizard(request):
    if request.method == "POST":
        action = request.POST.get("action", "save_full")
        client_form = ClientForm(request.POST, prefix="client")
        order_form = OrderForm(request.POST, prefix="order")
        item_formset = OrderItemFormSet(
            request.POST,
            queryset=OrderItem.objects.none(),
            prefix="items",
        )

        if action == "save_client":
            if client_form.is_valid():
                client = client_form.save()
                messages.success(
                    request,
                    f"Реквизиты клиента «{client.name}» сохранены. Заказ можно оформить позже.",
                )
                return redirect("portal:wizard")
            messages.error(request, "Проверьте заполнение реквизитов клиента")
        else:
            if all([client_form.is_valid(), order_form.is_valid(), item_formset.is_valid()]):
                with transaction.atomic():
                    client = client_form.save()
                    order = order_form.save(commit=False)
                    order.client = client
                    order.save()

                    total = Decimal("0")
                    for form in item_formset:
                        if form.cleaned_data and not form.cleaned_data.get("DELETE", False):
                            item = form.save(commit=False)
                            item.order = order
                            item.save()
                            total += item.quantity * item.unit_price

                    order.total_amount = total
                    order.save(update_fields=["total_amount"])

                messages.success(request, "Заказ сохранён и появится в отчёте")
                return redirect("portal:index")
            messages.error(request, "Исправьте ошибки в форме заказа")
    else:
        client_form = ClientForm(prefix="client")
        order_form = OrderForm(prefix="order")
        item_formset = OrderItemFormSet(queryset=OrderItem.objects.none(), prefix="items")

    context = {
        "client_form": client_form,
        "order_form": order_form,
        "item_formset": item_formset,
    }
    return render(request, "portal/wizard.html", context)


def help_page(request):
    return render(request, "portal/help.html")


def directory(request):
    return render(request, "portal/directory.html")


def staff(request):
    employees = (
        Employee.objects.select_related("main_position__department")
        .prefetch_related("skills")
        .order_by("full_name")
    )
    context = {"employees": employees}
    return render(request, "portal/staff.html", context)


def inventory(request):
    items = InventoryItem.objects.all()
    return render(request, "portal/inventory.html", {"items": items})
