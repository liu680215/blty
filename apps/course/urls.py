from django.urls import path
from . import views

app_name = 'course'
urlpatterns = [
    path('', views.course_index, name='course_index'),
    path('<int:detail_id>', views.course_detail, name='course_detail'),
    path('course_order/<int:course_id>/', views.course_order, name='course_order'),
    path('course_order_key/', views.course_order_key, name="course_order_key"),
    path('notify_view/', views.notify_view, name='notify_view'),
]
