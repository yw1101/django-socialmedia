from django.db import models
from django.contrib.auth.models import User
from utils.time_helpers import utc_now
from django.contrib.contenttypes.models import ContentType
from likes.models import Like


class Tweet(models.Model):
    #Who posts the tweet
    user = models.ForeignKey(
        User,
        on_delete = models.SET_NULL,
        null = True
    )
    content = models.CharField(max_length = 255)
    created_at = models.DateTimeField(auto_now_add = True)

    class Meta:
        #composite index
        index_together = (('user', 'created_at'),) #tuple
        ordering = ('user', '-created_at')

    @property
    def hours_to_now(self):
        return (utc_now() - self.created_at).seconds // 3600

    def __str__(self):
        #Print(tweet instance)
        return f'{self.created_at} {self.user}: {self.content}'

    @property
    def like_set(self):
        return Like.objects.filter(
            content_type = ContentType.objects.get_for_model(Tweet),
            object_id = self.id,
        ).order_by('-created_at')
