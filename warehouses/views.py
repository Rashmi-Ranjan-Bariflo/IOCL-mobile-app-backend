from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404

from .models import (
    Warehouse,
    WarehouseZone,
    WarehouseItem,
    WarehouseStock,
    WarehouseStockMovement,
)
from .serializers import (
    WarehouseSerializer,
    WarehouseZoneSerializer,
    WarehouseItemSerializer,
    WarehouseStockSerializer,
    WarehouseStockMovementSerializer,
    WarehouseStockInSerializer,
    WarehouseDeploySerializer,
    WarehouseReturnSerializer,
    WarehouseStockOutSerializer,
    WarehouseAdjustmentSerializer,
)


# =========================================================
# Warehouse CRUD
# =========================================================
class WarehouseListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Warehouse.objects.filter(user=request.user, is_active=True)
        warehouse_type = request.query_params.get("warehouse_type")
        if warehouse_type:
            qs = qs.filter(warehouse_type=warehouse_type.upper())
        search = request.query_params.get("search")
        if search:
            qs = qs.filter(name__icontains=search) | qs.filter(code__icontains=search)
        serializer = WarehouseSerializer(qs, many=True)
        return Response(
            {
                "success": True,
                "message": "Warehouses retrieved successfully.",
                "count": qs.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = WarehouseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        warehouse = serializer.save(user=request.user)
        return Response(
            {
                "success": True,
                "message": "Warehouse created successfully.",
                "data": WarehouseSerializer(warehouse).data,
            },
            status=status.HTTP_201_CREATED,
        )


class WarehouseDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        return get_object_or_404(Warehouse, pk=pk, user=user)

    def get(self, request, pk):
        warehouse = self.get_object(pk, request.user)
        return Response(
            {
                "success": True,
                "message": "Warehouse retrieved successfully.",
                "data": WarehouseSerializer(warehouse).data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        warehouse = self.get_object(pk, request.user)
        serializer = WarehouseSerializer(warehouse, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(
            {
                "success": True,
                "message": "Warehouse updated successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        warehouse = self.get_object(pk, request.user)
        serializer = WarehouseSerializer(warehouse, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(
            {
                "success": True,
                "message": "Warehouse updated successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, pk):
        warehouse = self.get_object(pk, request.user)
        warehouse.is_active = False
        warehouse.save(update_fields=["is_active", "updated_at"])
        return Response(
            {
                "success": True,
                "message": f"Warehouse '{warehouse.name}' deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# Warehouse Zone
# =========================================================
class WarehouseZoneListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = WarehouseZone.objects.filter(warehouse__user=request.user, is_active=True)
        warehouse_id = request.query_params.get("warehouse")
        if warehouse_id:
            qs = qs.filter(warehouse_id=warehouse_id)
        serializer = WarehouseZoneSerializer(qs, many=True)
        return Response(
            {
                "success": True,
                "message": "Zones retrieved successfully.",
                "count": qs.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = WarehouseZoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        warehouse = serializer.validated_data["warehouse"]
        if warehouse.user_id != request.user.id:
            return Response(
                {"success": False, "message": "Warehouse does not belong to you."},
                status=status.HTTP_403_FORBIDDEN,
            )
        zone = serializer.save()
        return Response(
            {
                "success": True,
                "message": "Zone created successfully.",
                "data": WarehouseZoneSerializer(zone).data,
            },
            status=status.HTTP_201_CREATED,
        )


# =========================================================
# Warehouse Item
# =========================================================
class WarehouseItemListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = WarehouseItem.objects.filter(user=request.user, is_active=True)
        search = request.query_params.get("search")
        if search:
            qs = qs.filter(name__icontains=search) | qs.filter(code__icontains=search)
        equipment_id = request.query_params.get("equipment")
        if equipment_id:
            qs = qs.filter(equipment_id=equipment_id)
        serializer = WarehouseItemSerializer(qs, many=True)
        return Response(
            {
                "success": True,
                "message": "Items retrieved successfully.",
                "count": qs.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = WarehouseItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = serializer.save(user=request.user)
        return Response(
            {
                "success": True,
                "message": "Item created successfully.",
                "data": WarehouseItemSerializer(item).data,
            },
            status=status.HTTP_201_CREATED,
        )


class WarehouseItemDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        return get_object_or_404(WarehouseItem, pk=pk, user=user)

    def get(self, request, pk):
        item = self.get_object(pk, request.user)
        return Response(
            {
                "success": True,
                "message": "Item retrieved successfully.",
                "data": WarehouseItemSerializer(item).data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        item = self.get_object(pk, request.user)
        serializer = WarehouseItemSerializer(item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(
            {
                "success": True,
                "message": "Item updated successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, pk):
        item = self.get_object(pk, request.user)
        item.is_active = False
        item.save(update_fields=["is_active", "updated_at"])
        return Response(
            {"success": True, "message": f"Item '{item.name}' deleted successfully."},
            status=status.HTTP_200_OK,
        )


# =========================================================
# Warehouse Stock list
# =========================================================
class WarehouseStockListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = WarehouseStock.objects.filter(warehouse__user=request.user).select_related(
            "item", "warehouse", "zone"
        )
        warehouse_id = request.query_params.get("warehouse")
        if warehouse_id:
            qs = qs.filter(warehouse_id=warehouse_id)
        item_id = request.query_params.get("item")
        if item_id:
            qs = qs.filter(item_id=item_id)
        warehouse_type = request.query_params.get("warehouse_type")
        if warehouse_type:
            qs = qs.filter(warehouse__warehouse_type=warehouse_type.upper())
        serializer = WarehouseStockSerializer(qs, many=True)
        return Response(
            {
                "success": True,
                "message": "Stock retrieved successfully.",
                "count": qs.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# Stock movements list
# =========================================================
class WarehouseStockMovementListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = (
            WarehouseStockMovement.objects.filter(user=request.user)
            .select_related(
                "item", "from_warehouse", "to_warehouse", "equipment", "treatment_stage"
            )
            .order_by("-transaction_date", "-id")
        )
        movement_type = request.query_params.get("movement_type")
        if movement_type:
            qs = qs.filter(movement_type=movement_type.upper())
        item_id = request.query_params.get("item")
        if item_id:
            qs = qs.filter(item_id=item_id)
        serializer = WarehouseStockMovementSerializer(qs, many=True)
        return Response(
            {
                "success": True,
                "message": "Movements retrieved successfully.",
                "count": qs.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# STOCK IN
# =========================================================
class WarehouseStockInAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = WarehouseStockInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        item = data["item"]
        to_warehouse = data["to_warehouse"]

        if item.user_id != request.user.id:
            return Response(
                {"success": False, "message": "Item does not belong to you."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if to_warehouse.user_id != request.user.id:
            return Response(
                {"success": False, "message": "Warehouse does not belong to you."},
                status=status.HTTP_403_FORBIDDEN,
            )

        movement = WarehouseStockMovement(
            user=request.user,
            item=item,
            movement_type=WarehouseStockMovement.MovementType.STOCK_IN,
            to_warehouse=to_warehouse,
            from_warehouse=None,
            quantity=data["quantity"],
            reference_number=data.get("reference_number") or "",
            remarks=data.get("remarks") or "",
            transaction_date=data.get("transaction_date") or timezone.now(),
        )
        movement.save()

        zone = data.get("zone")
        if zone:
            stock = WarehouseStock.objects.filter(
                item=item, warehouse=to_warehouse
            ).first()
            if stock:
                stock.zone = zone
                stock.save(update_fields=["zone", "updated_at"])

        return Response(
            {
                "success": True,
                "message": f"Stock in successful. {data['quantity']} units added.",
                "data": WarehouseStockMovementSerializer(movement).data,
            },
            status=status.HTTP_201_CREATED,
        )


# =========================================================
# DEPLOY  (Spare -->  Deploy)
# =========================================================
class WarehouseDeployAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = WarehouseDeploySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        item = data["item"]
        from_warehouse = data["from_warehouse"]
        to_warehouse = data["to_warehouse"]

        if item.user_id != request.user.id:
            return Response(
                {"success": False, "message": "Item does not belong to you."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if (
            from_warehouse.user_id != request.user.id
            or to_warehouse.user_id != request.user.id
        ):
            return Response(
                {"success": False, "message": "Warehouse does not belong to you."},
                status=status.HTTP_403_FORBIDDEN,
            )

        movement = WarehouseStockMovement(
            user=request.user,
            item=item,
            movement_type=WarehouseStockMovement.MovementType.DEPLOY,
            from_warehouse=from_warehouse,
            to_warehouse=to_warehouse,
            quantity=data["quantity"],
            equipment=data.get("equipment"),
            treatment_stage=data.get("treatment_stage"),
            reference_number=data.get("reference_number") or "",
            remarks=data.get("remarks") or "",
            transaction_date=data.get("transaction_date") or timezone.now(),
        )
        movement.save()

        return Response(
            {
                "success": True,
                "message": f"Deployed {data['quantity']} units from Spare to Deploy.",
                "data": WarehouseStockMovementSerializer(movement).data,
            },
            status=status.HTTP_201_CREATED,
        )


# =========================================================
# RETURN  (Deploy --> Spare)
# =========================================================
class WarehouseReturnAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = WarehouseReturnSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        item = data["item"]
        from_warehouse = data["from_warehouse"]
        to_warehouse = data["to_warehouse"]

        if item.user_id != request.user.id:
            return Response(
                {"success": False, "message": "Item does not belong to you."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if (
            from_warehouse.user_id != request.user.id
            or to_warehouse.user_id != request.user.id
        ):
            return Response(
                {"success": False, "message": "Warehouse does not belong to you."},
                status=status.HTTP_403_FORBIDDEN,
            )

        movement = WarehouseStockMovement(
            user=request.user,
            item=item,
            movement_type=WarehouseStockMovement.MovementType.RETURN,
            from_warehouse=from_warehouse,
            to_warehouse=to_warehouse,
            quantity=data["quantity"],
            equipment=data.get("equipment"),
            reference_number=data.get("reference_number") or "",
            remarks=data.get("remarks") or "",
            transaction_date=data.get("transaction_date") or timezone.now(),
        )
        movement.save()

        return Response(
            {
                "success": True,
                "message": f"Returned {data['quantity']} units from Deploy to Spare.",
                "data": WarehouseStockMovementSerializer(movement).data,
            },
            status=status.HTTP_201_CREATED,
        )


# =========================================================
# STOCK OUT
# =========================================================
class WarehouseStockOutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = WarehouseStockOutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        item = data["item"]
        from_warehouse = data["from_warehouse"]

        if item.user_id != request.user.id:
            return Response(
                {"success": False, "message": "Item does not belong to you."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if from_warehouse.user_id != request.user.id:
            return Response(
                {"success": False, "message": "Warehouse does not belong to you."},
                status=status.HTTP_403_FORBIDDEN,
            )

        movement = WarehouseStockMovement(
            user=request.user,
            item=item,
            movement_type=WarehouseStockMovement.MovementType.STOCK_OUT,
            from_warehouse=from_warehouse,
            to_warehouse=None,
            quantity=data["quantity"],
            reference_number=data.get("reference_number") or "",
            remarks=data.get("remarks") or "",
            transaction_date=data.get("transaction_date") or timezone.now(),
        )
        movement.save()

        return Response(
            {
                "success": True,
                "message": f"Stock out successful. {data['quantity']} units issued.",
                "data": WarehouseStockMovementSerializer(movement).data,
            },
            status=status.HTTP_201_CREATED,
        )


# =========================================================
# ADJUSTMENT
# =========================================================
class WarehouseAdjustmentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = WarehouseAdjustmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        item = data["item"]
        warehouse = data["warehouse"]
        quantity = data["quantity"]

        if item.user_id != request.user.id:
            return Response(
                {"success": False, "message": "Item does not belong to you."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if warehouse.user_id != request.user.id:
            return Response(
                {"success": False, "message": "Warehouse does not belong to you."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if quantity > 0:
            movement = WarehouseStockMovement(
                user=request.user,
                item=item,
                movement_type=WarehouseStockMovement.MovementType.ADJUSTMENT,
                to_warehouse=warehouse,
                from_warehouse=None,
                quantity=abs(quantity),
                remarks=data.get("remarks") or "Stock adjustment increase",
                transaction_date=data.get("transaction_date") or timezone.now(),
            )
        else:
            movement = WarehouseStockMovement(
                user=request.user,
                item=item,
                movement_type=WarehouseStockMovement.MovementType.ADJUSTMENT,
                from_warehouse=warehouse,
                to_warehouse=None,
                quantity=abs(quantity),
                remarks=data.get("remarks") or "Stock adjustment decrease",
                transaction_date=data.get("transaction_date") or timezone.now(),
            )

        movement.save()
        action = "increased" if quantity > 0 else "decreased"

        return Response(
            {
                "success": True,
                "message": f"Stock adjustment successful. Quantity {action} by {abs(quantity)}.",
                "data": WarehouseStockMovementSerializer(movement).data,
            },
            status=status.HTTP_201_CREATED,
        )
