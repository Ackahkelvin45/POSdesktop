from django.urls import  path
from .views import CreateInventoryLogView,IventoryLogListView,ProductQuantityView,EditInventoryLogView,UndoInventoryLogView

app_name='inventory'

urlpatterns =[
        path('create/', CreateInventoryLogView.as_view(), name='createinventorylog'),
        path('list/', IventoryLogListView.as_view(), name='inventorylist'),
        path('get-product-quantity/<int:product_id>/',ProductQuantityView.as_view(), name='get_product_quantity'),
        path("edit/<int:pk>/", EditInventoryLogView.as_view(), name="editinventory"),
        path('logs/<int:pk>/undo/', UndoInventoryLogView.as_view(), name='undo_log'),


]



