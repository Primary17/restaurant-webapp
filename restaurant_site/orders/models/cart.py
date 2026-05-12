from django.db import models


class Cart(models.Model):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart ({self.user})"