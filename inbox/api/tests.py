from notifications.models import Notification
from testing.testcases import TestCase

COMMENT_URL = '/api/comments/'
LIKE_URL = '/api/likes/'
NOTIFICATION_URL = '/api/notifications/'


class NotificationTests(TestCase):

    def setUp(self):
        self.kellynim, self.kellynim_client = self.create_user_and_client('kellynim')
        self.talenti, self.talenti_client = self.create_user_and_client('dong')
        self.talenti_tweet = self.create_tweet(self.talenti)

    def test_comment_create_api_trigger_notification(self):
        self.assertEqual(Notification.objects.count(), 0)
        self.kellynim_client.post(COMMENT_URL, {
            'tweet_id': self.talenti_tweet.id,
            'content': 'a ha',
        })
        self.assertEqual(Notification.objects.count(), 1)

    def test_like_create_api_trigger_notification(self):
        self.assertEqual(Notification.objects.count(), 0)
        self.kellynim_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.talenti_tweet.id,
        })
        self.assertEqual(Notification.objects.count(), 1)


class NotificationApiTests(TestCase):

    def setUp(self):
        self.kellynim, self.kellynim_client = self.create_user_and_client('kellynim')
        self.talenti, self.talenti_client = self.create_user_and_client('talenti')
        self.kellynim_tweet = self.create_tweet(self.kellynim)

    def test_unread_count(self):
        self.talenti_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.kellynim_tweet.id,
        })

        url = '/api/notifications/unread-count/'
        response = self.kellynim_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unread_count'], 1)

        comment = self.create_comment(self.kellynim, self.kellynim_tweet)
        self.talenti_client.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })
        response = self.kellynim_client.get(url)
        self.assertEqual(response.data['unread_count'], 2)
        response = self.talenti_client.get(url)
        self.assertEqual(response.data['unread_count'], 0)

    def test_mark_all_as_read(self):
        self.talenti_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.kellynim_tweet.id,
        })
        comment = self.create_comment(self.kellynim, self.kellynim_tweet)
        self.talenti_client.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })

        unread_url = '/api/notifications/unread-count/'
        response = self.kellynim_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 2)

        mark_url = '/api/notifications/mark-all-as-read/'
        response = self.kellynim_client.get(mark_url)
        self.assertEqual(response.status_code, 405)

        response = self.talenti_client.post(mark_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['marked_count'], 0)
        response = self.kellynim_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 2)

        response = self.kellynim_client.post(mark_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['marked_count'], 2)
        response = self.kellynim_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 0)

    def test_list(self):
        self.talenti_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.kellynim_tweet.id,
        })
        comment = self.create_comment(self.kellynim, self.kellynim_tweet)
        self.talenti_client.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })


        response = self.anonymous_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 403)

        response = self.talenti_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)

        response = self.kellynim_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)

        notification = self.kellynim.notifications.first()
        notification.unread = False
        notification.save()
        response = self.kellynim_client.get(NOTIFICATION_URL)
        self.assertEqual(response.data['count'], 2)
        response = self.kellynim_client.get(NOTIFICATION_URL, {'unread': True})
        self.assertEqual(response.data['count'], 1)
        response = self.kellynim_client.get(NOTIFICATION_URL, {'unread': False})
        self.assertEqual(response.data['count'], 1)

    def test_update(self):
        self.talenti_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.kellynim_tweet.id,
        })
        comment = self.create_comment(self.kellynim, self.kellynim_tweet)
        self.talenti_client.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })
        notification = self.kellynim.notifications.first()

        url = '/api/notifications/{}/'.format(notification.id)
        
        response = self.talenti_client.post(url, {'unread': False})
        self.assertEqual(response.status_code, 405)

        response = self.anonymous_client.put(url, {'unread': False})
        self.assertEqual(response.status_code, 403)

        response = self.talenti_client.put(url, {'unread': False})
        self.assertEqual(response.status_code, 404)

        response = self.kellynim_client.put(url, {'unread': False})
        self.assertEqual(response.status_code, 200)
        unread_url = '/api/notifications/unread-count/'
        response = self.kellynim_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 1)


        response = self.kellynim_client.put(url, {'unread': True})
        response = self.kellynim_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 2)

        response = self.kellynim_client.put(url, {'verb': 'newverb'})
        self.assertEqual(response.status_code, 400)

        response = self.kellynim_client.put(url, {'verb': 'newverb', 'unread': False})
        self.assertEqual(response.status_code, 200)
        notification.refresh_from_db()
        self.assertNotEqual(notification.verb, 'newverb')
