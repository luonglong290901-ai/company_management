from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    DashboardView, CompanyListView, CompanyDetailView, 
    CompanyCreateView, CompanyUpdateView, CompanyDeleteView,
    ContactCreateView, ContactUpdateView, ContactDeleteView
)

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', DashboardView.as_view(), name='dashboard'),
    path('companies/', CompanyListView.as_view(), name='company_list'),
    path('companies/<int:pk>/', CompanyDetailView.as_view(), name='company_detail'),
    path('companies/add/', CompanyCreateView.as_view(), name='company_add'),
    path('companies/<int:pk>/edit/', CompanyUpdateView.as_view(), name='company_edit'),
    path('companies/<int:pk>/delete/', CompanyDeleteView.as_view(), name='company_delete'),
    path('companies/<int:company_pk>/contacts/add/', ContactCreateView.as_view(), name='contact_add'),
    path('contacts/<int:pk>/edit/', ContactUpdateView.as_view(), name='contact_edit'),
    path('contacts/<int:pk>/delete/', ContactDeleteView.as_view(), name='contact_delete'),
]