from django.db import models
from django_fsm import FSMField, transition


class BlogPostStatus(models.TextChoices):
    NEW = "new", "New"
    MODERATED = "moderated", "Moderated"
    PUBLISHED = "published", "Published"
    HIDDEN = "hidden", "Hidden"


class BlogPost(models.Model):
    title = models.CharField(max_length=200, null=True, blank=True)

    state = FSMField(
        choices=BlogPostStatus.choices,
        default=BlogPostStatus.NEW,
        protected=False,
    )

    @transition(
        field=state,
        source=[BlogPostStatus.NEW],
        target=BlogPostStatus.MODERATED,
    )
    def moderate(self):
        pass

    @transition(
        field=state,
        source=[
            BlogPostStatus.MODERATED,
            BlogPostStatus.HIDDEN,
        ],
        target=BlogPostStatus.PUBLISHED,
    )
    def publish(self):
        pass

    @transition(
        field=state,
        source=[
            BlogPostStatus.MODERATED,
            BlogPostStatus.PUBLISHED,
        ],
        target=BlogPostStatus.HIDDEN,
    )
    def hide(self):
        pass
