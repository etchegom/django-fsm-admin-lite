from typing import Any
from unittest.mock import patch

from django.contrib import messages
from django.contrib.admin.sites import AdminSite
from django.test import TestCase
from django.test.client import RequestFactory
from django_fsm import ConcurrentTransition, FSMField

from testapp.admin import BlogPostAdmin
from testapp.models import BlogPost, BlogPostState


class MockRequest:
    path = "/path"
    user: Any


class MockSuperUser:
    def has_perm(self, perm, obj=None):
        return True


request = MockRequest()
request.user = MockSuperUser()


class ModelAdminTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        blog_post = BlogPost.objects.create(title="Article name")
        blog_post.moderate()
        blog_post.save()
        cls.blog_post = blog_post

    def setUp(self):
        self.model_admin = BlogPostAdmin(BlogPost, AdminSite())

    def test_get_fsm_field_instance(self):
        assert self.model_admin.get_fsm_field_instance(fsm_field_name="dummy_name") is None
        fsm_field = self.model_admin.get_fsm_field_instance(fsm_field_name="state")
        assert fsm_field is not None
        assert isinstance(fsm_field, FSMField)

    def test_readonly_fields(self):
        assert self.model_admin.get_readonly_fields(request=request) == ("state",)

    def test_get_fsm_block_label(self):
        assert (
            self.model_admin.get_fsm_block_label(fsm_field_name="MyField") == "Transition (MyField)"
        )

    def test_get_fsm_object_transitions(self):
        fsm_object_transitions = self.model_admin.get_fsm_object_transitions(
            request=request, obj=self.blog_post
        )

        assert len(fsm_object_transitions) == 2
        state_transition, step_transition = fsm_object_transitions

        assert state_transition.fsm_field == "state"
        assert state_transition.block_label == "Transition (state)"
        assert sorted([t.name for t in state_transition.available_transitions]) == [
            "hide",
            "publish",
        ]

        assert step_transition.fsm_field == "step"
        assert step_transition.block_label == "Transition (step)"
        assert sorted([t.name for t in step_transition.available_transitions]) == ["step_two"]

    def test_get_fsm_redirect_url(self):
        assert self.model_admin.get_fsm_redirect_url(request=request, obj=None) == "/path"

    @patch("django.contrib.admin.ModelAdmin.change_view")
    @patch("fsm_admin_lite.mixins.FSMAdminMixin.get_fsm_object_transitions")
    def test_change_view_context(
        self,
        mock_get_fsm_object_transitions,
        mock_super_change_view,
    ):
        mock_get_fsm_object_transitions.return_value = "object transitions"

        self.model_admin.change_view(
            request=request,
            form_url="/test",
            object_id=self.blog_post.pk,
            extra_context={
                "existing_context": "existing context",
            },
        )

        mock_get_fsm_object_transitions.assert_called_once_with(
            request=request,
            obj=self.blog_post,
        )

        mock_super_change_view.assert_called_once_with(
            request=request,
            object_id=self.blog_post.pk,
            form_url="/test",
            extra_context={
                "existing_context": "existing context",
                "fsm_object_transitions": "object transitions",
            },
        )


@patch("django.contrib.admin.options.ModelAdmin.message_user")
class ResponseChangeTest(TestCase):
    def setUp(self):
        self.model_admin = BlogPostAdmin(BlogPost, AdminSite())

    def test_unknown_transition(self, mock_message_user):
        request = RequestFactory().post(
            path="/",
            data={"_fsm_transition_to": "unkown_transition"},
        )

        blog_post = BlogPost.objects.create(title="Article name")
        assert blog_post.state == BlogPostState.CREATED

        self.model_admin.response_change(
            request=request,
            obj=blog_post,
        )

        mock_message_user.assert_called_once_with(
            request=request,
            message="FSM transition 'unkown_transition' is not a valid.",
            level=messages.ERROR,
        )

        updated_blog_post = BlogPost.objects.get(pk=blog_post.pk)
        assert updated_blog_post.state == BlogPostState.CREATED

    def test_transition_applied(self, mock_message_user):
        request = RequestFactory().post(
            path="/",
            data={"_fsm_transition_to": "moderate"},
        )

        blog_post = BlogPost.objects.create(title="Article name")
        assert blog_post.state == BlogPostState.CREATED

        self.model_admin.response_change(
            request=request,
            obj=blog_post,
        )

        mock_message_user.assert_called_once_with(
            request=request,
            message="FSM transition 'moderate' succeeded.",
            level=messages.INFO,
        )

        updated_blog_post = BlogPost.objects.get(pk=blog_post.pk)
        assert updated_blog_post.state == BlogPostState.REVIEWED

    def test_transition_not_allowed_exception(self, mock_message_user):
        request = RequestFactory().post(
            path="/",
            data={"_fsm_transition_to": "publish"},
        )

        blog_post = BlogPost.objects.create(title="Article name")
        assert blog_post.state == BlogPostState.CREATED

        self.model_admin.response_change(
            request=request,
            obj=blog_post,
        )

        mock_message_user.assert_called_once_with(
            request=request,
            message="FSM transition 'publish' is not allowed.",
            level=messages.ERROR,
        )

        updated_blog_post = BlogPost.objects.get(pk=blog_post.pk)
        assert updated_blog_post.state == BlogPostState.CREATED

    def test_concurent_transition_exception(self, mock_message_user):
        request = RequestFactory().post(
            path="/",
            data={"_fsm_transition_to": "moderate"},
        )

        blog_post = BlogPost.objects.create(title="Article name")
        assert blog_post.state == BlogPostState.CREATED

        with patch(
            "testapp.models.BlogPost.moderate",
            side_effect=ConcurrentTransition("error message"),
        ):
            self.model_admin.response_change(
                request=request,
                obj=blog_post,
            )

        mock_message_user.assert_called_once_with(
            request=request,
            message="FSM transition 'moderate' failed: error message.",
            level=messages.ERROR,
        )

        updated_blog_post = BlogPost.objects.get(pk=blog_post.pk)
        assert updated_blog_post.state == BlogPostState.CREATED
