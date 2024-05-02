from djangocms4_utilities.utilities import plugintree

from cms.models.placeholdermodel import Placeholder

from .base import BaseCommand


class Command(BaseCommand):
    args = '<none>'
    help = 'Runs check_tree for every draft placeholder and prints inconsistencies ' \
           'to the console'

    def add_arguments(self, parser):
        parser.add_argument('--page-url', type=str, help="Check plugin tree for specified page. Default is all.")

    def handle(self, *args, **options):
        if options['page_url']:
            page_content = self.get_pagecontent_from_path(options['page_url'])
            placeholders = Placeholder.objects.get_for_obj(page_content)
        else:
            placeholders = None
        plugintree.check_placeholders(placeholders=placeholders)
