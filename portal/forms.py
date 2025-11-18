from django import forms
from django.forms import modelformset_factory

from .models import Client, Order, OrderItem


class ClientForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    class Meta:
        model = Client
        fields = ["name", "contact_person", "email", "phone", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 2}),
        }


class OrderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            css_class = "form-select" if field_name == "status" else "form-control"
            field.widget.attrs.setdefault("class", css_class)

    class Meta:
        model = Order
        fields = ["title", "description", "status", "due_date"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }


class OrderItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            css_class = "form-control"
            field.widget.attrs.setdefault("class", css_class)

    class Meta:
        model = OrderItem
        fields = ["title", "quantity", "unit_price", "comment"]
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 1}),
        }


OrderItemFormSet = modelformset_factory(
    OrderItem,
    form=OrderItemForm,
    extra=3,
    can_delete=True,
)
