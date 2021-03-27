from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.


class Courier(models.Model):
    COURIER_TYPES = (
        ('foot', 'foot'),
        ('bike', 'bike'),
        ('car', 'car')
    )
    PRICE_COEFFS = {
        'foot': 2,
        'bike': 5,
        'car': 9
    }
    courier_id = models.IntegerField(primary_key=True, unique=True)
    courier_type = models.CharField(max_length=4, choices=COURIER_TYPES)
    regions = ArrayField(models.IntegerField())
    working_hours = ArrayField(models.CharField(max_length=11))
    assign_time = models.CharField(max_length=25, null=True)
    earnings = models.IntegerField(default=0)
    rating = models.FloatField(default=0)

    @staticmethod
    def update_courier_earnings(courier):
        courier.earnings = courier.earnings + 500 * Courier.PRICE_COEFFS[courier.courier_type]
        courier.save()


class Order(models.Model):
    order_id = models.IntegerField(primary_key=True, unique=True)
    weight = models.FloatField()
    region = models.IntegerField()
    delivery_hours = ArrayField(models.CharField(max_length=11))
    complete_time = models.CharField(max_length=25, null=True)
    courier = models.ForeignKey(Courier, on_delete=models.CASCADE, null=True)
