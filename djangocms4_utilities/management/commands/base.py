from django.conf import settings
from django.core.management import base

from cms.models.pagemodel import PageUrl
from cms.utils import get_current_site


class BaseCommand(base.BaseCommand):
    def get_pagecontent_from_path(self, url):
        site = get_current_site()
        path = url
        for language, _ in settings.LANGUAGES:
            if path.startswith(f'/{language}/'):
                path = path[len(language) + 2:]
                break
        else:
            language = None
            if path.startswith('/'):
                path = path[1:]
        if path.endswith('/'):
            path = path[:-1]

        try:
            page_url = PageUrl.objects.get_for_site(site).get(path=path, language=language)
        except PageUrl.DoesNotExist:
            self.stderr.write(f"Page URL '{path}' not found.")
            raise
        return page_url.page.get_content_obj(language)
