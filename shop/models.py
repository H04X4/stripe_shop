from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.IntegerField()
    currency = models.CharField(max_length=3, choices=[('rub','RUB'),('usd','USD')], default='rub')

    def __str__(self):
        return f"{self.name} ({self.currency} {self.price})"

class Discount(models.Model):
    name = models.CharField(max_length=100)
    amount = models.IntegerField()

    def __str__(self):
        return f"{self.name} (-{self.amount})"

class Tax(models.Model):
    name = models.CharField(max_length=100)
    percentage = models.FloatField()

    def __str__(self):
        return f"{self.name} ({self.percentage}%)"

class Order(models.Model):
    items = models.ManyToManyField(Item, blank=True)
    discount = models.ForeignKey(Discount, null=True, blank=True, on_delete=models.SET_NULL)
    tax = models.ForeignKey(Tax, null=True, blank=True, on_delete=models.SET_NULL)
    currency = models.CharField(max_length=3, choices=[('rub','RUB'),('usd','USD')], default='rub')
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.IntegerField(default=0)

    def calculate_total(self):
        total = sum(item.price for item in self.items.all())
        if self.discount:
            total -= self.discount.amount
        if self.tax:
            total += int(total * (self.tax.percentage / 100))
        self.total_amount = total
        self.save()

    def __str__(self):
        return f"Order #{self.id} ({self.total_amount})"