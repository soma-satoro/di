from world.wod20th.models import Stat
from world.wod20th.sheet_defaults import ATTRIBUTES, ABILITIES, ADVANTAGES

def initialize_basic_stats():
    # Initialize Attributes
    for attr_name, attr_value in ATTRIBUTES.items():
        Stat.objects.get_or_create(
            name=attr_name,
            defaults={
                'description': f'Basic attribute: {attr_name}',
                'game_line': 'World of Darkness',
                'category': 'attributes',
                'stat_type': 'attribute',
                'values': list(range(6)),  # 0 to 5
                'default': attr_value
            }
        )

    # Initialize Abilities
    for ability_category, abilities in ABILITIES.items():
        for ability_name, ability_value in abilities.items():
            Stat.objects.get_or_create(
                name=ability_name,
                defaults={
                    'description': f'{ability_category} ability: {ability_name}',
                    'game_line': 'World of Darkness',
                    'category': 'abilities',
                    'stat_type': ability_category.lower(),
                    'values': list(range(6)),  # 0 to 5
                    'default': ability_value
                }
            )

    # Initialize Advantages
    for advantage_category, advantages in ADVANTAGES.items():
        for advantage_name, advantage_value in advantages.items():
            Stat.objects.get_or_create(
                name=advantage_name,
                defaults={
                    'description': f'{advantage_category} advantage: {advantage_name}',
                    'game_line': 'World of Darkness',
                    'category': 'advantages',
                    'stat_type': advantage_category.lower(),
                    'values': list(range(11)),  # 0 to 10
                    'default': advantage_value
                }
            )

    print("Basic stats initialized successfully.")