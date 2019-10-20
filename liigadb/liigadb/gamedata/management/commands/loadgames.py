#!/usr/bin/env python

from django.core.management.base import BaseCommand

from liigadb.gamedata.dataloader import loaddata, analyze, calendar, calculate, calendarcalc, oldliiga

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--analyze',
                            action='store_true',
                            dest='analyze',
                            default=False)
        parser.add_argument('--oldliiga',
                            action='store_true',
                            dest='oldliiga',
                            default=False)
        parser.add_argument('--calendar',
                            action='store_true',
                            dest='calendar',
                            default=False)
        parser.add_argument('--calculate',
                            action='store_true',
                            dest='calculate',
                            default=False)
        parser.add_argument('path', nargs='?', type=str)

    def handle(self, *args, **kwargs):
        if kwargs.get('oldliiga'):
            oldliiga(kwargs['path'])
        elif kwargs.get('analyze'):
            analyze(kwargs['path'])
        elif kwargs.get('calendar'):
            if kwargs.get('calculate'):
                calendarcalc()
            else:
                calendar(kwargs['path'])
        elif kwargs.get('calculate'):
            calculate(kwargs['path'])
        else:
            loaddata(kwargs['path'])
        
