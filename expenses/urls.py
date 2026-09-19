from django.urls import path
from django.contrib.auth.views import LoginView
from . import views
from .forms import LoginForm

urlpatterns = [
    path('', views.expense_list, name='expense_list'),
    path('add/', views.add_expense, name='add_expense'),
    path('edit/<int:pk>/', views.edit_expense, name='edit_expense'),
    path('delete/<int:pk>/', views.delete_expense, name='delete_expense'),
    path('stats/', views.stats, name='stats'),
    path('register/', views.register, name='register'),
    path('login/', LoginView.as_view(template_name='expenses/login.html', authentication_form=LoginForm), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('pricing/', views.pricing, name='pricing'),
    path('pricing/success/', views.checkout_success, name='checkout_success'),
    path('paddle/webhook/', views.paddle_webhook, name='paddle_webhook'),
]