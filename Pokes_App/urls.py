from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('login', views.login, name='login'),
    path('logout',views.logout, name='logout'),
    path('registro', views.new_user, name='registro'),
    path('admin', views.admin, name = 'admin'),
    path('perfil/<int:id_user>/edit',views.edit_perfil, name = 'editar_perfil'),
    path('poke/<int:id_user>/add', views.give_poked, name = 'give_poked')
]