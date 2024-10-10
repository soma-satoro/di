import json
import os
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django.db import connection, IntegrityError

# Import Evennia and initialize it
import evennia
evennia._init()

# Ensure Django settings are configured
import django
django.setup()

# Import the Stat model
from world.wod20th.models import Stat, CATEGORIES, STAT_TYPES

class Command(BaseCommand):
    help = 'Load WoD20th stats from a folder containing JSON files'

    def add_arguments(self, parser):
        parser.add_argument('json_folder', type=str, help='Path to the folder containing JSON files with stats')

    def handle(self, *args, **kwargs):
        json_folder = kwargs['json_folder']
        
        if not os.path.isdir(json_folder):
            self.stdout.write(self.style.ERROR(f'Folder {json_folder} not found.'))
            return

        self.stdout.write(self.style.NOTICE(f'Starting to process files in folder: {json_folder}'))

        for filename in os.listdir(json_folder):
            if filename.endswith('.json'):
                file_path = os.path.join(json_folder, filename)
                self.stdout.write(self.style.NOTICE(f'Processing file: {file_path}'))
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        stats_data = json.load(file)
                        self.stdout.write(self.style.SUCCESS(f'Successfully loaded JSON data from {file_path}'))
                except FileNotFoundError:
                    self.stdout.write(self.style.ERROR(f'File {file_path} not found.'))
                    continue
                except json.JSONDecodeError:
                    self.stdout.write(self.style.ERROR(f'Error decoding JSON from file {file_path}.'))
                    continue
                except UnicodeDecodeError as e:
                    self.stdout.write(self.style.ERROR(f'Error reading file {filename}: {str(e)}. This file might not be UTF-8 encoded.'))
                    continue
                
                for stat_data in stats_data:
                    self.stdout.write(self.style.NOTICE(f'Processing stat data: {stat_data}'))
                    
                    name = stat_data.get('name')
                    if not name:
                        self.stdout.write(self.style.ERROR('Missing stat name in data. Skipping entry.'))
                        continue
                    
                    description = stat_data.get('description', '')
                    game_line = stat_data.get('game_line')
                    category = stat_data.get('category')
                    stat_type = stat_data.get('stat_type')
                    values = stat_data.get('values', [])
                    lock_string = stat_data.get('lock_string', '')
                    default = stat_data.get('default', '')
                    instanceed = stat_data.get('instanced', False)
                    splat = stat_data.get('splat', None)
                    hidden = stat_data.get('hidden', False)
                    locked = stat_data.get('locked', False)


                    # Data validation
                    if not game_line:
                        self.stdout.write(self.style.ERROR(f'Missing game_line for stat {name}. Skipping entry.'))
                        continue

                    if not category:
                        self.stdout.write(self.style.WARNING(f'Missing category for stat {name}. Using "other".'))
                        category = 'other'

                    if not stat_type:
                        self.stdout.write(self.style.WARNING(f'Missing stat_type for stat {name}. Using "other".'))
                        stat_type = 'other'

                    # Ensure category is valid
                    if category not in dict(CATEGORIES):
                        self.stdout.write(self.style.WARNING(f'Invalid category "{category}" for stat {name}. Using "other".'))
                        category = 'other'

                    # Ensure stat_type is valid
                    if stat_type not in dict(STAT_TYPES):
                        self.stdout.write(self.style.WARNING(f'Invalid stat_type "{stat_type}" for stat {name}. Using "other".'))
                        stat_type = 'other'

                    # Ensure values is a list
                    if not isinstance(values, list):
                        if isinstance(values, dict):
                            values_list = []
                            for key in ['permanent', 'temporary', 'perm', 'temp']:
                                if key in values:
                                    values_list.extend(values[key])
                            values = values_list
                        else:
                            self.stdout.write(self.style.WARNING(f'Invalid values for stat {name}. Using empty list.'))
                            values = []

                    # Create new stat
                    try:
                        stat = Stat(
                            name=name,
                            description=description,
                            game_line=game_line,
                            category=category,
                            stat_type=stat_type,
                            values=values,
                            lock_string=lock_string,
                            default=default,
                            instanced=instanceed,
                            splat=splat,
                            hidden=hidden,
                            locked=locked
                        )
                        stat.save()
                        self.stdout.write(self.style.SUCCESS(f'Successfully created stat: {name}'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error creating stat {name}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('Finished processing all files.'))
