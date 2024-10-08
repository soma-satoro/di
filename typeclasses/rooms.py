from evennia import DefaultRoom
from evennia.utils.ansi import ANSIString
from world.wod20th.utils.ansi_utils import wrap_ansi
from world.wod20th.utils.formatting import header, footer, divider

class RoomParent(DefaultRoom):

    def get_display_name(self, looker, **kwargs):
        """
        Get the name to display for the character.
        """
        
        name = self.key
        
        if self.db.gradient_name:
            name = ANSIString(self.db.gradient_name)
            if looker.check_permstring("builders"):
                name += f"({self.dbref})"
            return name
        
        # If the looker is builder+ show the dbref
        if looker.check_permstring("builders"):
            name += f"({self.dbref})"

        return name

    def return_appearance(self, looker, **kwargs):
        if not looker:
            return ""

        name = self.get_display_name(looker, **kwargs)
        desc = self.db.desc

        # Header with room name
        
        string = header(name, width=78, bcolor="|r", fillchar=ANSIString("|r-|n")) + "\n"
        
        # Process room description
        if desc:
            paragraphs = desc.split('%r')
            formatted_paragraphs = []
            for i, p in enumerate(paragraphs):
                if not p.strip():
                    if i > 0 and not paragraphs[i-1].strip():
                        formatted_paragraphs.append('')  # Add blank line for double %r
                    continue
                
                lines = p.split('%t')
                formatted_lines = []
                for j, line in enumerate(lines):
                    if j == 0 and line.strip():
                        formatted_lines.append(wrap_ansi(line.strip(), width=76))
                    elif line.strip():
                        formatted_lines.append(wrap_ansi('    ' + line.strip(), width=76))
                
                formatted_paragraphs.append('\n'.join(formatted_lines))
            
            string += '\n'.join(formatted_paragraphs) + "\n\n"

        # List all characters in the room
        characters = [obj for obj in self.contents if obj.has_account]
        if characters:
            string += divider("Characters", width=78, fillchar=ANSIString("|r-|n")) + "\n"
            for character in characters:
                idle_time = self.idle_time_display(character.idle_time)
                if character == looker:
                    idle_time = self.idle_time_display(0)

                shortdesc = character.db.shortdesc
                if shortdesc:
                    shortdesc_str = f"{shortdesc}"
                else:
                    shortdesc_str ="|h|xType '|n+shortdesc <desc>|h|x' to set a short description.|n"

                if len(ANSIString(shortdesc_str).strip()) > 43:
                    shortdesc_str = ANSIString(shortdesc_str)[:43]
                    shortdesc_str = ANSIString(shortdesc_str[:-3] + "...|n")
                else:
                    shortdesc_str = ANSIString(shortdesc_str).ljust(43, ' ')
                
                string += ANSIString(f" {character.get_display_name(looker).ljust(25)} {ANSIString(idle_time).rjust(7)}|n {shortdesc_str}\n")

        # List all objects in the room
        objects = [obj for obj in self.contents if not obj.has_account and not obj.destination]
        if objects:
            string += divider("Objects", width=78, fillchar=ANSIString("|r-|n")) + "\n"
            
            # get shordesc or dhoe s blsnk string
            for obj in objects:
                if obj.db.shortdesc:
                    shortdesc = obj.db.shortdesc
                else:
                    shortdesc = ""


            # if looker builder+ show dbref.

                string +=" "+  ANSIString(f"{obj.get_display_name(looker)}").ljust(25) + ANSIString(f"{shortdesc}") .ljust(53, ' ') + "\n"

        # List all exits
        exits = [ex for ex in self.contents if ex.destination]
        if exits:
            direction_strings = []
            exit_strings = []
            for exit in exits:
                aliases = exit.aliases.all() or []
                exit_name = exit.get_display_name(looker)
                short = min(aliases, key=len) if aliases else ""
                
                exit_string = ANSIString(f" <|y{short.upper()}|n> {exit_name}")
                
                if any(word in exit_name for word in ['Sector', 'District', 'Neighborhood']):
                    direction_strings.append(exit_string)
                else:
                    exit_strings.append(exit_string)

            # Display Directions
            if direction_strings:
                string += divider("Directions", width=78, fillchar=ANSIString("|r-|n")) + "\n"
                string += self.format_exit_columns(direction_strings)

            # Display Exits
            if exit_strings:
                string += divider("Exits", width=78, fillchar=ANSIString("|r-|n")) + "\n"
                string += self.format_exit_columns(exit_strings)

        # Get room type and resources
        room_type = self.db.roomtype or "Unknown"
        resources = self.db.resources
        resources_str = f"Res:{resources}" if resources is not None else ""

        # Create the footer with room type and resources
        footer_text = f"{resources_str}, {room_type}".strip(", ")
        footer_length = len(ANSIString(footer_text))
        padding = 78 - footer_length - 2  # -2 for the brackets

        string += ANSIString(f"|r{'-' * padding}[|y{footer_text}|r]|n")

        return string

    def format_exit_columns(self, exit_strings):
        # Split into two columns
        half = (len(exit_strings) + 1) // 2
        col1 = exit_strings[:half]
        col2 = exit_strings[half:]

        # Create two-column format
        formatted_string = ""
        for i in range(max(len(col1), len(col2))):
            col1_str = col1[i] if i < len(col1) else ANSIString("")
            col2_str = col2[i] if i < len(col2) else ANSIString("")
            formatted_string += f"{col1_str.ljust(38)} {col2_str}\n"
        
        return formatted_string

    def idle_time_display(self, idle_time):
        """
        Formats the idle time display.
        """
        idle_time = int(idle_time)  # Convert to int
        if idle_time < 60:
            time_str = f"{idle_time}s"
        elif idle_time < 3600:
            time_str = f"{idle_time // 60}m"
        else:
            time_str = f"{idle_time // 3600}h"

        # Color code based on idle time intervals
        if idle_time < 900:  # less than 15 minutes
            color = "|g"  # green
        elif idle_time < 1800:  # 15-30 minutes
            color = "|y"  # yellow
        elif idle_time < 2700:  # 30-45 minutes
            color = "|o"  # orange
        elif idle_time < 3600:
            color = "|r"  # red
        else:
            color = "|h|x"
        

        return f"{color}{time_str}|n"
