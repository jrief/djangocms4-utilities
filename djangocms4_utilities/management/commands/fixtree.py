from django.db.models import Q
from djangocms4_utilities.utilities import plugintree

from cms.models.placeholdermodel import Placeholder

from .base import BaseCommand


class Command(BaseCommand):
    args = '<none>'
    help = 'Runs fix_tree for every draft placeholder'

    def add_arguments(self, parser):
        parser.add_argument('--page-url', type=str, help="Fix plugin tree for specified page. Default is all.")

    def handle(self, *args, **options):
        if options['page_url']:
            page_content = self.get_pagecontent_from_path(options['page_url'])
            for placeholder in plugintree.get_draft_placeholders(page_content):
                plugintree.fix_tree(placeholder, page_content.language)
        else:
            for placeholder in plugintree.get_draft_placeholders():
                self.stdout.write(f"Fixing placeholder {placeholder.slot} (id={placeholder.id})")
                plugintree.fix_tree(placeholder)
