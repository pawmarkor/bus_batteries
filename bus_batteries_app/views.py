from collections import namedtuple

from django.db import transaction
from django.contrib import messages
from django.db.models import F
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


def index(request):
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
        'buses': buses_with_batteries,
    }
    return render(request, 'bus_batteries_app/index.html', context)


def add_bus(request):
    try:
        _id = request.POST['id']
        name = request.POST['name']
        no_of_batteries = int(request.POST['no_of_batteries'])
    except KeyError:
        return render(request, 'bus_batteries_app/add_bus.html', {'n': n})
    else:
        try:
            if Bus.objects.filter(id=_id).exists():
                raise Exception('Bus with id={} already exists'.format(_id))
            check_number_of_batteries(
                current_no_of_batteries=0,
                no_of_batteries_to_be_added=no_of_batteries,
                no_of_batteries_to_be_removed=0,
            )
            bus = Bus(id=_id, name=name)
            bulk_create_batteries(bus, no_of_batteries)
            bus.next_battery_number = no_of_batteries + 1
            bus.save()
        except Exception as e:
            messages.error(request, 'Error while adding a bus: {}'.format(e))
        else:
            messages.success(request, 'Bus of id={} added successfully'.format(bus.id))
        return redirect('bus_batteries_app:index')


def edit_bus(request, bus_id):
    bus = get_object_or_404(Bus, pk=bus_id)
    try:
        bus.name = request.POST['name']
        no_of_batteries_to_be_added = int(request.POST['no_of_batteries_to_be_added'])
        batteries_to_be_removed = set(
            int(_id) for _id in request.POST.getlist('batteries_to_be_removed')
        )
    except KeyError:
        context = {
            'n': n,
            'bus': BusWithBatteries(bus.id, bus.name, bus.battery_set.order_by('number').all()),
        }
        return render(request, 'bus_batteries_app/edit_bus.html', context)
    except TypeError:
        messages.error(request, 'Number of batteries to be added and '
                                'battery ids to be removed must be integers')
    else:
        try:
            check_number_of_batteries(
                current_no_of_batteries=bus.battery_set.count(),
                no_of_batteries_to_be_added=no_of_batteries_to_be_added,
                no_of_batteries_to_be_removed=len(batteries_to_be_removed),
            )
            with transaction.atomic():
                for battery in bus.battery_set.all():
                    if battery.id in batteries_to_be_removed:
                        battery.delete()
                    else:
                        battery.active = request.POST.get('battery_{}_active'.format(battery.id)) is not None
                        battery.save()
                bulk_create_batteries(bus, no_of_batteries_to_be_added)
                bus.next_battery_number = F('next_battery_number') + no_of_batteries_to_be_added
                bus.save()
        except Exception as e:
            messages.error(request, 'Error while editing a bus of id={}: {}'.format(bus_id, e))
        else:
            messages.success(request, 'Bus of id={} edited successfully'.format(bus_id))
    return redirect('bus_batteries_app:index')


def check_number_of_batteries(current_no_of_batteries,
                              no_of_batteries_to_be_added,
                              no_of_batteries_to_be_removed):
    if (current_no_of_batteries
            + no_of_batteries_to_be_added
            - no_of_batteries_to_be_removed) > n:
        raise Exception('The number of batteries cannot be higher then {}'.format(n))


def bulk_create_batteries(bus, no_of_batteries_to_be_added):
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
