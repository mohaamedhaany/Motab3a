from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('manager/', views.manager_dashboard, name='manager_dashboard'),
    path('settle/<int:order_id>/', views.settle_order, name='settle_order'),
    
    # الروابط الجديدة للتعديل والحذف
    path('edit/<int:order_id>/', views.edit_order, name='edit_order'),
    path('delete/<int:order_id>/', views.delete_order, name='delete_order'),
    
    path('login/', auth_views.LoginView.as_view(template_name='expenses/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('close-period/', views.close_period, name='close_period'),
]