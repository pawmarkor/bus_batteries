from django.db import models


class Bus(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    next_battery_number = models.BigIntegerField(default=1)

    def __str__(self):
        return self.name


class Battery(models.Model):
    db_id = models.BigAutoField(primary_key=True)
    number = models.BigIntegerField()
    active = models.BooleanField()
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)

    @property
    def id(self):
        return self.number * 2 + 3

    def __str__(self):
        return "battery no {} from bus {}".format(self.number, self.bus.name)
