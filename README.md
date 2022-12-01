# django-fsm-admin-lite

![Generic badge](https://github.com/etchegom/django-fsm-admin-lite/actions/workflows/tests.yml/badge.svg)


Integrate [django-fsm](https://github.com/viewflow/django-fsm) state transitions into Django Admin.

Alternative of [django-fsm-admin](https://github.com/gadventures/django-fsm-admin), with a lighter version of the frontend part.

Features:
- display available transitions in model admin so that user can apply them
- mark FSM protected fields as read only

Limitations:
- transition methods parameters are not handled

---

## Installation

```
pip install django-fsm-admin-lite
```
Or, for the latest git version
```
python -m pip install 'django-fsm-admin-lite @ git+https://github.com/etchegom/django-fsm-admin-lite.git'
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

## Configuration

| Admin class attribute             | Option                                              |
|-----------------------------------|-----------------------------------------------------|
| `fsm_fields`                      | List of FSM fields to handle                        |
| `fsm_transition_success_msg`      | Admin message for transition success                |
| `fsm_transition_error_msg`        | Admin message for transition error                  |
| `fsm_transition_not_allowed_msg`  | Admin message for transition not allowed error      |
| `fsm_transition_not_valid_msg`    | Admin message for transition not valid error        |
| `fsm_context_key`                 | Template context key for FSM transitions            |
| `fsm_post_param`                  | POST parameter name for FSM transitions             |

---

## Run example

```
make example
```

Then go to [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin), login with `admin`/`password` and create a new blog post object.


---

## TODO
- improve the default template files
- display all the transitions (not available transition should be represented as disabled buttons)
