from testing.testcases import TestCase


class CommentModelTests(TestCase):

    def setUp(self):
        self.clear_cache()
        self.kellynim = self.create_user('kellynim')
        self.tweet = self.create_tweet(self.kellynim)
        self.comment = self.create_comment(self.kellynim, self.tweet)

    def test_comment(self):
        self.assertNotEqual(self.comment.__str__(), None)

    def test_like_test(self):
        self.create_like(self.kellynim, self.comment)
        self.assertEqual(self.comment.like_set.count(), 1)

        self.create_like(self.kellynim, self.comment)
        self.assertEqual(self.comment.like_set.count(), 1)

        talenti = self.create_user('talenti')
        self.create_like(talenti, self.comment)
        self.assertEqual(self.comment.like_set.count(), 2)
