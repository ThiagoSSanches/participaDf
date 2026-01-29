from django.urls import path
from .views import ClassificarPedidoView

urlpatterns = [
    path('classificar-pedido/', ClassificarPedidoView.as_view(), name='classificar-pedido'),
]