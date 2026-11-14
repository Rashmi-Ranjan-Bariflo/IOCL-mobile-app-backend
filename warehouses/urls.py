from django.urls import path
from .views import (
    WarehouseListCreateAPIView,
    WarehouseDetailAPIView,
    WarehouseZoneListCreateAPIView,
    WarehouseItemListCreateAPIView,
    WarehouseItemDetailAPIView,
    WarehouseStockListAPIView,
    WarehouseStockMovementListAPIView,
    WarehouseStockInAPIView,
    WarehouseDeployAPIView,
    WarehouseReturnAPIView,
    WarehouseStockOutAPIView,
    WarehouseAdjustmentAPIView,
)

urlpatterns = [
    # Warehouse
    path("", WarehouseListCreateAPIView.as_view(), name="warehouse-list-create"),
    path("<int:pk>/", WarehouseDetailAPIView.as_view(), name="warehouse-detail"),

    # Zone
    path("zones/", WarehouseZoneListCreateAPIView.as_view(), name="warehouse-zone-list-create"),

    # Item
    path("items/", WarehouseItemListCreateAPIView.as_view(), name="warehouse-item-list-create"),
    path("items/<int:pk>/", WarehouseItemDetailAPIView.as_view(), name="warehouse-item-detail"),

    # Stock
    path("stocks/", WarehouseStockListAPIView.as_view(), name="warehouse-stock-list"),

    # Movements list
    path("movements/", WarehouseStockMovementListAPIView.as_view(), name="warehouse-movement-list"),

    # Actions
    path("stock-in/", WarehouseStockInAPIView.as_view(), name="warehouse-stock-in"),
    path("deploy/", WarehouseDeployAPIView.as_view(), name="warehouse-deploy"),
    path("return/", WarehouseReturnAPIView.as_view(), name="warehouse-return"),
    path("stock-out/", WarehouseStockOutAPIView.as_view(), name="warehouse-stock-out"),
    path("adjustment/", WarehouseAdjustmentAPIView.as_view(), name="warehouse-adjustment"),
]