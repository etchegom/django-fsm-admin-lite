# django-fsm-admin-lite

![Generic badge](https://github.com/etchegom/django-fsm-admin-lite/actions/workflows/tests.yml/badge.svg)


Integrate [django-fsm](https://github.com/viewflow/django-fsm) state transitions into Django Admin.

Alternative of [django-fsm-admin](https://github.com/gadventures/django-fsm-admin), with much lighter version of frontend part.

Features:
- add transitions allowed behavior in model admin pages
- mark FSM protected fields as read only

Limitations:
- transition parameters are not handled
- all available transitions are displayed only

---

## Installation (**WIP, not in pypi yet**)

```
pip install django-fsm-admin-lite
```
Or, for the latest git version
```
pip install git@github.com:etchegom/django-fsm-admin-lite.git#egg=django-fsm-admin-lite
```

---

## Usage

Make you model admin class inherit from the mixin class `FSMAdminMixin`.

```python
from django.contrib import admin
from fsm_admin_lite.mixins import FSMAdminMixin

@admin.register(MyModel)
class MyModelAdmin(FSMAdminMixin, admin.ModelAdmin):
    fsm_fields = [
        "state",
    ]
```

---

## Run example

```
make example
```

Then go to [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin), login with `admin`/`password` and create a new blog post object.


---

## TODO

- complete unit tests
- update README file
- example with 2 FSM fields
- push first release to pypi repo
- improve templates
- show all transitions (not available are disabled but visible)
