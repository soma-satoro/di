from evennia.utils.ansi import ANSIString

def format_stat(stat, value, width=25, default=None, tempvalue=None):
    # if there's no value and the default value is greater than 0 then use the default value.
    if default is not None and value is None or value == 0 or value == "":
        value = default

    if not value or value == "" or value == 0 and not tempvalue:
        value = default
    
    if not tempvalue:
        tempvalue = value
    # compare two strings
    if  ANSIString(f"{value}").strip() != ANSIString(f"{tempvalue}").strip():
        value = ANSIString(f"|h{value}|n(|w{tempvalue}|n)")

    # A regex to see if the string starts with a bscktick

    if ANSIString(f"{stat}").startswith("`"):
        return ANSIString(f"|n|y {stat}").ljust(width -  len(ANSIString(value).strip()), ANSIString('|y.|n')) + f"|n|y{value}|n"
    else:
        if value == default and default == 0 or value == default and default == "":
            value = ANSIString(f"|n{value}|n")
            stat = ANSIString(f"|n{stat}|n")
        else :
            value = ANSIString(f"|w{value}|n")
            stat = ANSIString(f"|w{stat}|n")

        return ANSIString(f" |w{stat}").ljust(width -  len(ANSIString(value).strip()), ANSIString('|h|x.|n')) + value


def header(title, width=78,  color="|y", fillchar=ANSIString("|b-|n"), bcolor="|b"):
    return ANSIString.center(ANSIString(f"{bcolor}<|n {color} {title} |n{bcolor}>|n"), width=width, fillchar=ANSIString(fillchar)) + "\n"

def footer(width=78, fillchar=ANSIString("|b-|n")):
    return ANSIString(fillchar) * width + "\n"


def divider(title, width=78, fillchar="-", color="|r", text_color="|n"):
    """
    Create a divider with a title.

    Args:
        title (str): The title to display in the divider.
        width (int): The total width of the divider.
        fillchar (str): The character to use for filling.
        color (str): The color code for the divider line.
        text_color (str): The color code for the title text.

    Returns:
        ANSIString: The formatted divider.
    """
    if isinstance(fillchar, ANSIString):
        fillchar = fillchar[0]
    else:
        fillchar = fillchar[0]

    colored_fillchar = f"{color}{fillchar}"
    
    if title:
        # Calculate the width of the title text without color codes
        title_width = len(ANSIString(title).clean())
        
        # Calculate padding on each side of the title
        padding = (width - title_width - 2) // 2  # -2 for spaces around the title
        
        # Create the divider with title
        left_part = colored_fillchar * padding
        right_part = colored_fillchar * (width - padding - title_width - 2)
        inner_content = f"{left_part} {text_color}{title}|n {right_part}"
    else:
        # If no title, just create a line of fillchars
        inner_content = colored_fillchar * width

    return ANSIString(f"{inner_content}|n")
