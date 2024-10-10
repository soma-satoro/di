from evennia import default_cmds
from world.wod20th.models import Stat, SHIFTER_IDENTITY_STATS, SHIFTER_RENOWN

# Define the allowed identity stats for each shifter type
SHIFTER_IDENTITY_STATS = {
    "Garou": ["Tribe", "Breed", "Auspice"],
    "Gurahl": ["Tribe", "Breed", "Auspice"],
    "Rokea": ["Tribe", "Breed", "Auspice"],
    "Ananasi": ["Aspect", "Ananasi Faction", "Breed", "Ananasi Cabal"],
    "Ajaba": ["Aspect", "Breed"],
    "Bastet": ["Tribe", "Breed"],
    "Corax": ["Breed"],
    "Kitsune": ["Kitsune Path", "Kitsune Faction", "Breed"],
    "Mokole": ["Varnas", "Stream", "Breed"],
    "Nagah": ["Crown", "Breed", "Auspice"],
    "Nuwisha": ["Breed"],
    "Ratkin": ["Aspect", "Plague", "Breed"]
}

class CmdStats(default_cmds.MuxCommand):
    """
    Usage:
      +stats <character>/<stat>[(<instance>)]/<category>=[+-]<value>
      +stats me/<stat>[(<instance>)]/<category>=[+-]<value>
      +stats <character>=reset
      +stats me=reset

    Examples:
      +stats Bob/Strength/Physical=+2
      +stats Alice/Firearms/Skill=-1
      +stats John/Status(Ventrue)/Social=
      +stats me=reset
      +stats me/Strength=3
    """

    key = "stats"
    aliases = ["stat"]
    locks = "cmd:perm(Builder)"  # Only Builders and above can use this command
    help_category = "Chargen & Character Info"

    def parse(self):
        """
        Parse the arguments.
        """
        self.character_name = ""
        self.stat_name = ""
        self.instance = None
        self.category = None
        self.value_change = None
        self.temp = False

        try:
            args = self.args.strip()

            if '=' in args:
                first_part, second_part = args.split('=', 1)
                if second_part.lower().strip() == 'reset':
                    self.character_name = first_part.strip()
                    self.stat_name = 'reset'
                    return
                self.value_change = second_part.strip()
            else:
                first_part = args

            if '/' in first_part:
                self.character_name, stat_part = first_part.split('/', 1)
            else:
                self.character_name = first_part
                stat_part = ''

            try:
                if '(' in stat_part and ')' in stat_part:
                    self.stat_name, instance_and_category = stat_part.split('(', 1)
                    self.instance, self.category = instance_and_category.split(')', 1)
                    self.category = self.category.lstrip('/').strip() if '/' in self.category else None
                else:
                    parts = stat_part.split('/')
                    if len(parts) == 3:
                        self.stat_name, self.instance, self.category = parts
                    elif len(parts) == 2:
                        self.stat_name, self.category = parts
                    else:
                        self.stat_name = parts[0]

                    self.stat_name = self.stat_name.strip()
                    self.instance = self.instance.strip() if self.instance else None
                    self.category = self.category.strip() if self.category else None

            except ValueError:
                self.stat_name = stat_part.strip()
            except UnboundLocalError:
                self.stat_name = stat_part.strip()

        except ValueError:
            self.character_name = self.stat_name = self.value_change = self.instance = self.category = None

    def func(self):
        """Implement the command"""

        if not self.character_name:
            self.caller.msg("|rUsage: +stats <character>/<stat>[(<instance>)]/[<category>]=[+-]<value>|n")
            return

        if self.character_name.lower().strip() == 'me':
            character = self.caller
        else:
            character = self.caller.search(self.character_name)

        if not character:
            self.caller.msg(f"|rCharacter '{self.character_name}' not found.|n")
            return

        # Handle the reset command
        if self.stat_name and self.stat_name.lower() == 'reset':
            character.db.stats = {}
            self.caller.msg(f"|gReset all stats for {character.name}.|n")
            character.msg(f"|y{self.caller.name}|n |greset all your stats.|n")
            return

        if not self.stat_name:
            self.caller.msg("|rUsage: +stats <character>/<stat>[(<instance>)]/[<category>]=[+-]<value>|n")
            return

        # Fetch the stat definition from the database
        try:
            if self.category:
                matching_stats = Stat.objects.filter(name__icontains=self.stat_name.strip(), category__iexact=self.category.strip())
            else:
                matching_stats = Stat.objects.filter(name__icontains=self.stat_name.strip())
        except Exception as e:
            self.caller.msg(f"|rError fetching stats: {e}|n")
            return

        if not matching_stats.exists():
            self.caller.msg(f"|rNo stats matching '{self.stat_name}' found in the database.|n")
            return

        if len(matching_stats) > 1:
            self.caller.msg(f"|rMultiple stats matching '{self.stat_name}' found: {[stat.name for stat in matching_stats]}. Please be more specific.|n")
            return

        stat = matching_stats.first()
        full_stat_name = stat.name

        # Check if the stat is instanced and handle accordingly
        if stat.instanced:
            if not self.instance:
                self.caller.msg(f"|rThe stat '{full_stat_name}' requires an instance. Use the format: {full_stat_name}(instance)|n")
                return
            full_stat_name = f"{full_stat_name}({self.instance})"
        elif self.instance:
            self.caller.msg(f"|rThe stat '{full_stat_name}' does not support instances.|n")
            return

        # Check if the character passes the stat's lock_string
        try:
            if stat.lockstring and not character.locks.check_lockstring(character, stat.lockstring):
                self.caller.msg(f"|rYou do not have permission to modify the stat '{full_stat_name}' for {character.name}.|n")
                return
        except AttributeError:
            pass
        
        # Check if the stat being set is an identity stat for a shifter
        if character.get_stat('other', 'splat', 'Splat').lower() == 'shifter' and stat.category == 'identity':
            shifter_type = character.get_stat('identity', 'lineage', 'Type')
            if shifter_type and full_stat_name != 'Type':
                allowed_stats = SHIFTER_IDENTITY_STATS.get(shifter_type, [])
                if full_stat_name not in allowed_stats:
                    self.caller.msg(f"|rThe stat '{full_stat_name}' is not valid for {shifter_type} characters.|n")
                    return

        # Add this check before updating the stat
        if stat.category == 'pools':
            splat = character.get_stat('other', 'splat', 'Splat')
            valid_pools = ['Willpower']
            if splat.lower() == 'vampire':
                valid_pools.extend(['Blood', 'Road'])
            elif splat.lower() == 'shifter':
                valid_pools.extend(['Gnosis', 'Rage'])
            
            if full_stat_name not in valid_pools:
                self.caller.msg(f"|rThe pool '{full_stat_name}' is not valid for {splat}.|n")
                return

        # Determine if the stat should be removed
        if self.value_change == '':
            current_stats = character.db.stats.get(stat.category, {}).get(stat.stat_type, {})
            if full_stat_name in current_stats:
                del current_stats[full_stat_name]
                character.db.stats[stat.category][stat.stat_type] = current_stats
                self.caller.msg(f"|gRemoved stat '{full_stat_name}' from {character.name}.|n")
                character.msg(f"|y{self.caller.name}|n |rremoved your stat|n '|y{full_stat_name}|n'.")
            else:
                self.caller.msg(f"|rStat '{full_stat_name}' not found on {character.name}.|n")
            return

        # Determine if the stat value should be treated as a number or a string
        try:
            value_change = int(self.value_change)
            is_number = True
        except (ValueError, TypeError):
            value_change = self.value_change
            is_number = False

        # Check if the stat exists for the character and get the current value
        if not hasattr(character.db, "stats"):
            character.db.stats = {}

        current_value = character.get_stat(stat.category, stat.stat_type, full_stat_name, temp=self.temp)
        if current_value is None:
            # Initialize the stat if it doesn't exist
            current_value = 0 if is_number else ''

        if self.value_change and (self.value_change.startswith('+') or self.value_change.startswith('-')):
            if is_number:
                new_value = current_value + value_change
            else:
                self.caller.msg(f"|rIncrement/decrement values must be integers.|n")
                return
        else:
            new_value = value_change

        # Validate the new value against the stat's valid values
        valid_values = stat.values
        if valid_values and new_value not in valid_values and valid_values != []:
            self.caller.msg(f"|rValue '{new_value}' is not valid for stat '{full_stat_name}'. Valid values are: {valid_values}|n")
            return

        # Update the stat
        character.set_stat(stat.category, stat.stat_type, full_stat_name, new_value, temp=False)
        
        # If the stat is in the 'pools' category or has a 'dual' stat_type, update the temporary value as well
        if stat.category == 'pools' or stat.stat_type == 'dual':
            character.set_stat(stat.category, stat.stat_type, full_stat_name, new_value, temp=True)
            self.caller.msg(f"|gUpdated {character.name}'s {full_stat_name} to {new_value} (both permanent and temporary).|n")
            character.msg(f"|y{self.caller.name}|n |gupdated your|n '|y{full_stat_name}|n' |gto|n '|y{new_value}|n' |g(both permanent and temporary).|n")
        else:
            self.caller.msg(f"|gUpdated {character.name}'s {full_stat_name} to {new_value}.|n")
            character.msg(f"|y{self.caller.name}|n |gupdated your|n '|y{full_stat_name}|n' |gto|n '|y{new_value}|n'.")

        # If the stat is 'Type' for a Shifter, apply the correct pools and renown
        if full_stat_name == 'Type' and character.get_stat('other', 'splat', 'Splat').lower() == 'shifter':
            self.apply_shifter_pools(character, new_value)

        # If the stat is Willpower, update the temporary Willpower pool to match the permanent value
        if full_stat_name == 'Willpower':
            character.set_stat('pools', 'temporary', 'Willpower', new_value, temp=True)
            self.caller.msg(f"|gAlso updated {character.name}'s temporary Willpower pool to {new_value}.|n")
            character.msg(f"|gYour temporary Willpower pool has also been set to {new_value}.|n")

        # If the stat is 'Splat', apply the correct pools
        if full_stat_name == 'Splat':
            self.apply_splat_pools(character, new_value)

    def apply_splat_pools(self, character, splat):
        """Apply the correct pools based on the character's splat."""
        # Remove all existing pools except Willpower
        character.db.stats['pools'] = {k: v for k, v in character.db.stats.get('pools', {}).items() if k == 'Willpower'}

        # Add Willpower for all characters if it doesn't exist
        if 'Willpower' not in character.db.stats['pools']:
            character.set_stat('pools', 'dual', 'Willpower', 1, temp=False)
            character.set_stat('pools', 'dual', 'Willpower', 1, temp=True)

        if splat.lower() == 'vampire':
            # Add Vampire-specific pools
            character.set_stat('pools', 'dual', 'Blood', 10, temp=False)
            character.set_stat('pools', 'dual', 'Blood', 10, temp=True)
            character.set_stat('pools', 'moral', 'Road', 7, temp=False)
        elif splat.lower() == 'shifter':
            # Add default Shifter pools (will be adjusted in apply_shifter_pools if necessary)
            character.set_stat('pools', 'dual', 'Gnosis', 1, temp=False)
            character.set_stat('pools', 'dual', 'Gnosis', 1, temp=True)
            character.set_stat('pools', 'dual', 'Rage', 1, temp=False)
            character.set_stat('pools', 'dual', 'Rage', 1, temp=True)

        self.caller.msg(f"|gApplied default pools for {splat} to {character.name}.|n")
        character.msg(f"|gYour default pools for {splat} have been applied.|n")

    def apply_shifter_pools(self, character, shifter_type):
        """Apply the correct pools and renown based on the Shifter's type."""
        # Ensure Willpower exists
        if 'Willpower' not in character.db.stats.get('pools', {}):
            character.set_stat('pools', 'dual', 'Willpower', 1, temp=False)
            character.set_stat('pools', 'dual', 'Willpower', 1, temp=True)

        # Set Gnosis for all Shifter types
        character.set_stat('pools', 'dual', 'Gnosis', 1, temp=False)
        character.set_stat('pools', 'dual', 'Gnosis', 1, temp=True)

        if shifter_type == 'Ananasi':
            # Remove Rage if it exists
            if 'Rage' in character.db.stats.get('pools', {}):
                del character.db.stats['pools']['Rage']
            # Add Blood
            character.set_stat('pools', 'dual', 'Blood', 10, temp=False)
            character.set_stat('pools', 'dual', 'Blood', 10, temp=True)
        else:
            # Remove Blood if it exists
            if 'Blood' in character.db.stats.get('pools', {}):
                del character.db.stats['pools']['Blood']
            # Add Rage
            character.set_stat('pools', 'dual', 'Rage', 1, temp=False)
            character.set_stat('pools', 'dual', 'Rage', 1, temp=True)

        # Set Renown
        renown_types = SHIFTER_RENOWN.get(shifter_type, [])
        for renown_type in renown_types:
            character.set_stat('advantages', 'renown', renown_type, 0, temp=False)

        self.caller.msg(f"|gApplied specific pools and renown for {shifter_type} to {character.name}.|n")
        character.msg(f"|gYour specific pools and renown for {shifter_type} have been applied.|n")

    def apply_splat_pools(self, character, splat):
        """Apply the correct pools based on the character's splat."""
        # Remove all existing pools except Willpower
        character.db.stats['pools'] = {k: v for k, v in character.db.stats.get('pools', {}).items() if k == 'Willpower'}

        # Add Willpower for all characters if it doesn't exist
        if 'Willpower' not in character.db.stats['pools']:
            character.set_stat('pools', 'dual', 'Willpower', 1, temp=False)
            character.set_stat('pools', 'dual', 'Willpower', 1, temp=True)

        if splat.lower() == 'vampire':
            # Add Vampire-specific pools
            character.set_stat('pools', 'dual', 'Blood', 10, temp=False)
            character.set_stat('pools', 'dual', 'Blood', 10, temp=True)
            character.set_stat('pools', 'moral', 'Road', 7, temp=False)
        elif splat.lower() == 'shifter':
            # Add Shifter-specific pools
            character.set_stat('pools', 'dual', 'Gnosis', 1, temp=False)
            character.set_stat('pools', 'dual', 'Gnosis', 1, temp=True)
            character.set_stat('pools', 'dual', 'Rage', 1, temp=False)
            character.set_stat('pools', 'dual', 'Rage', 1, temp=True)

        self.caller.msg(f"|gApplied default pools for {splat} to {character.name}.|n")
        character.msg(f"|gYour default pools for {splat} have been applied.|n")

