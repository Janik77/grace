from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('accounts.urls')),
    path('', include('portal.urls')),  # Django сам зарегистрирует "portal" через app_name
]
