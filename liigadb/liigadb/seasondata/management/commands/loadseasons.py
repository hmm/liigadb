#!/usr/bin/env python

from django.core.management.base import BaseCommand

from liigadb.seasondata.dataloader import loadseasons, loadplayoffs, calculate

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--playoffs',
                            action='store_true',
                            dest='playoffs',
                            default=False)
        parser.add_argument('--calculate',
                            action='store_true',
                            dest='calculate',
                            default=False)
        parser.add_argument('path', nargs='?', type=str)

    def handle(self, *args, **kwargs):
        if kwargs.get('playoffs'):
            loadplayoffs(kwargs['path'])
        elif kwargs.get('calculate'):
            calculate()
        else:
            loadseasons(kwargs['path'])
        
