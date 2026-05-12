from django.db import models


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('delivering', 'Delivering'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.BigAutoField(primary_key=True)

    user = models.ForeignKey('users.User', on_delete=models.CASCADE)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    items_total = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    address = models.TextField()
    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id}"