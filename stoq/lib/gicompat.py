import sys

import gi


def install_enum(mod, enum):
    modname = mod.__name__.rsplit('.', 1)[1].upper()
    for value, enum in enum.__enum_values__.items():
        name = enum.value_name
        name = name.replace(modname + '_', '')
        setattr(mod, name, enum)


def install_flags(mod, flags):
    modname = mod.__name__.rsplit('.', 1)[1].upper()
    for value, flag in flags.__flags_values__.items():
        for name in flag.value_names:
            name = name.replace(modname + '_', '')
            setattr(mod, name, flag)


def enable():
    # gobject
    from gi.repository import GObject
    sys.modules['gobject'] = GObject
    from gi._gobject import propertyhelper
    sys.modules['gobject.propertyhelper'] = propertyhelper

    # gio
    from gi.repository import Gio
    sys.modules['gio'] = Gio

_unset = object()


def enable_gtk():
    # set the default encoding like PyGTK
    reload(sys)
    sys.setdefaultencoding('utf-8')

    # atk
    gi.require_version('Atk', '1.0')
    from gi.repository import Atk
    sys.modules['atk'] = Atk

    # pango
    gi.require_version('Pango', '1.0')
    from gi.repository import Pango
    sys.modules['pango'] = Pango
    for enum_type in [Pango.EllipsizeMode]:
        install_enum(Pango, enum_type)

    # pangocairo
    gi.require_version('PangoCairo', '1.0')
    from gi.repository import PangoCairo
    sys.modules['pangocairo'] = PangoCairo

    # gdk
    gi.require_version('Gdk', '2.0')
    gi.require_version('GdkPixbuf', '2.0')
    from gi.repository import Gdk
    from gi.repository import GdkPixbuf
    sys.modules['gtk.gdk'] = Gdk
    for enum_type in [Gdk.CursorType,
                      Gdk.WindowTypeHint,
                      GdkPixbuf.InterpType]:
        install_enum(Gdk, enum_type)
    for flags_type in [Gdk.EventMask,
                       Gdk.WindowState,
                       Gdk.ModifierType]:
        install_flags(Gdk, flags_type)
    Gdk.BUTTON_PRESS = 4

    Gdk.Pixbuf = GdkPixbuf.Pixbuf
    Gdk.pixbuf_new_from_file = GdkPixbuf.Pixbuf.new_from_file
    Gdk.PixbufLoader = GdkPixbuf.PixbufLoader.new_with_type

    orig_get_frame_extents = Gdk.Window.get_frame_extents

    def get_frame_extents(window):
        rect = Gdk.Rectangle(0, 0, 0, 0)
        orig_get_frame_extents(window, rect)
        return rect
    Gdk.Window.get_frame_extents = get_frame_extents

    # gtk
    gi.require_version('Gtk', '2.0')
    from gi.repository import Gtk
    sys.modules['gtk'] = Gtk
    Gtk.gdk = Gdk

    Gtk.pygtk_version = (2, 99, 0)

    Gtk.gtk_version = (2, 22, 0)
    for enum_type in [Gtk.ArrowType,
                      Gtk.ButtonsType,
                      Gtk.EntryIconPosition,
                      Gtk.Justification,
                      Gtk.IconSize,
                      Gtk.MessageType,
                      Gtk.Orientation,
                      Gtk.PackType,
                      Gtk.PolicyType,
                      Gtk.PositionType,
                      Gtk.ResponseType,
                      Gtk.ReliefStyle,
                      Gtk.SelectionMode,
                      Gtk.ShadowType,
                      Gtk.SizeGroupMode,
                      Gtk.SortType,
                      Gtk.StateType,
                      Gtk.TextDirection,
                      Gtk.ToolbarStyle,
                      Gtk.TreeViewColumnSizing,
                      Gtk.WindowPosition,
                      Gtk.WindowType]:
        install_enum(Gtk, enum_type)
    for flags_type in [Gtk.DialogFlags]:
        install_flags(Gtk, flags_type)

    # Action

    def set_tool_item_type(menuaction, gtype):
        print 'set_tool_item_type is not supported'
    Gtk.Action.set_tool_item_type = classmethod(set_tool_item_type)

    # Alignment

    orig_Alignment = Gtk.Alignment

    class Alignment(orig_Alignment):
        def __init__(self, xalign=0.0, yalign=0.0, xscale=0.0, yscale=0.0):
            orig_Alignment.__init__(self)
            self.props.xalign = xalign
            self.props.yalign = yalign
            self.props.xscale = xscale
            self.props.yscale = yscale

    Gtk.Alignment = Alignment

    # Box

    orig_pack_end = Gtk.Box.pack_end

    def pack_end(self, child, expand=True, fill=True, padding=0):
        orig_pack_end(self, child, expand, fill, padding)
    Gtk.Box.pack_end = pack_end

    orig_pack_start = Gtk.Box.pack_start

    def pack_start(self, child, expand=True, fill=True, padding=0):
        orig_pack_start(self, child, expand, fill, padding)
    Gtk.Box.pack_start = pack_start

    # CellLayout

    orig_cell_pack_end = Gtk.CellLayout.pack_end

    def cell_pack_end(self, cell, expand=True):
        orig_cell_pack_end(self, cell, expand)
    Gtk.CellLayout.pack_end = cell_pack_end

    orig_cell_pack_start = Gtk.CellLayout.pack_start

    def cell_pack_start(self, cell, expand=True):
        orig_cell_pack_start(self, cell, expand)
    Gtk.CellLayout.pack_start = cell_pack_start

    orig_cell_data_func = Gtk.CellLayout.set_cell_data_func

    def cell_data_func(self, func, user_data=_unset):
        def callback(*args):
            if args[-1] == _unset:
                args = args[:-1]
            return func(*args)
        orig_cell_data_func(self, callback, user_data)
    Gtk.CellLayout.set_cell_data_func = cell_data_func

    # CellRenderer

    class GenericCellRenderer(Gtk.CellRenderer):
        pass
    Gtk.GenericCellRenderer = GenericCellRenderer

    # ComboBox

    orig_combo_row_separator_func = Gtk.ComboBox.set_row_separator_func

    def combo_row_separator_func(self, func, user_data=_unset):
        def callback(*args):
            if args[-1] == _unset:
                args = args[:-1]
            return func(*args)
        orig_combo_row_separator_func(self, callback, user_data)
    Gtk.ComboBox.set_row_separator_func = combo_row_separator_func

    # Container

    def install_child_property(container, flag, pspec):
        print 'install_child_property is not supported'
    Gtk.Container.install_child_property = classmethod(install_child_property)

    Gtk.expander_new_with_mnemonic = Gtk.Expander.new_with_mnemonic
    Gtk.icon_theme_get_default = Gtk.IconTheme.get_default
    Gtk.image_new_from_stock = Gtk.Image.new_from_stock
    Gtk.settings_get_default = Gtk.Settings.get_default
    Gtk.widget_get_default_direction = Gtk.Widget.get_default_direction
    Gtk.window_set_default_icon = Gtk.Window.set_default_icon

    # gtk.unixprint
    class UnixPrint(object):
        pass
    unixprint = UnixPrint()
    sys.modules['gtkunixprint'] = unixprint

    # gtk.keysyms
    class Keysyms(object):
        pass
    keysyms = Keysyms()
    sys.modules['gtk.keysyms'] = keysyms
    Gtk.keysyms = keysyms
    for name in dir(Gdk):
        if name.startswith('KEY_'):
            target = name[4:]
            if target[0] in '0123456789':
                target = '_' + target
            value = getattr(Gdk, name)
            setattr(keysyms, target, value)


def enable_vte():
    # vte
    gi.require_version('Vte', '0.0')
    from gi.repository import Vte
    sys.modules['vte'] = Vte


def enable_poppler():
    # poppler
    gi.require_version('Poppler', '0.18')
    from gi.repository import Poppler
    sys.modules['poppler'] = Poppler


def enable_webkit():
    # poppler
    gi.require_version('WebKit', '1.0')
    from gi.repository import WebKit
    sys.modules['webkit'] = WebKit