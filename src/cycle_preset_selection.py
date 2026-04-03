import gi

gi.require_version("Adw", "1")
gi.require_version("Gio", "2.0")
gi.require_version("Gtk", "4.0")

from gi.repository import Adw, Gio, Gtk

from .preferences import settings


@Gtk.Template(resource_path="/io/github/diegopvlk/Tomatillo/cycle_preset_selection.ui")
class CyclePresetSelection(Adw.Dialog):
    __gtype_name__ = "CyclePresetSelection"

    presets_list = Gtk.Template.Child()

    def __init__(self, active_window, **kwargs):
        super().__init__(**kwargs)
        self.window = active_window
        self._populate_list()

    def _populate_list(self):
        preset_names = settings.get_value("cycle-presets").unpack().keys()
        for name in preset_names:
            preset_item = Adw.ActionRow(title=name)
            preset_item.set_activatable(True)
            self.presets_list.append(preset_item)

    @Gtk.Template.Callback()
    def _on_item_clicked(self, list, item):
        preset_name = item.get_title()
        settings.set_string("chosen-cycle-preset", preset_name)
        # after a new preset selection reset the current session
        self.window.set_start()
        # preset_name = self.window.current_preset_name
        # if preset_name != "" and preset_name is not None:
        #     self.window.timer_name.set_label(preset_name)