from evennia.commands.default.muxcommand import MuxCommand
from world.wod20th.models import Stat
from evennia.utils import search

class CmdSpecialty(MuxCommand):
    """
    Usage:
      +stats/specialty <character>/<stat>=<specialty>
      +stats/specialty me/<stat>=<specialty>

    Examples:
      +stats/specialty Bob/Firearms=Sniping
      +stats/specialty me/Firearms=Sniping
    """

    key = "+stats/specialty"
    aliases = ["stat/specialty","specialty", "spec"]
    locks = "cmd:perm(Builder)"  # Only Builders and above can use this command
    help_category = "Chargen & Character Info"

    def parse(self):
        """
        Parse the arguments.
        """
        self.character_name = ""
        self.stat_name = ""
        self.specialty = ""

        try:
            args = self.args.strip()
            first_part, self.specialty = args.split('=', 1)

            if '/' in first_part:
                self.character_name, self.stat_name = first_part.split('/', 1)
            else:
                self.character_name = first_part

            self.character_name = self.character_name.strip()
            self.stat_name = self.stat_name.strip()
            self.specialty = self.specialty.strip()

        except ValueError:
            self.character_name = self.stat_name = self.specialty = None

    def func(self):
        """Implement the command"""

        if not self.character_name or not self.stat_name or not self.specialty:
            self.caller.msg("|rUsage: +stats/specialty <character>/<stat>=<specialty>|n")
            return

        if self.character_name.lower().strip() == 'me':
            character = self.caller
        else:
            character = self.caller.search(self.character_name)

        if not character:
            self.caller.msg(f"|rCharacter '{self.character_name}' not found.|n")
            return

        # Fetch the stat definition from the database
        try:
            matching_stats = Stat.objects.filter(name__icontains=self.stat_name.strip())
        except Exception as e:
            self.caller.msg(f"|rError fetching stats: {e}|n")
            return

        if not matching_stats.exists():
            self.caller.msg(f"|rNo stats matching '{self.stat_name}' found in the database.|n")
            return

        if len(matching_stats) > 1:
            self.caller.msg(f"|rMultiple stats matching '{self.stat_name}' found: {[stat.name for stat in matching_stats]}. Please be more specific.|n")
            return

        stat = matching_stats.first()
        stat_name = stat.name

        specialties = character.db.specialties or {}
        if not specialties.get(stat_name):
            specialties[stat_name] = []
        specialties[stat_name].append(self.specialty)
        character.db.specialties = specialties

        self.caller.msg(f"|gAdded specialty '{self.specialty}' to {character.name}'s {stat_name}.|n")
        character.msg(f"|y{self.caller.name}|n |gadded the specialty|n '|y{self.specialty}|n' |gto your {stat_name}.|n")