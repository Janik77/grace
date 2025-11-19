from django.db import models


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Client(TimestampedModel):
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=64, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name


class Order(TimestampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Черновик"
        IN_PROGRESS = "in_progress", "В работе"
        ON_HOLD = "on_hold", "На паузе"
        DONE = "done", "Завершён"
        CANCELLED = "cancelled", "Отменён"

    title = models.CharField(max_length=255)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="orders")
    description = models.TextField(blank=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.DRAFT)
    due_date = models.DateField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title


class OrderItem(TimestampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    title = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    comment = models.TextField(blank=True)

    class Meta:
        ordering = ["created_at"]

    @property
    def total(self) -> float:
        return float(self.quantity * self.unit_price)

    def __str__(self) -> str:
        return f"{self.title} ({self.quantity} x {self.unit_price})"


class InventoryItem(TimestampedModel):
    class Unit(models.TextChoices):
        METER = "m", "Метры"
        PIECE = "pcs", "Штуки"
        SHEET = "sheet", "Листы"
        SQUARE_METER = "sqm", "Кв. метры"

    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=150, blank=True)
    base_unit = models.CharField(max_length=10, choices=Unit.choices, default=Unit.PIECE)
    package_size = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Сколько базовых единиц в упаковке (например, 50 м в рулоне)",
    )
    package_unit_label = models.CharField(
        max_length=50,
        blank=True,
        help_text="Название упаковки: рулон, пачка, коробка…",
    )
    default_unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    quantity_on_hand = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    location = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.sku} — {self.name}"

    @property
    def package_count(self):
        if self.package_size:
            return float(self.quantity_on_hand) / float(self.package_size)
        return None

    def get_package_label(self) -> str:
        if self.package_unit_label:
            return self.package_unit_label
        return "упаковка"


class InventoryMovement(TimestampedModel):
    class Direction(models.TextChoices):
        IN = "in", "Приход"
        OUT = "out", "Расход"

    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name="movements")
    direction = models.CharField(max_length=3, choices=Direction.choices)
    quantity = models.IntegerField()
    reason = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        prefix = "+" if self.direction == self.Direction.IN else "-"
        return f"{prefix}{self.quantity} {self.item.sku}"
