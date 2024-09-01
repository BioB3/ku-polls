"""A module that contains views for the polls application."""
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from .models import Question, Choice


class IndexView(generic.ListView):
    """Display the most recent 5 poll questions.

    :return: a rendered template with the most recent 5 questions
    """

    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the last five published questions.

        (not including those set to be published in the future).
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    """Display the detail of a question.

    :param pk: primary key of the question
    :return: a rendered template with the question's details
    """

    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """Excludes any questions that aren't published yet."""
        return Question.objects.filter(pub_date__lte=timezone.now())

    def get(self, request, *args, **kwargs):
        """Get the question object.

        Redirect the visitor to the index page with an error message
        if the Question with entered ID does not exist or
        unavailable for voting

        :param request: request from the vistior
        :param *args: arguments
        :param *kwargs: keyword arguments
        """
        try:
            question = get_object_or_404(Question, pk=kwargs["pk"])
        except Http404:
            messages.error(request, f"Poll ID {kwargs['pk']} does not exist.")
            return HttpResponseRedirect(reverse("polls:index"))
        if not question.can_vote():
            messages.error(request,
                           f"Voting is unavailable for Poll ID {kwargs['pk']}.")
            return HttpResponseRedirect(reverse("polls:index"))
        return super().get(request, *args, **kwargs)


class ResultsView(generic.DetailView):
    """Display the result of a question.

    :return: a rendered template with the question's result
    """

    model = Question
    template_name = 'polls/results.html'

    def get(self, request, *args, **kwargs):
        """Get the question object.

        Redirect the visitor to the index page with an error message
        if the Question with entered ID does not exist,
        is not published or the results are unavailable.

        :param request: request from the vistior
        :param *args: arguments
        :param *kwargs: keyword arguments
        """
        try:
            question = get_object_or_404(Question, pk=kwargs["pk"])
        except Http404:
            messages.error(request, f"Poll ID {kwargs['pk']} does not exist.")
            return HttpResponseRedirect(reverse("polls:index"))
        if not question.is_published():
            messages.error(request,
                           f"Results for Poll ID {kwargs['pk']} are unavailable")
            return HttpResponseRedirect(reverse("polls:index"))
        return super().get(request, *args, **kwargs)


def vote(request, question_id):
    """Handle voting in a question.

    :param request: request from the visitor
    :param question_id: id of the question
    :return: redirect to the result page or
             the detail page with error message if no choice was selected
    """
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        messages.error(request, "You didn't select a choice.")
        return HttpResponseRedirect(reverse('polls:detail',
                                            args=(question_id,)))
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results',
                                            args=(question_id,)))
