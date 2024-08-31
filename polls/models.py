"""
A module that contains the Question and Choice model
for the polls application.
"""
import datetime
from django.db import models
from django.utils import timezone


class Question(models.Model):
    """
    Stores the text and publication date of questions as a table in the database.
    """
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published', default=timezone.now)
    end_date = models.DateTimeField('ending date for voting',
                                    default=None, null=True, blank=True)
    def __str__(self):
        """
        :return: The text of the question
        """
        return self.question_text

    def was_published_recently(self):
        """
        Check whether the question was published within the last 24 hours.

        :return: True if pub_date is within the last 24 hours,
                 False otherwise
        """
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def is_published(self):
        """
        Check whether the question is published.
        
        :return: True if current date-time is on or after question's publication date,
                 False otherwise
        """
        now = timezone.now()
        return now >= self.pub_date

    def can_vote(self):
        """
        Check whether voting is available for the question.
        
        :return: True if voting is allowed for this question,
                 False otherwise
        """
        now = timezone.now()
        if self.end_date is not None:
            return self.end_date > now >= self.pub_date
        else:
            return now >= self.pub_date


class Choice(models.Model):
    """
    Stores the text and votes count of choices as a table in the database,
    related to :model:'Question'.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        """
        :return: The text of the choice
        """
        return self.choice_text
