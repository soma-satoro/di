from evennia.commands.default.muxcommand import MuxCommand
from world.wod20th.models import SHIFTER_IDENTITY_STATS, SHIFTER_RENOWN, CLAN, MAGE_FACTION, MAGE_SPHERES, TRADITION, TRADITION_SUBFACTION, CONVENTION, METHODOLOGIES, NEPHANDI_FACTION, SEEMING, KITH, SEELIE_LEGACIES, UNSEELIE_LEGACIES, ARTS, REALMS
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
        
        common_stats = ['Full Name', 'Date of Birth', 'Concept']
        splat = character.db.stats.get('other', {}).get('splat', {}).get('Splat', {}).get('perm', '')
        
        if splat.lower() == 'changeling':
            common_stats += ['Seelie Legacy', 'Unseelie Legacy']
        else:
            common_stats += ['Nature', 'Demeanor']

        if splat.lower() == 'vampire':
            splat_specific_stats = ['Clan', 'Date of Embrace', 'Generation', 'Sire']
        elif splat.lower() == 'shifter':
            shifter_type = character.db.stats.get('identity', {}).get('lineage', {}).get('Type', {}).get('perm', '')
            splat_specific_stats = ['Type'] + SHIFTER_IDENTITY_STATS.get(shifter_type, [])
        elif splat.lower() == 'mage':
            mage_faction = character.db.stats.get('identity', {}).get('lineage', {}).get('Mage Faction', {}).get('perm', '')
            splat_specific_stats = ['Essence', 'Mage Faction']
            
            if mage_faction.lower() == 'traditions':
                traditions = character.db.stats.get('identity', {}).get('lineage', {}).get('Traditions', {}).get('perm', '')
                splat_specific_stats.extend(['Traditions'])
                if traditions:
                    splat_specific_stats.append('Traditions Subfaction')
            elif mage_faction.lower() == 'technocracy':
                splat_specific_stats.extend(['Convention', 'Methodology'])
            elif mage_faction.lower() == 'nephandi':
                splat_specific_stats.append('Nephandi Faction')
        elif splat.lower() == 'changeling':
            splat_specific_stats = ['Kith', 'Seeming', 'House']
        else:
            splat_specific_stats = []

        all_stats = common_stats + splat_specific_stats + ['Splat']
        
        def format_stat_with_dots(stat, value, width=37):
            # Special case for 'Traditions Subfaction'
            display_stat = 'Subfaction' if stat == 'Traditions Subfaction' else stat
            
            stat_str = f" {display_stat}"
            value_str = f"{value}"
            dots = "." * (width - len(stat_str) - len(value_str) - 1)
            return f"{stat_str}{dots}{value_str}"

        for i in range(0, len(all_stats), 2):
            left_stat = all_stats[i]
            right_stat = all_stats[i+1] if i+1 < len(all_stats) else None

            left_value = character.db.stats.get('identity', {}).get('personal', {}).get(left_stat, {}).get('perm', '')
            if not left_value:
                left_value = character.db.stats.get('identity', {}).get('lineage', {}).get(left_stat, {}).get('perm', '')
            if not left_value:
                left_value = character.db.stats.get('identity', {}).get('other', {}).get(left_stat, {}).get('perm', '')
            if not left_value and left_stat == 'Splat':
                left_value = character.db.stats.get('other', {}).get('splat', {}).get('Splat', {}).get('perm', '')

            left_formatted = format_stat_with_dots(left_stat, left_value)

            if right_stat:
                right_value = character.db.stats.get('identity', {}).get('personal', {}).get(right_stat, {}).get('perm', '')
                if not right_value:
                    right_value = character.db.stats.get('identity', {}).get('lineage', {}).get(right_stat, {}).get('perm', '')
                if not right_value:
                    right_value = character.db.stats.get('identity', {}).get('other', {}).get(right_stat, {}).get('perm', '')
                if not right_value and right_stat == 'Splat':
                    right_value = character.db.stats.get('other', {}).get('splat', {}).get('Splat', {}).get('perm', '')
                right_formatted = format_stat_with_dots(right_stat, right_value)
                string += f"{left_formatted}  {right_formatted}\n"
            else:
                string += f"{left_formatted}\n"

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

        string += header("Advantages", width=78, color="|y")
        
        powers = []
        advantages = []
        status = []

        # Process powers based on character splat
        if character_splat.lower() == 'vampire':
            powers.append(divider("Disciplines", width=25, color="|b"))
            disciplines = character.db.stats.get('powers', {}).get('discipline', {})
            for discipline, values in disciplines.items():
                discipline_value = values.get('perm', 0)
                powers.append(format_stat(discipline, discipline_value, default=0))

        elif character_splat.lower() == 'mage':
            powers.append(divider("Spheres", width=25, color="|b"))
            spheres = ['Correspondence', 'Entropy', 'Forces', 'Life', 'Matter', 'Mind', 'Prime', 'Spirit', 'Time']
            for sphere in spheres:
                sphere_value = character.db.stats.get('powers', {}).get('sphere', {}).get(sphere, {}).get('perm', 0)
                powers.append(format_stat(sphere, sphere_value, default=0))

        elif character_splat.lower() == 'changeling':
            powers.append(divider("Arts", width=25, color="|b"))
            arts = character.db.stats.get('powers', {}).get('art', {})
            for art, values in arts.items():
                art_value = values.get('perm', 0)
                powers.append(format_stat(art, art_value, default=0))

            powers.append(" " * 25)
            powers.append(divider("Realms", width=25, color="|b"))
            realms = character.db.stats.get('powers', {}).get('realm', {})
            for realm, values in realms.items():
                realm_value = values.get('perm', 0)
                powers.append(format_stat(realm, realm_value, default=0))

        elif character_splat.lower() == 'shifter':
            powers.append(divider("Gifts", width=25, color="|b"))
            gifts = character.db.stats.get('powers', {}).get('gift', {})
            for gift, values in gifts.items():
                gift_value = values.get('perm', 0)
                powers.append(format_stat(gift, gift_value, default=0))

        # Process backgrounds, merits, flaws, and other advantages
        advantages.append(divider("Backgrounds", width=25, color="|b"))
        backgrounds = character.db.stats.get('backgrounds', {}).get('background', {})
        for background, values in backgrounds.items():
            background_value = values.get('perm', 0)
            advantages.append(format_stat(background, background_value, default=0))

        advantages.append(" " * 25)
        advantages.append(divider("Merits & Flaws", width=25, color="|b"))
        for category, merits_dict in character.db.stats.get('merits', {}).items():
            for merit, values in merits_dict.items():
                advantages.append(format_stat(merit, values['perm']))

        for category, flaws_dict in character.db.stats.get('flaws', {}).items():
            for flaw, values in flaws_dict.items():
                advantages.append(format_stat(flaw, values['perm']))

        # Process pools
        advantages.append(" " * 25)
        advantages.append(divider("Pools", width=25, color="|b"))
        valid_pools = []
        if character_splat.lower() == 'vampire':
            valid_pools.extend(['Blood', 'Road'])
        elif character_splat.lower() == 'shifter':
            valid_pools.extend(['Rage', 'Gnosis'])
        elif character_splat.lower() == 'mage':
            advantages.append(" " * 25)
            advantages.append(divider("Pools", width=25, color="|b"))
            
            # Willpower
            willpower_perm = character.db.stats.get('pools', {}).get('dual', {}).get('Willpower', {}).get('perm', 0)
            willpower_temp = character.db.stats.get('pools', {}).get('dual', {}).get('Willpower', {}).get('temp', willpower_perm)
            advantages.append(format_stat("Willpower", willpower_perm, tempvalue=willpower_temp))
            
            # Arete (no temporary value)
            arete_value = character.db.stats.get('other', {}).get('advantage', {}).get('Arete', {}).get('perm', 0)
            advantages.append(format_stat("Arete", arete_value))
            
            # Quintessence
            quintessence_perm = character.db.stats.get('pools', {}).get('dual', {}).get('Quintessence', {}).get('perm', 0)
            quintessence_temp = character.db.stats.get('pools', {}).get('dual', {}).get('Quintessence', {}).get('temp', quintessence_perm)
            advantages.append(format_stat("Quintessence", quintessence_perm, tempvalue=quintessence_temp))
            
            # Paradox (only temporary value)
            paradox_temp = character.db.stats.get('pools', {}).get('dual', {}).get('Paradox', {}).get('temp', 0)
            advantages.append(format_stat("Paradox", paradox_temp, tempvalue=paradox_temp))
        elif character_splat.lower() == 'changeling':
            valid_pools.extend(['Glamour', 'Banality'])

        for pool_name in valid_pools:
            if pool_name == 'Arete':
                pool_value = character.db.stats.get('other', {}).get('advantage', {}).get('Arete', {}).get('perm', 0)
                temp_value = character.db.stats.get('other', {}).get('advantage', {}).get('Arete', {}).get('temp', pool_value)
            else:
                pool_value = character.db.stats.get('pools', {}).get('dual', {}).get(pool_name, {}).get('perm', 0)
                temp_value = character.db.stats.get('pools', {}).get('dual', {}).get(pool_name, {}).get('temp', pool_value)
            
            advantages.append(format_stat(f"{pool_name}", pool_value, tempvalue=temp_value))

        # Add Renown for Shifters
        if character_splat.lower() == "shifter":
            advantages.append(" " * 25)
            advantages.append(divider("Renown", width=25, color="|b"))
            shifter_type = character.get_stat('identity', 'lineage', 'Type', 'perm')
            renown_types = SHIFTER_RENOWN.get(shifter_type, [])
            for renown_type in renown_types:
                renown_value = character.get_stat('advantages', 'renown', renown_type, 'perm') or 0
                advantages.append(format_stat(renown_type, renown_value, default=0))

        # Process health
        status.append(divider("Health & Status", width=25, color="|b"))
        status.extend(format_damage_stacked(character))

        # Combine powers, advantages, and status
        max_len = max(len(powers), len(advantages), len(status))
        while len(powers) < max_len:
            powers.append(" " * 25)
        while len(advantages) < max_len:
            advantages.append(" " * 25)
        while len(status) < max_len:
            status.append(" " * 25)

        for power, advantage, status_line in zip(powers, advantages, status):
            string += f"{power} {advantage} {status_line}\n"

        if not character.db.approved:
            string += footer()
            string += header("Unapproved Character", width=78, color="|y")
        string += footer()

        self.caller.msg(string)