from typing import Any

from django.contrib import messages
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect


class FSMAdminMixin:
    change_form_template = "admin/fsm_admin_change_form.html"

    def change_view(
        self,
        request: HttpRequest,
        object_id: str,
        form_url: str = "",
        extra_context: dict[str, Any] | None = None,
    ) -> HttpResponse:

        _context = extra_context or {}
        _context["available_transitions"] = list(
            self.get_object(
                request=request, object_id=object_id
            ).get_available_user_state_transitions(request.user)
        )

        return super().change_view(
            request=request,
            object_id=object_id,
            form_url=form_url,
            extra_context=_context,
        )

    def response_change(self, request: HttpRequest, obj: Any):
        if "_transit_to" in request.POST:
            try:
                transition_name = request.POST["_transit_to"]
                func = getattr(obj, transition_name)
            except AttributeError:
                self.message_user(
                    request=request,
                    message=f"'{transition_name}' is not a valid transition",
                    level=messages.ERROR,
                )
            else:
                func()
                obj.save()
                self.message_user(
                    request=request,
                    message=f"FSM field has been changed to '{obj.state}'",
                )
            return HttpResponseRedirect(".")

        return super().response_change(request, obj)
