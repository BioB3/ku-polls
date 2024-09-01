"""A module that contains tests for the polls application."""
import datetime
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from .models import Question


def create_question(question_text, days):
    """Create question without end_date.

    Create a question with the given 'question_text' and published the
    given number of 'days' offset to now (negative for questions
    published in the past, positive for questions that have yet to be
    published). The created question has end_date set to None.

    :param question_text: the text of the question to be created
    :param days: the number of days offset for the question's pub_date
    :return: a Question with question_text as the text and the current time
             + days amount of offset as the publication date
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


def create_question_with_end_date(question_text, pub_days, end_days):
    """Create question with end_date.

    Create a question with the given 'question_text', published the
    given number of 'pub_days' offset to now and has an end date of
    'end_days' offset to now.

    :param question_text: the text of the question to be created
    :param pub_days: the number of days offset for the question's pub_date
    :param end_days: the number of days offset for the question's end_date
    :return: a Question with question_text as the text, the current time
             + pub_days amount of offset as the publication date and
             the current time + end_days amount of offset as the end date
    """
    pub_date = timezone.now() + datetime.timedelta(days=pub_days)
    end_date = timezone.now() + datetime.timedelta(days=end_days)
    return Question.objects.create(question_text=question_text,
                                   pub_date=pub_date, end_date=end_date)


class QuestionIndexViewTests(TestCase):
    """Tests for QuestionIndexView."""

    def test_no_question(self):
        """If no questions exist, an appropriate message is displayed."""
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """Questions with pub_date in the past are displayed on index page."""
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerySetEqual(response.context['latest_question_list'],
                                 [question],)

    def test_future_question(self):
        """Questions with pub_date in the future aren't displayed."""
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available")
        self.assertQuerySetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """Only past questions are displayed."""
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerySetEqual(response.context['latest_question_list'],
                                 [question],)

    def test_two_past_questions(self):
        """The questions index page may display multiple questions."""
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerySetEqual(response.context['latest_question_list'],
                                 [question2, question1],)


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
