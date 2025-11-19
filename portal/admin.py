from django.contrib import admin

from .models import Client, Expense, InventoryItem, InventoryMovement, Order, OrderItem


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "address", "contact_person", "email", "created_at")
    search_fields = ("name", "phone", "address", "contact_person", "email")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "client",
        "status",
        "is_locked",
        "due_date",
        "total_amount",
        "created_at",
    )
    list_filter = ("status", "due_date", "client", "is_locked")
    search_fields = ("title", "description", "client__name")
    date_hierarchy = "due_date"
    inlines = [OrderItemInline]


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = (
        "sku",
        "name",
        "category",
        "base_unit",
        "quantity_on_hand",
        "package_size",
        "default_unit_price",
        "location",
        "updated_at",
    )
    search_fields = ("sku", "name", "location", "category")
    list_filter = ("base_unit", "category")


@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
    list_display = ("item", "direction", "quantity", "reason", "created_at")
    list_filter = ("direction", "created_at")


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("supplier_name", "expense_date", "amount", "created_at")
    list_filter = ("expense_date",)
    search_fields = ("supplier_name", "description")
