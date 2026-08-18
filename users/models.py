from django.contrib.auth.hashers import make_password
from django.db import models

class User(models.Model):
    email = models.EmailField(unique=True, db_index=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["-created_at"],
                name="user_created_at_idx"
            ),
            models.Index(
                fields=["updated_at"],
                name="user_updated_at_idx"
            ),
        ]

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.email