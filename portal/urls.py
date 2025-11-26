# portal/urls.py
from django.urls import path
from . import views

app_name = "portal"  # ← вот это важно

urlpatterns = [
    path('', views.index, name='index'),
    path('order/', views.order, name='order'),
    path('wizard/', views.wizard, name='wizard'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('report/', views.report, name='report'),
    path('expenses/', views.expenses, name='expenses'),
    path('usage/', views.usage, name='usage'),
    path('inventory/', views.inventory, name='inventory'),
    path('help/', views.help_page, name='help'),
    path('directory/', views.directory, name='directory'),
    path('staff/', views.staff, name='staff'),
]
