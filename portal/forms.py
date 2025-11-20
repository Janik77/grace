from django import forms
from django.forms import formset_factory, modelformset_factory

from .models import Client, Expense, InventoryItem, Order, OrderItem


class ClientForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    class Meta:
        model = Client
        fields = ["name", "phone", "address"]
        widgets = {
            "address": forms.TextInput(attrs={"placeholder": "Адрес клиента"}),
        }


class OrderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            css_class = "form-select" if field_name == "status" else "form-control"
            field.widget.attrs.setdefault("class", css_class)

    class Meta:
        model = Order
        fields = ["title", "start_date", "end_date"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }


class OrderDetailForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            css_class = "form-select" if field_name == "status" else "form-control"
            field.widget.attrs.setdefault("class", css_class)

    class Meta:
        model = Order
        fields = ["title", "description", "status", "start_date", "end_date"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }


class OrderItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            css_class = "form-control"
            field.widget.attrs.setdefault("class", css_class)

    class Meta:
        model = OrderItem
        fields = ["title", "quantity", "unit_price"]


OrderItemFormSet = modelformset_factory(
    OrderItem,
    form=OrderItemForm,
    extra=1,
    can_delete=True,
)


class CalculatorSummaryForm(forms.Form):
    project_name = forms.CharField(
        required=False,
        label="Название расчёта",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Проект / заказ"}),
    )
    margin_percent = forms.DecimalField(
        required=False,
        min_value=0,
        max_digits=5,
        decimal_places=2,
        label="Наценка / налог, %",
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "value": "0"}),
    )
    notes = forms.CharField(
        required=False,
        label="Примечания",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    )


class CalculatorItemForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=InventoryItem.objects.order_by("name"),
        required=False,
        label="Материал",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    description = forms.CharField(
        required=False,
        label="Что считаем",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Баннер, плёнка…"}),
    )
    quantity = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        label="Кол-во",
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
    )
    unit_price = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0,
        label="Цена за ед.",
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
    )

    def clean(self):
        cleaned = super().clean()
        product = cleaned.get("product")
        description = cleaned.get("description")
        if product and not description:
            cleaned["description"] = product.name
        return cleaned


CalculatorItemFormSet = formset_factory(CalculatorItemForm, extra=3, can_delete=True)


class ExpenseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    class Meta:
        model = Expense
        fields = ["supplier_name", "expense_date", "amount", "attachment", "description"]
        widgets = {
            "expense_date": forms.DateInput(attrs={"type": "date"}),
        }
