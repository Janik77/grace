from datetime import date, datetime
from decimal import Decimal

from django.contrib import messages
from django.db import transaction
from django.db.models import F, Max, Min, Sum
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import Employee

from .forms import (
    CalculatorItemFormSet,
    CalculatorSummaryForm,
    ClientForm,
    DefectRecordForm,
    ExpenseForm,
    InventoryUsageForm,
    OrderDetailForm,
    OrderForm,
    OrderItemFormSet,
)
from .models import (
    DefectRecord,
    Expense,
    InventoryItem,
    InventoryUsage,
    Order,
    OrderItem,
)


def _normalize_to_date(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    return value


def _month_context(request, min_date, max_date):
    today = date.today()
    min_date = _normalize_to_date(min_date) or today
    max_date = _normalize_to_date(max_date) or today

    default_month = date(max_date.year, max_date.month, 1)
    month_param = request.GET.get("month")
    try:
        if month_param:
            year, month = [int(x) for x in month_param.split("-")]
            current_month = date(year, month, 1)
        else:
            current_month = default_month
    except (TypeError, ValueError):
        current_month = default_month

    min_month = date(min_date.year, min_date.month, 1)
    max_month = date(max_date.year, max_date.month, 1)

    if current_month < min_month:
        current_month = min_month
    if current_month > max_month:
        current_month = max_month

    if current_month.month == 12:
        month_end = date(current_month.year + 1, 1, 1)
    else:
        month_end = date(current_month.year, current_month.month + 1, 1)

    previous_month = None
    if current_month > min_month:
        if current_month.month == 1:
            previous_month = date(current_month.year - 1, 12, 1)
        else:
            previous_month = date(current_month.year, current_month.month - 1, 1)

    next_month = None
    if current_month < max_month:
        if current_month.month == 12:
            next_month = date(current_month.year + 1, 1, 1)
        else:
            next_month = date(current_month.year, current_month.month + 1, 1)

    month_slug = current_month.strftime("%Y-%m")
    month_label = current_month.strftime("%m.%Y")

    return {
        "month_start": current_month,
        "month_end": month_end,
        "previous_month": previous_month,
        "next_month": next_month,
        "month_slug": month_slug,
        "month_label": month_label,
    }


def index(request):
    order_bounds = Order.objects.aggregate(
        min_date=Min("created_at"), max_date=Max("created_at")
    )
    order_month = _month_context(
        request,
        order_bounds.get("min_date"),
        order_bounds.get("max_date"),
    )

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

    status_summary = {
        "total": Order.objects.count(),
        "active": sum(counts.values()) - counts.get(Order.Status.DONE, 0),
        "office": counts.get(Order.Status.OFFICE, 0),
        "workshop": counts.get(Order.Status.WORKSHOP, 0) + counts.get(Order.Status.INSTALLATION, 0),
        "done": counts.get(Order.Status.DONE, 0),
    }

    recent_orders = (
        Order.objects.select_related("client")
        .prefetch_related("items")
        .filter(
            created_at__date__gte=order_month["month_start"],
            created_at__date__lt=order_month["month_end"],
        )
        .order_by("-created_at")
    )
    low_stock = InventoryItem.objects.order_by("quantity_on_hand")[:5]

    context = {
        "status_cards": status_cards,
        "status_summary": status_summary,
        "recent_orders": recent_orders,
        "low_stock": low_stock,
        "order_month": order_month,
    }
    return render(request, "portal/index.html", context)


def report(request):
    order_bounds = Order.objects.aggregate(
        min_date=Min("created_at"), max_date=Max("created_at")
    )
    expense_bounds = Expense.objects.aggregate(
        min_date=Min("expense_date"), max_date=Max("expense_date")
    )
    bounds = [
        _normalize_to_date(order_bounds.get("min_date")),
        _normalize_to_date(expense_bounds.get("min_date")),
    ]
    bounds_max = [
        _normalize_to_date(order_bounds.get("max_date")),
        _normalize_to_date(expense_bounds.get("max_date")),
    ]
    min_date = min([d for d in bounds if d]) if any(bounds) else None
    max_date = max([d for d in bounds_max if d]) if any(bounds_max) else None
    month_ctx = _month_context(request, min_date, max_date)

    income_qs = (
        Order.objects.select_related("client")
        .filter(
            created_at__date__gte=month_ctx["month_start"],
            created_at__date__lt=month_ctx["month_end"],
        )
        .order_by("-created_at")
    )
    income_total = income_qs.aggregate(total=Sum("total_amount"))
    income_total = income_total.get("total") or Decimal("0")

    expense_qs = (
        Expense.objects.filter(
            expense_date__gte=month_ctx["month_start"],
            expense_date__lt=month_ctx["month_end"],
        )
        .order_by("-expense_date")
    )
    expense_total = expense_qs.aggregate(total=Sum("amount"))
    expense_total = expense_total.get("total") or Decimal("0")

    context = {
        "income_total": income_total,
        "expense_total": expense_total,
        "net_total": income_total - expense_total,
        "income_rows": income_qs,
        "expense_rows": expense_qs,
        "report_month": month_ctx,
    }
    return render(request, "portal/report.html", context)


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
            if all([client_form.is_valid(), order_form.is_valid()]):
                with transaction.atomic():
                    client = client_form.save()
                    order = order_form.save(commit=False)
                    order.client = client
                    order.save()

                messages.success(
                    request,
                    "Заказ сохранён. Добавьте детали и позиции из карточки заказа.",
                )
                return redirect("portal:order_detail", pk=order.pk)
            messages.error(request, "Исправьте ошибки в форме заказа")
    else:
        client_form = ClientForm(prefix="client")
        order_form = OrderForm(prefix="order")

    context = {
        "client_form": client_form,
        "order_form": order_form,
    }
    return render(request, "portal/wizard.html", context)


def order_detail(request, pk):
    order = get_object_or_404(
        Order.objects.select_related("client"),
        pk=pk,
    )
    can_edit = order.can_edit(request.user)

    if request.method == "POST" and request.POST.get("action") == "toggle_lock":
        if request.user.is_superuser:
            order.is_locked = not order.is_locked
            order.save(update_fields=["is_locked"])
            state = "разблокирован" if not order.is_locked else "заблокирован"
            messages.success(request, f"Заказ {state} для редактирования")
        else:
            messages.error(request, "Недостаточно прав для изменения статуса блокировки")
        return redirect("portal:order_detail", pk=order.pk)

    if request.method == "POST":
        if not can_edit:
            messages.warning(request, "Заказ заблокирован. Обратитесь к администратору.")
            return redirect("portal:order_detail", pk=order.pk)

        order_form = OrderDetailForm(request.POST, instance=order, prefix="order")
        item_formset = OrderItemFormSet(
            request.POST,
            queryset=order.items.all(),
            prefix="items",
        )

        if order_form.is_valid() and item_formset.is_valid():
            order_form.save()
            instances = item_formset.save(commit=False)
            for obj in item_formset.deleted_objects:
                obj.delete()
            for obj in instances:
                obj.order = order
                obj.save()

            total = (
                order.items.all()
                .aggregate(total=Sum(F("quantity") * F("unit_price")))
                .get("total")
                or Decimal("0")
            )
            order.total_amount = total
            order.save(update_fields=["total_amount"])

            messages.success(request, "Изменения сохранены")
            return redirect("portal:order_detail", pk=order.pk)
        else:
            messages.error(request, "Проверьте форму заказа")
    else:
        order_form = OrderDetailForm(instance=order, prefix="order")
        item_formset = OrderItemFormSet(queryset=order.items.all(), prefix="items")

    if not can_edit:
        for field in order_form.fields.values():
            field.widget.attrs["disabled"] = True
        for form in item_formset:
            for field in form.fields.values():
                field.widget.attrs["disabled"] = True
            if "DELETE" in form.fields:
                form.fields["DELETE"].widget.attrs["disabled"] = True

    context = {
        "order": order,
        "order_form": order_form,
        "item_formset": item_formset,
        "can_edit": can_edit,
    }
    return render(request, "portal/order_detail.html", context)


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


def expenses(request):
    expense_bounds = Expense.objects.aggregate(
        min_date=Min("expense_date"), max_date=Max("expense_date")
    )
    expense_month = _month_context(
        request,
        expense_bounds.get("min_date"),
        expense_bounds.get("max_date"),
    )

    expenses_qs = (
        Expense.objects.filter(
            expense_date__gte=expense_month["month_start"],
            expense_date__lt=expense_month["month_end"],
        )
        .order_by("-expense_date")
    )
    if request.method == "POST":
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Расход добавлен")
            return redirect("portal:expenses")
        messages.error(request, "Проверьте форму расхода")
    else:
        form = ExpenseForm(initial={"expense_date": date.today()})

    context = {"form": form, "expenses": expenses_qs, "expense_month": expense_month}
    return render(request, "portal/expenses.html", context)


def usage(request):
    usage_qs = InventoryUsage.objects.select_related("item", "project")
    usage_bounds = usage_qs.aggregate(
        min_date=Min("usage_date"), max_date=Max("usage_date")
    )
    usage_month = _month_context(
        request,
        usage_bounds.get("min_date"),
        usage_bounds.get("max_date"),
    )

    filtered_usages = usage_qs.filter(
        usage_date__gte=usage_month["month_start"],
        usage_date__lt=usage_month["month_end"],
    ).order_by("-usage_date", "-created_at")

    if request.method == "POST":
        form = InventoryUsageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Расход материалов сохранён")
            return redirect("portal:usage")
        messages.error(request, "Проверьте заполнение расхода")
    else:
        form = InventoryUsageForm(initial={"usage_date": date.today()})

    context = {
        "form": form,
        "usages": filtered_usages,
        "usage_month": usage_month,
    }
    return render(request, "portal/usage.html", context)


def defects(request):
    defect_qs = DefectRecord.objects.select_related("project", "responsible")

    if request.method == "POST":
        form = DefectRecordForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Брак/замечание сохранены")
            return redirect("portal:defects")
        messages.error(request, "Проверьте форму учёта брака")
    else:
        form = DefectRecordForm(initial={"report_date": date.today()})

    defects_list = defect_qs.order_by("-report_date", "-created_at")
    context = {
        "form": form,
        "defects": defects_list,
    }
    return render(request, "portal/defects.html", context)
