from django.db import models


class Bus(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Battery(models.Model):
    db_id = models.BigIntegerField(primary_key=True)
    id = models.BigIntegerField()
    number = models.BigIntegerField()
    active = models.BooleanField()
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)

    def __str__(self):
        return "battery no {} from bus {}".format(self.number, self.bus.name)
