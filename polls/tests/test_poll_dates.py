"""Tests of Question publication date."""
import datetime
from django.test import TestCase
from django.utils import timezone

from polls.models import Question
from polls.tests.question_creation import create_question


class WasPublishedRecentlyTests(TestCase):
    """Tests for was_published_recently method in Question model."""

    def test_was_published_recently_with_future_question(self):
        """Future questions weren't published recently."""
        future_question = create_question('', 30)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """1 or more days old questions weren't published recently."""
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """Less than 24 hours old questions were published recently."""
        time = timezone.now() - datetime.timedelta(
            hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


class IsPublishedTests(TestCase):
    """Tests for is_published method in Question model."""

    def test_is_published_with_future_question(self):
        """Questions whose pub_date are in the future are not published."""
        future_question = create_question(
            question_text="Future Question", days=30)
        self.assertIs(future_question.is_published(), False)

    def test_is_published_with_default_pub_date(self):
        """Questions whose pub_date are the current time are published."""
        default_question = Question.objects.create(
            question_text="Default Question")
        self.assertIs(default_question.is_published(), True)

    def test_is_published_with_old_question(self):
        """Questions whose pub_date are in the pass are not published."""
        old_question = create_question(question_text="Old Question", days=-30)
        self.assertIs(old_question.is_published(), True)
