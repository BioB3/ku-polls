"""Tests of voting for KU Polls."""
from django.test import TestCase
from django.urls import reverse

from polls.models import Choice, Question
from django.contrib.auth.models import User
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


class VotingTest(TestCase):
    """Test of voting function."""

    def setUp(self):
        super().setUp()
        self.username = "testuser"
        self.password = "FatChance!"
        self.user1 = User.objects.create_user(
                         username=self.username,
                         password=self.password,
                         email="testuser@nowhere.com"
                         )
        self.user1.first_name = "Tester"
        self.user1.save()
        q = Question.objects.create(question_text="First Poll Question")
        q.save()
        for n in range(1,4):
            choice = Choice(choice_text=f"Choice {n}", question=q)
            choice.save()
        self.question = q
        self.url = reverse('polls:vote', args=[self.question.id])
        self.choice = self.question.choice_set.first()
        self.client.login(username=self.username, password=self.password)

    def test_user_can_vote(self):
        """Users can vote on a poll."""
        form_data = {"choice": f"{self.choice.id}"}
        response = self.client.post(self.url, form_data)
        self.assertEqual(response.status_code, 302)
        results = reverse('polls:results', args=(self.question.id,))
        self.assertRedirects(response, results, status_code=302,
                             target_status_code=200)
        self.assertEqual(self.choice.votes, 1)

    def test_user_change_vote(self):
        """Users can change the vote they have submitted."""
        changed_choice = self.question.choice_set.last()
        form_data_1 = {"choice": f"{self.choice.id}"}
        form_data_2 = {"choice": f"{changed_choice.id}"}
        self.client.post(self.url, form_data_1)
        self.client.post(self.url, form_data_2)
        self.assertEqual(self.choice.votes, 0)
        self.assertEqual(changed_choice.votes, 1)

    def test_one_vote_per_poll(self):
        """Users get only one vote on a poll question."""
        form_data = {"choice": f"{self.choice.id}"}
        for _ in range(3):
            self.client.post(self.url, form_data)
        self.assertEqual(self.choice.votes, 1)