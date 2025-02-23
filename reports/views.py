import pytz

from .tasks import generate_tiktok_report

from ddm.participation.models import Participant
from ddm.projects.models import DonationProject

from django.conf import settings
from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import TemplateView
from django.http import JsonResponse

from .utils.data_processing import load_csv_as_dict
from .utils.constants import (
    PUBLIC_TEMPORAL_PLOT_KEY,
    PUBLIC_PARTY_DISTRIBUTION_ALL_ACCOUNTS_KEY,
    PUBLIC_VIEWS_BARS_ALL_ACCOUNTS_KEY,
    PUBLIC_LIKES_BARS_ALL_ACCOUNTS_KEY,
    PUBLIC_HT_WORDCLOUD_KEY
)
from scraper.hashtags import HASHTAG_LIST

if not settings.DEBUG:
    from celery.result import AsyncResult

utc = pytz.UTC


class TikTokReportLoading(TemplateView):
    template_name = 'reports/loading.html'
    project_pk = settings.REPORT_PROJECT_PK

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project = self.get_project()

    def get_project(self):
        return DonationProject.objects.filter(url_id=self.project_pk).first()

    def get_participant(self):
        """
        Returns the participant object. If no Participant object is found,
        returns a http 404 response.
        """
        participant_id = self.kwargs.get('participant_id')
        return get_object_or_404(Participant, external_id=participant_id)

    def get(self, request, *args, **kwargs):
        # For local development, run synchronously and redirect immediately
        if settings.DEBUG:
            participant = self.get_participant()
            result = generate_tiktok_report(
                participant.pk, 
                self.project.secret_key, 
                self.project.get_salt()
            )
            # Store result in cache with a temporary "task_id"
            task_id = f"local_{participant.pk}"
            cache.set(task_id, result, timeout=3600)  # Cache for 1 hour
            return redirect(reverse(
                'reports:tiktok_report_result',
                kwargs={'task_id': task_id}
            ))
        
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if not settings.DEBUG:
            # Original Celery logic for production
            participant = self.get_participant()
            task_result = generate_tiktok_report.delay(
                participant.pk, self.project.secret_key, self.project.get_salt())

            task_id = task_result.id
            if task_id:
                result = AsyncResult(task_id)
                if result.ready():
                    context['redirect_url'] = reverse(
                        'reports:tiktok_report_result',
                        kwargs={'task_id': task_id}
                    )
                context['task_id'] = task_id
        return context


class TikTokReportResults(TemplateView):
    template_name = 'reports/base.html'

    def add_static_public_plots(self, context):
        """ Add static public plots to context. """
        context['public_party_distribution_temporal_all_accounts'] = cache.get(
            PUBLIC_TEMPORAL_PLOT_KEY)
        context['public_party_distribution_all_accounts'] = cache.get(
            PUBLIC_PARTY_DISTRIBUTION_ALL_ACCOUNTS_KEY)
        context['public_views_bars_all_accounts'] = cache.get(
            PUBLIC_VIEWS_BARS_ALL_ACCOUNTS_KEY)
        context['public_likes_bars_all_accounts'] = cache.get(
            PUBLIC_LIKES_BARS_ALL_ACCOUNTS_KEY)
        context['hashtag_cloud_germany'] = cache.get(
            PUBLIC_HT_WORDCLOUD_KEY)
        return

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task_id = self.kwargs.get('task_id')

        if task_id:
            if settings.DEBUG and task_id.startswith('local_'):
                # Get result from cache in local development
                result = cache.get(task_id)
            else:
                # Get result from Celery in production
                result = AsyncResult(task_id).get()

            if result:
                context.update({
                    'no_watch_history': result['no_watch_history'],
                    'matches': result['matches'],
                    'n_videos': result.get('n_videos', 0),
                    'n_matched': result.get('n_matched', 0),
                    'share_political': result.get('share_political', 0),
                })

                if result['matches']:
                    context.update(result['plots'])

                self.add_static_public_plots(context)

        return context


class HashtagsView(TemplateView):
    template_name = 'reports/hashtags.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Load accounts and their parties
        csv_path = './reports/static/reports/csv/actor_party_mapping.csv'
        context['accounts'] = load_csv_as_dict(csv_path)

        # Load hashtags from scraper/hashtags.py
        context['hashtags'] = sorted(HASHTAG_LIST)  # Sort alphabetically

        return context


def check_task_status(request, task_id):
    try:
        if settings.DEBUG and task_id.startswith('local_'):
            # In local development, task is always ready
            return JsonResponse({
                'ready': True,
                'status': 'SUCCESS',
                'redirect_url': reverse(
                    'reports:tiktok_report_result',
                    kwargs={'task_id': task_id})
            })
        
        # Original Celery logic for production
        result = AsyncResult(task_id)
        ready = result.ready()

        if ready and result.failed():
            return JsonResponse({
                'ready': False,
                'error': 'Task failed',
                'status': result.status
            })

        return JsonResponse({
            'ready': ready,
            'status': result.status,
            'redirect_url': reverse(
                'reports:tiktok_report_result',
                kwargs={'task_id': task_id}) if ready else None
        })
    except Exception as e:
        return JsonResponse({
            'ready': False,
            'error': str(e),
            'status': 'ERROR'
        }, status=500)
