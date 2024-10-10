from evennia.commands.default.muxcommand import MuxCommand
from world.wod20th.models import SHIFTER_IDENTITY_STATS, SHIFTER_RENOWN
from world.wod20th.models import Stat
from evennia.utils.ansi import ANSIString
from world.wod20th.utils.damage import format_damage, format_status, format_damage_stacked
from world.wod20th.utils.formatting import format_stat, header, footer, divider
from itertools import zip_longest

class CmdSheet(MuxCommand):
    """
    Show a sheet of the character.
    """
    key = "sheet"
    aliases = ["sh"]
    help_category = "Chargen & Character Info"

    def func(self):
        name = self.args.strip()
        if not name:
            name = self.caller.key
        character = self.caller.search(name)
        
        try:
            splat = character.get_stat('other', 'splat', 'Splat')
        except AttributeError:
            self.caller.msg(f"|rCharacter '{name}' not found.|n")
            return
        self.caller.msg(f"|rSplat: {splat}|n")
        if not splat:
            splat = "Mortal"
        if not self.caller.check_permstring("builders"):
            if self.caller != character:
                self.caller.msg(f"|rYou can't see the sheet of {character.key}.|n")
                return

        if not character:
            self.caller.msg(f"|rCharacter '{name}' not found.|n")
            return

        if self.caller != character:
            if not character.access(self.caller, 'edit'):
                self.caller.msg(f"|rYou can't see the sheet of {character.key}.|n")
                return

        stats = character.db.stats
        if not stats:
            character.db.stats = {}
        
        string = header(f"Character Sheet for:|n {character.get_display_name(self.caller)}")
        
        string += header("Identity", width=78, color="|y")
        
        splat = character.get_stat('other', 'splat', 'Splat') or ''
        
        # Common stats for all characters
        common_stats = ['Full Name', 'Age', 'Concept', 'Nature', 'Demeanor']
        
        if splat.lower() == 'vampire':
            valid_identity_stats = common_stats + ['Clan', 'Generation', 'Sire', 'Splat']
        elif splat.lower() == 'shifter':
            shifter_type = character.get_stat('identity', 'lineage', 'Type')
            valid_identity_stats = common_stats + ['Type'] + SHIFTER_IDENTITY_STATS.get(shifter_type, []) + ['Splat']
        else:  # For other splats or unspecified
            valid_identity_stats = common_stats + ['Splat']

        bio = []
        for stat_name in valid_identity_stats:
            if stat_name == 'Splat':
                value = splat
            else:
                value = character.get_stat('identity', 'lineage', stat_name) or ''
            bio.append(format_stat(stat_name, value, default="", width=38))

        # Split the bio list into two columns
        bio1 = bio[:len(bio)//2]
        bio2 = bio[len(bio)//2:]

        # Combine the two columns
        for b1, b2 in zip_longest(bio1, bio2, fillvalue=" " * 38):
            string += f"{b1}  {b2}\n"

        string += header("Attributes", width=78, color="|y")
        string += " " + divider("Physical", width=25, fillchar=" ") + " "
        string += divider("Social", width=25, fillchar=" ") + " "
        string += divider("Mental", width=25, fillchar=" ") + "\n"

        string += format_stat("Strength", character.get_stat('attributes', 'physical', 'Strength'), default=1, tempvalue=character.get_stat('attributes', 'physical', 'Strength', temp=True)) + " "
        string += format_stat("Charisma", character.get_stat('attributes', 'social', 'Charisma'), default=1, tempvalue=character.get_stat('attributes', 'social', 'Charisma', temp=True)) + " "
        string += format_stat("Perception", character.get_stat('attributes', 'mental', 'Perception'), default=1, tempvalue=character.get_stat('attributes', 'mental', 'Perception', temp=True)) + "\n"
        string += format_stat("Dexterity", character.get_stat('attributes', 'physical', 'Dexterity'), default=1, tempvalue=character.get_stat('attributes', 'physical', 'Dexterity', temp=True)) + " "
        string += format_stat("Manipulation", character.get_stat('attributes', 'social', 'Manipulation'), default=1, tempvalue=character.get_stat('attributes', 'social', 'Manipulation', temp=True)) + " "
        string += format_stat("Intelligence", character.get_stat('attributes', 'mental', 'Intelligence'), default=1, tempvalue=character.get_stat('attributes', 'mental', 'Intelligence', temp=True)) + "\n"
        string += format_stat("Stamina", character.get_stat('attributes', 'physical', 'Stamina'), default=1, tempvalue=character.get_stat('attributes', 'physical', 'Stamina', temp=True)) + " "
        string += format_stat("Appearance", character.get_stat('attributes', 'social', 'Appearance'), default=1, tempvalue=character.get_stat('attributes', 'social', 'Appearance', temp=True)) + " "
        string += format_stat("Wits", character.get_stat('attributes', 'mental', 'Wits'), default=1, tempvalue=character.get_stat('attributes', 'mental', 'Wits', temp=True)) + "\n"

        talents = Stat.objects.filter(category='abilities', stat_type='talent')
        talents = [talent for talent in talents if not talent.lock_string or character.check_permstring(talent.lock_string)]
        
        skills = Stat.objects.filter(category='abilities', stat_type='skill')
        skills = [skill for skill in skills if not skill.lock_string or character.check_permstring(skill.lock_string)]
        knowledges = Stat.objects.filter(category='abilities', stat_type='knowledge')
        knowledges = [knowledge for knowledge in knowledges if not knowledge.lock_string or character.check_permstring(knowledge.lock_string)]

        string += header("Abilities", width=78, color="|y")
        string += " " + divider("Talents", width=25, fillchar=" ") + " "
        string += divider("Skills", width=25, fillchar=" ") + " "
        string += divider("Knowledges", width=25, fillchar=" ") + "\n"

        formatted_talents = []
        for talent in talents:
            formatted_talents.append(format_stat(talent.name, character.get_stat(talent.category, talent.stat_type, talent.name), default=0, tempvalue=character.get_stat(talent.category, talent.stat_type, talent.name, temp=True)))
            # if there are any specialties add them too
            if character.db.specialties and talent.name in character.db.specialties:
                for specialty in character.db.specialties[talent.name]:
                    formatted_talents.append(format_stat(f"`{specialty}", 1))

        formatted_skills = []
        for skill in skills:
            formatted_skills.append(format_stat(skill.name, character.get_stat(skill.category, skill.stat_type, skill.name), default=0, tempvalue=character.get_stat(skill.category, skill.stat_type, skill.name, temp=True)))
            # if there are any specialties add them too
            if character.db.specialties and skill.name in character.db.specialties:
                for specialty in character.db.specialties[skill.name]:
                    formatted_skills.append(format_stat(f"`{specialty}", 1))

        formatted_knowledges = []
        for knowledge in knowledges:
            formatted_knowledges.append(format_stat(knowledge.name, character.get_stat(knowledge.category, knowledge.stat_type, knowledge.name), default=0, tempvalue=character.get_stat(knowledge.category, knowledge.stat_type, knowledge.name, temp=True)))
            # if there are any specialties add them too
            if character.db.specialties and knowledge.name in character.db.specialties:
                for specialty in character.db.specialties[knowledge.name]:
                    formatted_knowledges.append(format_stat(f"`{specialty}", 1))

        max_len = max(len(formatted_talents), len(formatted_skills), len(formatted_knowledges))
        while len(formatted_talents) < max_len:
            formatted_talents.append(" " * 25)
        while len(formatted_skills) < max_len:
            formatted_skills.append(" " * 25)
        while len(formatted_knowledges) < max_len:
            formatted_knowledges.append(" " * 25)

        for talent, skill, knowledge in zip(formatted_talents, formatted_skills, formatted_knowledges):
            string += f"{talent} {skill} {knowledge}\n"

        if character.db.splat == "Vampire":
            if not character.db.stats.get('backgrounds'):
                backgrounds = []
            else:
                backgrounds = [format_stat(background, character.get_stat('backgrounds', 'background', background), default=0, tempvalue=character.get_stat('backgrounds', 'background', background, temp=True)) for background in character.db.stats.get('backgrounds', {}).get('background', {}).keys()]

            if not character.db.stats.get('powers'):
                disciplines = []
            else:
                disciplines = [format_stat(discipline, character.get_stat('powers', 'discipline', discipline), default=0, tempvalue=character.get_stat('powers', 'discipline', discipline, temp=True)) for discipline in character.db.stats.get('powers', {}).get('discipline', {}).keys()]

            virtues = Stat.objects.filter(category='virtues')
            virtues = [format_stat(virtue.name, character.get_stat(virtue.category, virtue.stat_type, virtue.name)) for virtue in virtues if character.get_stat(virtue.category, virtue.stat_type, virtue.name)]

            string += header("Advantages", width=78, color="|y")
            string += divider("Disciplines", width=25, fillchar=" ") + " "
            string += divider("Backgrounds", width=25, fillchar=" ") + " "
            string += divider("Virtues", width=25, fillchar=" ") + "\n"

            max_len = max(len(disciplines), len(backgrounds), len(virtues))
            while len(disciplines) < max_len:
                disciplines.append(" " * 25)
            while len(backgrounds) < max_len:
                backgrounds.append(" " * 25)
            while len(virtues) < max_len:
                virtues.append(" " * 25)

            for discipline, background, virtue in zip(disciplines, backgrounds, virtues):
                string += f"{discipline} {background} {virtue}\n"

        elif character.db.splat == "Shifter":
            shifter_type = character.get_stat('identity', 'lineage', 'Type')
            
            backgrounds = [format_stat(background, character.get_stat('backgrounds', 'background', background), default=0, tempvalue=character.get_stat('backgrounds', 'background', background, temp=True)) for background in character.db.stats.get('backgrounds', {}).get('background', {}).keys()]
            
            gifts = [format_stat(gift, character.get_stat('powers', 'gift', gift), default=0, tempvalue=character.get_stat('powers', 'gift', gift, temp=True)) for gift in character.db.stats.get('powers', {}).get('gift', {}).keys()]
            
            renown_types = SHIFTER_RENOWN.get(shifter_type, [])
            renown = [format_stat(renown_type, character.get_stat('advantages', 'renown', renown_type), default=0, tempvalue=character.get_stat('advantages', 'renown', renown_type, temp=True)) for renown_type in renown_types]

            string += header("Advantages", width=78, color="|y")
            string += divider("Gifts", width=25, fillchar=" ") + " "
            string += divider("Backgrounds", width=25, fillchar=" ") + " "
            string += divider("Renown", width=25, fillchar=" ") + "\n"

            max_len = max(len(gifts), len(backgrounds), len(renown))
            while len(gifts) < max_len:
                gifts.append(" " * 25)
            while len(backgrounds) < max_len:
                backgrounds.append(" " * 25)
            while len(renown) < max_len:
                renown.append(" " * 25)

            for gift, background, renown_stat in zip(gifts, backgrounds, renown):
                string += f"{gift} {background} {renown_stat}\n"

        # Get the splat from the stats
        character_splat = character.get_stat('other', 'splat', 'Splat') or "Unknown"
        print(f"Character splat: {character_splat}")
        print(f"Character stats: {character.db.stats}")

        string += header("Other", width=78, color="|y")
        string += divider("Merits", width=25, fillchar=" ", color="|b") + " "
        string += divider("Pools", width=25, fillchar=" ", color="|b") + " " 
        string += divider("Health & Status", width=25, fillchar=" ", color="|b") + "\n"

        merits = []
        for category, merits_dict in character.db.stats.get('merits', {}).items():
            for merit, values in merits_dict.items():
                merits.append(format_stat(merit, values['perm']))

        flaws = []
        for category, flaws_dict in character.db.stats.get('flaws', {}).items():
            for flaw, values in flaws_dict.items():
                flaws.append(format_stat(flaw, values['perm']))
        
        if flaws:
            merits.append(" " * 25)
            merits.append(divider("Flaws", width=25))
            merits.extend(flaws)

        health = format_damage_stacked(character)

        print("About to process pools")
        # Show appropriate pools
        pools = []
        valid_pools = ['Willpower']
        if character_splat.lower() == 'vampire':
            valid_pools.extend(['Blood', 'Road'])
        elif character_splat.lower() == 'shifter':
            valid_pools.extend(['Rage', 'Gnosis'])

        print(f"Valid pools: {valid_pools}")

        for pool_name in valid_pools:
            pool_value = character.get_stat('pools', 'dual', pool_name) or 0
            pools.append(format_stat(pool_name, pool_value, 
                         tempvalue=character.get_stat('pools', 'dual', pool_name, temp=True)))

        print(f"Pools after processing: {pools}")

        # Add Renown for Shifters
        if character_splat.lower() == "shifter":
            print("Processing Shifter Renown")
            shifter_type = character.get_stat('identity', 'lineage', 'Type')
            print(f"Shifter Type: {shifter_type}")
            renown_types = SHIFTER_RENOWN.get(shifter_type, [])
            print(f"Renown Types: {renown_types}")
            if renown_types:
                pools.append(" " * 25)
                pools.append(divider("Renown", width=25, color="|b"))  # Change color to blue here
                for renown_type in renown_types:
                    renown_value = character.get_stat('advantages', 'renown', renown_type) or 0
                    print(f"Renown {renown_type}: {renown_value}")
                    pools.append(format_stat(renown_type, renown_value, default=0))  # Add default=0 here

        print(f"Final pools: {pools}")

        max_len = max(len(merits), len(pools), len(health))
        while len(merits) < max_len:
            merits.append(" " * 25)
        while len(pools) < max_len:
            pools.append(" " * 25)
        while len(health) < max_len:
            health.append(" " * 25)

        for merit, pool, health in zip(merits, pools, health):
            string += f"{merit} {pool} {health}\n"

        if not character.db.approved:
            string += footer()
            string += header("Unapproved Character", width=78, color="|y")
        string += footer()

        self.caller.msg(string)