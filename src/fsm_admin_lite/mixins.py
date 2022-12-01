from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.contrib import messages
from django.contrib.admin.options import BaseModelAdmin
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.core.exceptions import FieldDoesNotExist
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django_fsm import ConcurrentTransition, FSMField, Transition, TransitionNotAllowed


@dataclass
class FSMObjectTransition:
    fsm_field: str
    block_label: str
    available_transitions: list[Transition]


class FSMAdminMixin(BaseModelAdmin):
    change_form_template: str = "admin/fsm_admin_change_form.html"

    fsm_fields: list[str] = []
    fsm_transition_success_msg: str = "FSM transition '{transition_name}' succeeded."
    fsm_transition_error_msg: str = "FSM transition '{transition_name}' failed: {error}."
    fsm_transition_not_allowed_msg = "FSM transition '{transition_name}' is not allowed."
    fsm_transition_not_valid_msg = "FSM transition '{transition_name}' is not a valid."

    def get_fsm_field_instance(self, fsm_field_name: str) -> FSMField | None:
        try:
            return self.model._meta.get_field(fsm_field_name)
        except FieldDoesNotExist:
            return None

    def get_readonly_fields(self, request: HttpRequest, obj: Any = None) -> tuple[str]:
        read_only_fields = super().get_readonly_fields(request, obj)

        for fsm_field_name in self.fsm_fields:
            if fsm_field_name in read_only_fields:
                continue
            field = self.get_fsm_field_instance(fsm_field_name=fsm_field_name)
            if field and getattr(field, "protected", False):
                read_only_fields += (fsm_field_name,)

        return read_only_fields

    @staticmethod
    def get_fsm_block_label(fsm_field_name: str) -> str:
        return f"Transition ({fsm_field_name})"

    def get_fsm_object_transitions(
        self, request: HttpRequest, obj: Any
    ) -> list[FSMObjectTransition]:
        fsm_object_transitions = []

        for field_name in sorted(self.fsm_fields):
            func = getattr(obj, f"get_available_user_{field_name}_transitions")
            if func:
                fsm_object_transitions.append(
                    FSMObjectTransition(
                        fsm_field=field_name,
                        block_label=self.get_fsm_block_label(fsm_field_name=field_name),
                        available_transitions=list(func(request.user)),
                    )
                )

        return fsm_object_transitions

    def change_view(
        self,
        request: HttpRequest,
        object_id: str,
        form_url: str = "",
        extra_context: dict[str, Any] | None = None,
    ) -> HttpResponse:

        _context = extra_context or {}
        _context["fsm_object_transitions"] = self.get_fsm_object_transitions(
            request=request,
            obj=self.get_object(request=request, object_id=object_id),
        )

        return super().change_view(
            request=request,
            object_id=object_id,
            form_url=form_url,
            extra_context=_context,
        )

    def get_fsm_redirect_url(self, request: HttpRequest, obj: Any) -> str:
        return request.path

    def get_fsm_response(self, request: HttpRequest, obj: Any) -> HttpResponse:
        redirect_url = self.get_fsm_redirect_url(request=request, obj=obj)
        redirect_url = add_preserved_filters(
            context={
                "preserved_filters": self.get_preserved_filters(request),
                "opts": self.model._meta,
            },
            url=redirect_url,
        )
        return HttpResponseRedirect(redirect_to=redirect_url)

    def response_change(self, request: HttpRequest, obj: Any) -> HttpResponse:
        if "_transition_to" in request.POST:
            try:
                transition_name = request.POST["_transition_to"]
                transition_func = getattr(obj, transition_name)
            except AttributeError:
                self.message_user(
                    request=request,
                    message=self.fsm_transition_not_valid_msg.format(
                        transition_name=transition_name,
                    ),
                    level=messages.ERROR,
                )
                return self.get_fsm_response(
                    request=request,
                    obj=obj,
                )

            try:
                transition_func()
            except TransitionNotAllowed:
                self.message_user(
                    request=request,
                    message=self.fsm_transition_not_allowed_msg.format(
                        transition_name=transition_name,
                    ),
                    level=messages.ERROR,
                )
            except ConcurrentTransition as err:
                self.message_user(
                    request=request,
                    message=self.fsm_transition_error_msg.format(
                        transition_name=transition_name, error=str(err)
                    ),
                    level=messages.ERROR,
                )
            else:
                obj.save()
                self.message_user(
                    request=request,
                    message=self.fsm_transition_success_msg.format(
                        transition_name=transition_name,
                    ),
                    level=messages.INFO,
                )

            return self.get_fsm_response(
                request=request,
                obj=obj,
            )

        return super().response_change(request=request, obj=obj)
