from django.core.validators import MinValueValidator
from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=200)
    length = models.PositiveIntegerField(validators=[MinValueValidator(1)], help_text="mm")
    width = models.PositiveIntegerField(validators=[MinValueValidator(1)], help_text="mm")
    height = models.PositiveIntegerField(validators=[MinValueValidator(1)], help_text="mm")
    weight = models.PositiveIntegerField(validators=[MinValueValidator(1)], help_text="grams")

    def __str__(self):
        return self.name


class Box(models.Model):
    name = models.CharField(max_length=200)
    inner_length = models.PositiveIntegerField(validators=[MinValueValidator(1)], help_text="mm")
    inner_width = models.PositiveIntegerField(validators=[MinValueValidator(1)], help_text="mm")
    inner_height = models.PositiveIntegerField(validators=[MinValueValidator(1)], help_text="mm")
    max_weight = models.PositiveIntegerField(validators=[MinValueValidator(1)], help_text="grams")
    cost = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name_plural = "boxes"

    def __str__(self):
        return self.name


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.pk}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["order", "product"], name="unique_product_per_order"
            )
        ]

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"