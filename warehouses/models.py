from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.utils import timezone


class Warehouse(models.Model):

    class WarehouseType(models.TextChoices):
        SPARE = "SPARE", "Spare Warehouse"
        DEPLOY = "DEPLOY", "Deploy Warehouse"

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="warehouses")
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=50, editable=False, blank=True)
    warehouse_type = models.CharField(max_length=20, choices=WarehouseType.choices)
    location = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "warehouses"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["user", "code"], name="unique_user_warehouse_code"),
            models.UniqueConstraint(fields=["user", "name"], name="unique_user_warehouse_name"),
        ]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["warehouse_type"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["code"]),
        ]

    def __str__(self):
        return f"{self.code} - {self.name} ({self.get_warehouse_type_display()})"

    def _generate_code(self):
        prefix_map = {
            self.WarehouseType.SPARE: "WH-SPARE",
            self.WarehouseType.DEPLOY: "WH-DEPLOY",
        }
        prefix = prefix_map.get(self.warehouse_type, "WH")
        last = (
            Warehouse.objects.filter(user=self.user, code__startswith=f"{prefix}-")
            .order_by("-id")
            .first()
        )
        last_num = 0
        if last:
            try:
                last_num = int(last.code.rsplit("-", 1)[-1])
            except (ValueError, IndexError):
                last_num = 0
        return f"{prefix}-{last_num + 1:04d}"

    def save(self, *args, **kwargs):
        if not self.code:
            if not self.warehouse_type:
                raise ValidationError({"warehouse_type": "Warehouse type is required to generate code."})
            self.code = self._generate_code()
        super().save(*args, **kwargs)


