# bus_batteries
Simple app for managing buses and batteries installed.

The application allows for:
* creating buses
* managing (adding, removing, turning on/off) batteries installed in the buses

Each bus can have up to `n` batteries installed (`n` is defined in `bus_batteries_app/const.py`).

Every bus has:
* numeric `id`
* alphanumeric `name` up to 50 characters

Every battery has:
* numeric `number` and `id` (both unique in a given bus and related i.e. `id = number * 2 + 3` so only `number` is stored in database)
* boolean state `active` telling if the battery is working

### How to run?
The project is written in `Python 3.6`.

The project uses SQLite database so you don't have to perform any extra database related configuration steps.

Please run the following commands:
```bash
cd bus_batteries
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
Go to [http://127.0.0.1:8000/buses/](http://127.0.0.1:8000/buses/) in your browser and enjoy the app.

### TODOs
In the current state the project is missing:
* logging
* tests

In case the project would run in production migrating into another database (e.x. PostgreSQL) is recommended.