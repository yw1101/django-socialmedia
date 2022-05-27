from comments.models import Comment
from django.utils import timezone
from rest_framework.test import APIClient
from testing.testcases import TestCase


COMMENT_URL = '/api/comments/'
COMMENT_DETAIL_URL = '/api/comments/{}/'

class CommentApiTests(TestCase):

    def setUp(self):
        self.kellynim = self.create_user('kellynim')
        self.kellynim_client = APIClient()
        self.kellynim_client.force_authenticate(self.kellynim)
        self.talenti = self.create_user('talenti')
        self.talenti_client = APIClient()
        self.talenti_client.force_authenticate(self.talenti)

        self.tweet = self.create_tweet(self.kellynim)

    def test_create(self):

        response = self.anonymous_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 403)


        response = self.kellynim_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 400)


        response = self.kellynim_client.post(COMMENT_URL, {'tweet_id': self.tweet.id})
        self.assertEqual(response.status_code, 400)


        response = self.kellynim_client.post(COMMENT_URL, {'content': '1'})
        self.assertEqual(response.status_code, 400)


        response = self.kellynim_client.post(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'content': '1' * 141,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('content' in response.data['errors'], True)


        response = self.kellynim_client.post(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'content': '1',
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.kellynim.id)
        self.assertEqual(response.data['tweet_id'], self.tweet.id)
        self.assertEqual(response.data['content'], '1')

    def test_destroy(self):
        comment = self.create_comment(self.kellynim, self.tweet)
        url = COMMENT_DETAIL_URL.format(comment.id)


        response = self.anonymous_client.delete(url)
        self.assertEqual(response.status_code, 403)


        response = self.talenti_client.delete(url)
        self.assertEqual(response.status_code, 403)


        count = Comment.objects.count()
        response = self.kellynim_client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), count - 1)

    def test_update(self):
        comment = self.create_comment(self.kellynim, self.tweet, 'original')
        another_tweet = self.create_tweet(self.talenti)
        url = COMMENT_DETAIL_URL.format(comment.id)


        response = self.anonymous_client.put(url, {'content': 'new'})
        self.assertEqual(response.status_code, 403)

        response = self.talenti_client.put(url, {'content': 'new'})
        self.assertEqual(response.status_code, 403)
        comment.refresh_from_db()
        self.assertNotEqual(comment.content, 'new')

        before_updated_at = comment.updated_at
        before_created_at = comment.created_at
        now = timezone.now()
        response = self.kellynim_client.put(url, {
            'content': 'new',
            'user_id': self.talenti.id,
            'tweet_id': another_tweet.id,
            'created_at': now,
        })
        self.assertEqual(response.status_code, 200)
        comment.refresh_from_db()
        self.assertEqual(comment.content, 'new')
        self.assertEqual(comment.user, self.kellynim)
        self.assertEqual(comment.tweet, self.tweet)
        self.assertEqual(comment.created_at, before_created_at)
        self.assertNotEqual(comment.created_at, now)
        self.assertNotEqual(comment.updated_at, before_updated_at)
