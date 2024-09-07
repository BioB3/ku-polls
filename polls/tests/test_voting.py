"""Tests of voting for KU Polls."""
from django.test import TestCase

from polls.models import Question
from polls.tests.question_creation import create_question, create_question_with_end_date


class CanVoteTests(TestCase):
    """Tests for can_vote method in Question model."""

    def test_can_vote_no_end_date(self):
        """Can vote if the end_date is null."""
        forever_question = Question.objects.create(
            question_text="Forever Question")
        self.assertIs(forever_question.can_vote(), True)

    def test_cannot_vote_not_published(self):
        """Cannot vote if the question is not published."""
        future_question = create_question(
            question_text="Future Question", days=30)
        self.assertIs(future_question.can_vote(), False)

    def test_can_vote_before_end_date(self):
        """Can vote for published question if the end_date is in the future."""
        question1 = create_question_with_end_date(question_text="Question 1",
                                                  pub_days=0, end_days=30)
        self.assertIs(question1.can_vote(), True)

    def test_cannot_vote_after_end_date(self):
        """Cannot vote if the end_date is in the past."""
        ended_question = create_question_with_end_date(
            question_text="Ended Question", pub_days=-30, end_days=-1)
        self.assertIs(ended_question.can_vote(), False)

    def test_cannot_vote_exactly_at_end_date(self):
        """Cannot vote if the end_date is the current time."""
        question1 = create_question_with_end_date(
            question_text="Question 1", pub_days=-1, end_days=0)
        self.assertIs(question1.can_vote(), False)
