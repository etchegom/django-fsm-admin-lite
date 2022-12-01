from django.db import models
from django_fsm import FSMField, transition


class BlogPostState(models.TextChoices):
    CREATED = "created", "Created"
    REVIEWED = "reviewed", "Reviewed"
    PUBLISHED = "published", "Published"
    HIDDEN = "hidden", "Hidden"


class BlogPostStep(models.TextChoices):
    STEP_1 = "step1", "Step one"
    STEP_2 = "step2", "Step two"
    STEP_3 = "step3", "Step three"


class BlogPost(models.Model):
    title = models.CharField(max_length=200, null=True, blank=True)

    state = FSMField(
        choices=BlogPostState.choices,
        default=BlogPostState.CREATED,
        protected=True,
    )

    step = FSMField(
        choices=BlogPostStep.choices,
        default=BlogPostStep.STEP_1,
        protected=False,
    )

    # state transitions

    @transition(
        field=state,
        source=[BlogPostState.CREATED],
        target=BlogPostState.REVIEWED,
    )
    def moderate(self):
        pass

    @transition(
        field=state,
        source=[
            BlogPostState.REVIEWED,
            BlogPostState.HIDDEN,
        ],
        target=BlogPostState.PUBLISHED,
    )
    def publish(self):
        pass

    @transition(
        field=state,
        source=[
            BlogPostState.REVIEWED,
            BlogPostState.PUBLISHED,
        ],
        target=BlogPostState.HIDDEN,
    )
    def hide(self):
        pass

    # step transitions

    @transition(
        field=step,
        source=[BlogPostStep.STEP_1],
        target=BlogPostStep.STEP_2,
    )
    def step_two(self):
        pass

    @transition(
        field=step,
        source=[BlogPostStep.STEP_2],
        target=BlogPostStep.STEP_3,
    )
    def step_three(self):
        pass

    @transition(
        field=step,
        source=[
            BlogPostStep.STEP_2,
            BlogPostStep.STEP_3,
        ],
        target=BlogPostStep.STEP_1,
    )
    def step_reset(self):
        pass