class WarehouseZone(models.Model):

    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="zones")
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "warehouse_zones"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["warehouse", "name"], name="unique_warehouse_zone_name"),
        ]
        indexes = [
            models.Index(fields=["warehouse"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.warehouse.code} / {self.name}"


class WarehouseItem(models.Model):

    class Unit(models.TextChoices):
        PCS = "PCS", "Pieces"
        SET = "SET", "Set"
        KG = "KG", "Kilogram"
        G = "G", "Gram"
        L = "L", "Litre"
        ML = "ML", "Millilitre"
        BOX = "BOX", "Box"
        PACK = "PACK", "Pack"

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="warehouse_items")
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=50, editable=False, blank=True)
    unit = models.CharField(max_length=10, choices=Unit.choices, default=Unit.PCS)
    description = models.TextField(blank=True, null=True)
    equipment = models.ForeignKey("equipment.Equipment", on_delete=models.SET_NULL, null=True, blank=True, related_name="warehouse_items")
    minimum_stock = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "warehouse_items"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["user", "code"], name="unique_user_warehouse_item_code"),
            models.UniqueConstraint(fields=["user", "name"], name="unique_user_warehouse_item_name"),
        ]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["code"]),
            models.Index(fields=["equipment"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"

    def _generate_code(self):
        prefix = "".join(c for c in self.name.upper() if c.isalnum())[:4] or "ITEM"
        last = (
            WarehouseItem.objects.filter(user=self.user, code__startswith=f"{prefix}-")
            .order_by("-id")
            .first()
        )
        last_num = 0
        if last:
            try:
                last_num = int(last.code.rsplit("-", 1)[-1])
            except (ValueError, IndexError):
                last_num = 0
        return f"{prefix}-{last_num + 1:04d}"

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self._generate_code()
        super().save(*args, **kwargs)


class WarehouseStock(models.Model):

    item = models.ForeignKey(WarehouseItem, on_delete=models.CASCADE, related_name="stocks")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="stocks")
    zone = models.ForeignKey(WarehouseZone, on_delete=models.SET_NULL, null=True, blank=True, related_name="stocks")
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reserved_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "warehouse_stocks"
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(fields=["item", "warehouse"], name="unique_item_warehouse_stock"),
        ]
        indexes = [
            models.Index(fields=["item"]),
            models.Index(fields=["warehouse"]),
        ]

    @property
    def available_quantity(self):
        return self.quantity - self.reserved_quantity

    def clean(self):
        if self.item_id and self.warehouse_id:
            if self.item.user_id != self.warehouse.user_id:
                raise ValidationError({"warehouse": "Item and warehouse must belong to the same user."})
        if self.zone_id and self.warehouse_id:
            if self.zone.warehouse_id != self.warehouse_id:
                raise ValidationError({"zone": "Zone must belong to the selected warehouse."})
        if self.reserved_quantity > self.quantity:
            raise ValidationError({"reserved_quantity": "Reserved quantity cannot exceed quantity."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item.code} @ {self.warehouse.code}: {self.quantity}"


class WarehouseStockMovement(models.Model):

    class MovementType(models.TextChoices):
        STOCK_IN = "STOCK_IN", "Stock In"
        STOCK_OUT = "STOCK_OUT", "Stock Out"
        TRANSFER = "TRANSFER", "Transfer"
        ADJUSTMENT = "ADJUSTMENT", "Adjustment"
        DEPLOY = "DEPLOY", "Deploy"
        RETURN = "RETURN", "Return"

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="warehouse_stock_movements")
    item = models.ForeignKey(WarehouseItem, on_delete=models.PROTECT, related_name="movements")
    movement_type = models.CharField(max_length=20, choices=MovementType.choices)
    from_warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True, related_name="movements_from")
    to_warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True, related_name="movements_to")
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    equipment = models.ForeignKey("equipment.Equipment", on_delete=models.SET_NULL, null=True, blank=True, related_name="warehouse_movements")
    treatment_stage = models.ForeignKey("treatment_process.TreatmentStage", on_delete=models.SET_NULL, null=True, blank=True, related_name="warehouse_movements")
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    transaction_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "warehouse_stock_movements"
        ordering = ["-transaction_date", "-id"]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["item"]),
            models.Index(fields=["movement_type"]),
            models.Index(fields=["from_warehouse"]),
            models.Index(fields=["to_warehouse"]),
            models.Index(fields=["transaction_date"]),
            models.Index(fields=["equipment"]),
        ]

    def __str__(self):
        return f"{self.movement_type} - {self.item.code} - {self.quantity}"

    def clean(self):
        if self.quantity is None or self.quantity <= 0:
            raise ValidationError({"quantity": "Quantity must be greater than zero."})

        if self.item_id and self.user_id:
            if self.item.user_id != self.user_id:
                raise ValidationError({"item": "Item must belong to the same user."})

        if self.from_warehouse_id and self.user_id:
            if self.from_warehouse.user_id != self.user_id:
                raise ValidationError({"from_warehouse": "Source warehouse must belong to the same user."})

        if self.to_warehouse_id and self.user_id:
            if self.to_warehouse.user_id != self.user_id:
                raise ValidationError({"to_warehouse": "Destination warehouse must belong to the same user."})

        mt = self.movement_type

        if mt == self.MovementType.STOCK_IN:
            if not self.to_warehouse_id:
                raise ValidationError({"to_warehouse": "Destination warehouse is required for stock in."})
            if self.from_warehouse_id:
                raise ValidationError({"from_warehouse": "Source warehouse must be empty for stock in."})

        elif mt == self.MovementType.STOCK_OUT:
            if not self.from_warehouse_id:
                raise ValidationError({"from_warehouse": "Source warehouse is required for stock out."})
            if self.to_warehouse_id:
                raise ValidationError({"to_warehouse": "Destination warehouse must be empty for stock out."})

        elif mt in (self.MovementType.TRANSFER, self.MovementType.DEPLOY, self.MovementType.RETURN):
            if not self.from_warehouse_id or not self.to_warehouse_id:
                raise ValidationError({
                    "from_warehouse": "Source and destination warehouses are required.",
                    "to_warehouse": "Source and destination warehouses are required.",
                })
            if self.from_warehouse_id == self.to_warehouse_id:
                raise ValidationError({"to_warehouse": "Source and destination must be different."})

            if mt == self.MovementType.DEPLOY:
                if self.from_warehouse.warehouse_type != Warehouse.WarehouseType.SPARE:
                    raise ValidationError({"from_warehouse": "Deploy must start from Spare warehouse."})
                if self.to_warehouse.warehouse_type != Warehouse.WarehouseType.DEPLOY:
                    raise ValidationError({"to_warehouse": "Deploy must go to Deploy warehouse."})

            if mt == self.MovementType.RETURN:
                if self.from_warehouse.warehouse_type != Warehouse.WarehouseType.DEPLOY:
                    raise ValidationError({"from_warehouse": "Return must start from Deploy warehouse."})
                if self.to_warehouse.warehouse_type != Warehouse.WarehouseType.SPARE:
                    raise ValidationError({"to_warehouse": "Return must go to Spare warehouse."})

        elif mt == self.MovementType.ADJUSTMENT:
            if bool(self.from_warehouse_id) == bool(self.to_warehouse_id):
                raise ValidationError({
                    "to_warehouse": (
                        "Adjustment needs exactly one warehouse "
                        "(to_warehouse = increase, from_warehouse = decrease)."
                    )
                })

    def _get_or_create_stock(self, warehouse):
        stock, _ = WarehouseStock.objects.select_for_update().get_or_create(
            item=self.item,
            warehouse=warehouse,
            defaults={"quantity": 0, "reserved_quantity": 0},
        )
        return stock

    def _update_stock(self):
        qty = self.quantity
        mt = self.movement_type

        if mt == self.MovementType.STOCK_IN:
            stock = self._get_or_create_stock(self.to_warehouse)
            stock.quantity += qty
            stock.save(update_fields=["quantity", "updated_at"])

        elif mt == self.MovementType.STOCK_OUT:
            stock = self._get_or_create_stock(self.from_warehouse)
            if stock.available_quantity < qty:
                raise ValidationError({
                    "quantity": f"Insufficient stock. Available: {stock.available_quantity}, requested: {qty}."
                })
            stock.quantity -= qty
            if stock.reserved_quantity > stock.quantity:
                stock.reserved_quantity = stock.quantity
            stock.save(update_fields=["quantity", "reserved_quantity", "updated_at"])

        elif mt in (self.MovementType.TRANSFER, self.MovementType.DEPLOY, self.MovementType.RETURN):
            from_stock = self._get_or_create_stock(self.from_warehouse)
            if from_stock.available_quantity < qty:
                raise ValidationError({
                    "quantity": (
                        f"Insufficient stock in source. "
                        f"Available: {from_stock.available_quantity}, requested: {qty}."
                    )
                })
            from_stock.quantity -= qty
            if from_stock.reserved_quantity > from_stock.quantity:
                from_stock.reserved_quantity = from_stock.quantity
            from_stock.save(update_fields=["quantity", "reserved_quantity", "updated_at"])

            to_stock = self._get_or_create_stock(self.to_warehouse)
            to_stock.quantity += qty
            to_stock.save(update_fields=["quantity", "updated_at"])

        elif mt == self.MovementType.ADJUSTMENT:
            if self.to_warehouse_id and not self.from_warehouse_id:
                stock = self._get_or_create_stock(self.to_warehouse)
                stock.quantity += qty
                stock.save(update_fields=["quantity", "updated_at"])
            elif self.from_warehouse_id and not self.to_warehouse_id:
                stock = self._get_or_create_stock(self.from_warehouse)
                if stock.available_quantity < qty:
                    raise ValidationError({
                        "quantity": (
                            f"Insufficient stock. Available: {stock.available_quantity}, "
                            f"requested decrease: {qty}."
                        )
                    })
                stock.quantity -= qty
                if stock.reserved_quantity > stock.quantity:
                    stock.reserved_quantity = stock.quantity
                stock.save(update_fields=["quantity", "reserved_quantity", "updated_at"])

    def save(self, *args, **kwargs):
        self.full_clean()
        with transaction.atomic():
            super().save(*args, **kwargs)
            self._update_stock()