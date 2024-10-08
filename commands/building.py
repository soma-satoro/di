from evennia import CmdSet
from evennia.commands.default.building import ObjManipCommand

class CmdSetRoomResources(ObjManipCommand):
    """
    Set the resources value for a room.

    Usage:
      +res [<room>] = <value>

    Sets the 'resources' attribute of a room to the specified integer value.
    If no room is specified, it sets the attribute for the current room.

    Example:
      +res = 4
      +res Temple of Doom = 5
    """

    key = "+res"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: +res [<room>] = <value>")
            return

        if self.rhs is None:
            self.caller.msg("You must specify a value. Usage: +res [<room>] = <value>")
            return

        try:
            value = int(self.rhs)
        except ValueError:
            self.caller.msg("The resources value must be an integer.")
            return

        if self.lhs:
            obj = self.caller.search(self.lhs, global_search=True)
        else:
            obj = self.caller.location

        if not obj:
            return

        if not obj.is_typeclass("typeclasses.rooms.RoomParent"):
            self.caller.msg("You can only set resources on rooms.")
            return

        obj.db.resources = value
        self.caller.msg(f"Set resources to {value} for {obj.get_display_name(self.caller)}.")

class CmdSetRoomType(ObjManipCommand):
    """
    Set the room type for a room.

    Usage:
      +roomtype [<room>] = <type>

    Sets the 'roomtype' attribute of a room to the specified string value.
    If no room is specified, it sets the attribute for the current room.

    Example:
      +roomtype = Beach Town
      +roomtype Evil Lair = Villain Hideout
    """

    key = "+roomtype"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: +roomtype [<room>] = <type>")
            return

        if self.rhs is None:
            self.caller.msg("You must specify a room type. Usage: +roomtype [<room>] = <type>")
            return

        if self.lhs:
            obj = self.caller.search(self.lhs, global_search=True)
        else:
            obj = self.caller.location

        if not obj:
            return

        if not obj.is_typeclass("typeclasses.rooms.RoomParent"):
            self.caller.msg("You can only set room types on rooms.")
            return

        obj.db.roomtype = self.rhs
        self.caller.msg(f"Set room type to '{self.rhs}' for {obj.get_display_name(self.caller)}.")

class BuildingCmdSet(CmdSet):
    def at_cmdset_creation(self):
        self.add(CmdSetRoomResources())
        self.add(CmdSetRoomType())