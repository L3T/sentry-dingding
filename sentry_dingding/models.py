"""
sentry_dingding.models
~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2011 by Linovia, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from __future__ import unicode_literals

import requests
from django import forms
from sentry.plugins.bases.notify import NotifyPlugin
import sentry_dingding


class DingDingOptionsForm(forms.Form):
    endpoint = forms.CharField(help_text="DingDing Endpoint", required=True,
                               widget=forms.TextInput(attrs={'placeholder': 'dingding endpoint'}))


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
        server_name = event.get_tag('server_name')
        try:
            exception = event.get_interfaces()['sentry.interfaces.Exception'].to_string(event)
            msg = exception.replace('  ', '&emsp;').replace('\n', '</br>')
        except KeyError:
            msg = event.error()
        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": '{project_name}:{level}'.format(
                    project_name=project,
                    level=level,
                ),
                "text": '''## {project_name}@{server_name}:{level}
{msg}
> [view]({link})
                '''.format(
                    project_name=project,
                    level=level,
                    msg=msg,
                    server_name=server_name,
                    link=link,
                ),
            },
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
