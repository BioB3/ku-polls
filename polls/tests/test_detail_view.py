"""Tests for the Detail view of KU Polls."""
from django.test import TestCase
from django.urls import reverse

from polls.tests.question_creation import create_question


class QuestionDetailViewTests(TestCase):
    """Tests for QuestionDetailView."""

    def test_future_question(self):
        """Detail view redirect to index page for future questions.

        The detail view of a question with a pub_date in the future
        redirect user to index page with error message.
        """
        future_question = create_question(question_text='Future question.',
                                          days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertRedirects(response, '/polls/', status_code=302,
                             target_status_code=200)

    def test_past_question(self):
        """Questions text are displayed for past question.

        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text='Past question.',
                                        days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
