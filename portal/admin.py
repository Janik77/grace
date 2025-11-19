from django.contrib import admin

from .models import Client, InventoryItem, InventoryMovement, Order, OrderItem


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_person", "email", "phone", "created_at")
    search_fields = ("name", "contact_person", "email", "phone")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("title", "client", "status", "due_date", "total_amount", "created_at")
    list_filter = ("status", "due_date", "client")
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
