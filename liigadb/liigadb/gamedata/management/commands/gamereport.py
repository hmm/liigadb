#!/usr/bin/env python

from django.core.management.base import BaseCommand

from liigadb.gamedata.gamereports import runreport

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--limit',
                            dest='limit',
                            default=25)

        parser.add_argument('--homeaway',
                            dest='homeaway',
                            choices=['both', 'home', 'away'],
                            default='both')
                            
        parser.add_argument('report', nargs='?', type=str)

    def handle(self, report, limit, homeaway, *args, **kwargs):
        runreport(report, limit=limit, homeaway=homeaway)
        
