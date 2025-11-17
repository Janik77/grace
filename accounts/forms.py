from django import forms

class LoginForm(forms.Form):
    email_or_username = forms.CharField(
        label="E-mail",
        widget=forms.TextInput(
            attrs={
                "class": "g-input",                 # наш класс
                "placeholder": "Введите e-mail или логин",
                "autocomplete": "username",
            }
        ),
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(
            attrs={
                "class": "g-input",                 # наш класс
                "autocomplete": "current-password",
            }
        ),
    )
    remember_me = forms.BooleanField(label="Запомнить меня", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # На всякий случай уберём то, что могло прийти из старых стилей
        for name in ("email_or_username", "password"):
            w = self.fields[name].widget
            classes = w.attrs.get("class", "").split()
            classes = [c for c in classes if c != "form-control"]
            w.attrs["class"] = "g-input " + " ".join(filter(None, classes))
