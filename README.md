# bus_batteries
Simple app for managing buses and batteries installed.

The application allows for:
* creating buses
* managing batteries installed in the buses

Each bus can have up to `n` batteries installed (`n` is defined in `bus_batteries_app/const.py`).

Every bus has:
* numeric `id`
* alphanumeric `name` up to 50 characters

Every battery has:
* numeric `number` and `id` (both unique in a given bus and related i.e. `id = number * 2 + 3` so only `number` is stored in database)
* boolean state `active` telling if the battery is working
