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
    pub_date = models.DateTimeField('date published')

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
