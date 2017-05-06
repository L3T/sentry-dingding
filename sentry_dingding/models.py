"""
sentry_dingding.models
~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2011 by Linovia, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
import requests
from django import forms
from sentry.plugins.bases.notify import NotifyPlugin
import sentry_dingding


class DingDingOptionsForm(forms.Form):
    endpoint = forms.CharField(help_text="DingDing Endpoint", required=True,
                               widget=forms.TextInput(attrs={'placeholder': 'dingding endpoint'}))
    at_all = forms.BooleanField(help_text="@all", required=False,
                                widget=forms.TextInput(attrs={'placeholder': '@all?'}))


class DingDingMessage(NotifyPlugin):
    author = 'Zhang Yunyu'
    author_url = 'https://github.com/linovia/sentry-dingding'
    version = sentry_dingding.VERSION
    description = "Event notification to DingDing."
    resource_links = [
        ('Bug Tracker', 'https://github.com/linovia/sentry-dingding/issues'),
        ('Source', 'https://github.com/linovia/sentry-dingding'),
    ]
    slug = 'dingding'
    title = 'DingDing'
    conf_title = title
    conf_key = 'dingding'
    project_conf_form = DingDingOptionsForm

    def is_configured(self, project):
        return bool(self.get_option('endpoint', project))

    def notify_users(self, group, event, fail_silently=False):
        project = event.project
        level = group.get_level_display().upper()
        link = group.get_absolute_url()
        endpoint = self.get_option('endpoint', project)
        at_all = bool(self.get_option('at_all', project))
        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": "{level}".format(level=level),
                "text": "#### {project_name}\n".format(project_name=project.name) +
                        "{message}\n".format(message=event.error()) +
                        "> [view]({link}) \n".format(link=link)
            },
            "at": {
                "atMobiles": [],
                "isAtAll": at_all
            }
        }
        self.send_payload(
            endpoint=endpoint,
            data=data
        )

    def send_payload(self, endpoint, data):
        requests.post(
            endpoint,
            json=data,
        )
