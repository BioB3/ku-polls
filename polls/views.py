"""A module that contains views for the polls application."""
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.contrib.auth.decorators import login_required
from django.dispatch import receiver
from .models import Question, Choice, Vote
import logging

logger = logging.getLogger("polls")


class IndexView(generic.ListView):
    """Display the most recent 5 poll questions.

    :return: a rendered template with the most recent 5 questions
    """

    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return published questions ordered by publication date.

        (not including those set to be published in the future).
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()).order_by('-pub_date')


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
        except Http404 as ex:
            logger.exception(f"Non-existent question {kwargs['pk']} %s", ex)
            messages.error(request, f"Poll ID {kwargs['pk']} does not exist.")
            return HttpResponseRedirect(reverse("polls:index"))
        if not question.can_vote():
            messages.error(request,
                           f"Voting is unavailable for Poll ID {kwargs['pk']}.")
            return HttpResponseRedirect(reverse("polls:index"))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Create context dictionary used to render the template."""
        context = super().get_context_data(**kwargs)
        user = self.request.user
        try: 
            selected_choice = kwargs["object"].choice_set.filter(
                vote__user=user).first()
            vote = Vote.objects.get(user=user, choice=selected_choice)
        except (KeyError, Vote.DoesNotExist):
            logger.exception(f"Vote for question #{kwargs['object'].id}"
                             f" from {user.username} does not exist")
            vote = None
        except TypeError:
            logger.exception(f"Cannot retrieve vote for unauthenticated visitor")
            vote = None
        context['vote'] = vote
        return context


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
        except Http404 as ex:
            logger.exception(f"Non-existent question {kwargs['pk']} %s", ex)
            messages.error(request, f"Poll ID {kwargs['pk']} does not exist.")
            return HttpResponseRedirect(reverse("polls:index"))
        if not question.is_published():
            messages.error(request,
                           f"Results for Poll ID {kwargs['pk']} are unavailable")
            return HttpResponseRedirect(reverse("polls:index"))
        return super().get(request, *args, **kwargs)

@login_required
def vote(request, question_id):
    """Handle voting in a question.

    :param request: request from the visitor
    :param question_id: id of the question
    :return: redirect to the result page or
             the detail page with error message if no choice was selected
    """
    question = get_object_or_404(Question, pk=question_id)
    user = request.user
    try:
        logger.info(f"{user.username} voted for choice "
                    f"{request.POST['choice']} in question {question_id}")
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        logger.exception(f"{user.username} did not select a choice")
        messages.error(request, "You didn't select a choice.")
        return HttpResponseRedirect(reverse('polls:detail',
                                            args=(question_id,)))

    try:
        vote = request.user.vote_set.get(choice__question=question)
        vote.choice = selected_choice
        vote.save()
        messages.success(request,
                         f"Your vote was changed to '{selected_choice.choice_text}'.")
    except (KeyError, Vote.DoesNotExist):
        vote = Vote.objects.create(user=request.user, choice=selected_choice)
        messages.success(request,
                         f"You voted for '{selected_choice.choice_text}'.")

    return HttpResponseRedirect(reverse('polls:results', args=(question_id,)))

def get_client_ip(request):
    """Get the visitor's IP address using request headers."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@receiver(user_logged_in)
def user_login(sender, request, user, **kwargs):
    """Log successful login."""
    ip = get_client_ip(request)
    logger.info(f"user {user.username} logged in via ip: {ip}")

@receiver(user_logged_out)
def user_logout(sender, request, user, **kwargs):
    """Log successful logout."""
    ip = get_client_ip(request)
    logger.info(f"user {user.username} logged out via ip: {ip}")

@receiver(user_login_failed)
def user_login_failed(sender, request, credentials, **kwargs):
    """Log unsuccessful login"""
    ip = get_client_ip(request)
    logger.warning(f"login failed for {credentials['username']} from ip: {ip}")
