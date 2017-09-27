from collections import namedtuple

from django.shortcuts import render

from .models import Bus

BusWithBatteriesData = namedtuple(
    'BusWithBatteriesData',
    ['id', 'name', 'no_of_all_batteries', 'no_of_active_batteries']
)


def index(request):
    buses = Bus.objects.all()
    buses_with_batteries = [
        BusWithBatteriesData(
            bus.id,
            bus.name,
            no_of_all_batteries=bus.battery_set.count(),
            no_of_active_batteries=bus.battery_set.filter(active=True).count()
        )
        for bus in buses
    ]
    context = {
        'buses': buses_with_batteries,
    }
    return render(request, 'bus_batteries_app/index.html', context)
