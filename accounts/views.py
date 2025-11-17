from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from .forms import LoginForm

@require_http_methods(["GET", "POST"])
def login_view(request):
    # Если пользователь уже вошёл — сразу на профиль
    if request.user.is_authenticated:
        return redirect("accounts:profile")

    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data["email_or_username"].strip()
        password = form.cleaned_data["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if not form.cleaned_data.get("remember_me"):
                request.session.set_expiry(0)
            messages.success(request, "Добро пожаловать!")
            return redirect("accounts:profile")  # ✅ после входа — профиль
        messages.error(request, "Неверный e-mail или пароль.")

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "Вы вышли из системы.")
    return redirect("accounts:login")


@login_required
def profile_view(request):
    return render(request, "accounts/profile.html")
