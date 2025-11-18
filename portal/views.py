from decimal import Decimal

from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect, render

from accounts.models import Employee

from .forms import ClientForm, OrderForm, OrderItemFormSet
from .models import InventoryItem, Order


def index(request):
    active_statuses = [
        Order.Status.DRAFT,
        Order.Status.IN_PROGRESS,
        Order.Status.ON_HOLD,
    ]
    active_orders_count = Order.objects.filter(status__in=active_statuses).count()
    done_orders_count = Order.objects.filter(status=Order.Status.DONE).count()
    cancelled_orders_count = Order.objects.filter(status=Order.Status.CANCELLED).count()

    recent_orders = (
        Order.objects.select_related("client")
        .prefetch_related("items")
        .order_by("-created_at")[:5]
    )
    low_stock = InventoryItem.objects.order_by("quantity_on_hand")[:5]

    context = {
        "active_orders_count": active_orders_count,
        "done_orders_count": done_orders_count,
        "cancelled_orders_count": cancelled_orders_count,
        "recent_orders": recent_orders,
        "low_stock": low_stock,
    }
    return render(request, "portal/index.html", context)


def order(request):
    return render(request, "portal/order.html")


def wizard(request):
    if request.method == "POST":
        client_form = ClientForm(request.POST, prefix="client")
        order_form = OrderForm(request.POST, prefix="order")
        item_formset = OrderItemFormSet(request.POST, queryset=OrderItemFormSet.model.objects.none(), prefix="items")

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

            messages.success(request, "Заказ сохранён")
            return redirect("portal:index")
        messages.error(request, "Исправьте ошибки в форме")
    else:
        client_form = ClientForm(prefix="client")
        order_form = OrderForm(prefix="order")
        item_formset = OrderItemFormSet(queryset=OrderItemFormSet.model.objects.none(), prefix="items")

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
