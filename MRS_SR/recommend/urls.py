from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('rating/<m_id>', views.rating, name='rating'),
    path('signup/', views.signUp, name='signup'),
    path('login/', views.Login, name='login'),
    path('logout/', views.Logout, name='logout'),

]