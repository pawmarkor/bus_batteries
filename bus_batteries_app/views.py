from collections import namedtuple

from django.contrib import messages
from django.http.response import HttpResponseBadRequest
from django.shortcuts import (
    redirect,
    render,
    get_object_or_404,
)

from .models import Battery, Bus
from .const import n

Alert = namedtuple(
    'Alert',
    ['type', 'message']
)

BusWithBatteriesSummary = namedtuple(
    'BusWithBatteriesSummary',
    ['id', 'name', 'no_of_all_batteries', 'no_of_active_batteries']
)

BusWithBatteries = namedtuple(
    'BusWithBatteries',
    ['id', 'name', 'batteries']
)


def index(request, alert=None):
    buses = Bus.objects.order_by('id').all()
    buses_with_batteries = [
        BusWithBatteriesSummary(
            bus.id,
            bus.name,
            no_of_all_batteries=bus.battery_set.count(),
            no_of_active_batteries=bus.battery_set.filter(active=True).count()
        )
        for bus in buses
    ]
    context = {
        'alert': alert,
        'buses': buses_with_batteries,
    }
    return render(request, 'bus_batteries_app/index.html', context)


def add_bus(request):
    if request.method == 'POST':
        id = request.POST['id']
        name = request.POST['name']
        no_of_batteries = int(request.POST['no_of_batteries'])
        bus = Bus(id=id, name=name)
        try:
            bulk_create_batteries(bus, no_of_batteries)
            bus.save()
        except Exception as e:
            messages.error(request, 'Error while adding a bus: {}'.format(e))
        else:
            messages.success(request, 'Bus of id={} added successfully'.format(bus.id))
        return redirect('bus_batteries_app:index')
    elif request.method == 'GET':
        return render(request, 'bus_batteries_app/add_bus.html', {'n': n})
    else:
        return HttpResponseBadRequest('Unsupported HTTP method')


def edit_bus(request, bus_id):
    bus = get_object_or_404(Bus, pk=bus_id)
    if request.method == 'POST':
        bus.name = request.POST['name']
        batteries_to_be_removed = set(
            int(id) for id in request.POST.getlist('batteries_to_be_removed')
        )
        try:
            new_battery_ids = bulk_create_batteries(
                bus,
                no_of_batteries_to_be_added=int(request.POST['no_of_batteries_to_be_added']),
                no_of_batteries_to_be_removed=len(batteries_to_be_removed),
            )
            for battery in bus.battery_set.all():
                if battery.id in batteries_to_be_removed:
                    battery.delete()
                elif battery.id not in new_battery_ids:
                    battery.active = request.POST.get('battery_{}_active'.format(battery.id)) is not None
                    battery.save()
            bus.save()
        except Exception as e:
            messages.error(request, 'Error while editing a bus of id={}: {}'.format(bus_id, e))
        else:
            messages.success(request, 'Bus of id={} edited successfully'.format(bus_id))
        return redirect('bus_batteries_app:index')
    elif request.method == 'GET':
        context = {
            'n': n,
            'bus': BusWithBatteries(bus.id, bus.name, bus.battery_set.order_by('number').all()),
        }
        return render(request, 'bus_batteries_app/edit_bus.html', context)
    else:
        return HttpResponseBadRequest('Unsupported HTTP method')


def bulk_create_batteries(bus, no_of_batteries_to_be_added,
                          no_of_batteries_to_be_removed=0):
    if (bus.battery_set.count()
            + no_of_batteries_to_be_added
            - no_of_batteries_to_be_removed) > n:
        raise Exception('The number of batteries cannot be higher then {}'.format(n))
    new_batteries = [
        Battery(
            bus_id=bus.id,
            number=battery_no,
            active=True,
        )
        for battery_no in range(
            bus.next_battery_number,
            bus.next_battery_number + no_of_batteries_to_be_added
        )
    ]
    bus.battery_set.bulk_create(new_batteries)
    bus.next_battery_number += no_of_batteries_to_be_added
    return set(battery.id for battery in new_batteries)
