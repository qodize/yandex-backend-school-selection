from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from delivery import views

urlpatterns = [
    path('couriers', views.CouriersList.as_view()),
    path('couriers/<int:pk>', views.CourierDetail.as_view()),
    path('orders', views.OrdersList.as_view()),
    path('orders/assign', views.OrderAssign.as_view()),
    path('orders/complete', views.OrderComplete.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)
