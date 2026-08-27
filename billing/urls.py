from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('claims/', views.claims_list, name='claims_list'),

    path('', views.patient_list, name='patient_list'),
    path('new/', views.patient_create, name='patient_create'),
    path('<int:pk>/', views.patient_detail, name='patient_detail'),
    path('<int:pk>/edit/', views.patient_edit, name='patient_edit'),
    path('claims/new/', views.claim_create, name='claim_create'),
]