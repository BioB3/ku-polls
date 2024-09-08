"""Question creation function for tests."""
import datetime
from django.utils import timezone
from polls.models import Question


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
