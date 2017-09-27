from collections import namedtuple

from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.shortcuts import render

from .models import Battery, Bus

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


def add_bus(request):
    if request.method == 'POST':
        id = request.POST['id']
        name = request.POST['name']
        no_of_batteries = int(request.POST['no_of_batteries'])
        bus = Bus(id=id, name=name)
        bus.save()
        batteries = [
            Battery(
                bus_id=bus.id,
                id=5 + battery_no * 2,
                number=battery_no,
                active=True,
            )
            for battery_no in range(no_of_batteries)
        ]
        bus.battery_set.bulk_create(batteries)
        return HttpResponseRedirect(reverse('bus_batteries_app:index'))
    elif request.method == 'GET':
        return render(request, 'bus_batteries_app/add_bus.html')
    else:
        raise Http404('Unsupported HTTP method')
