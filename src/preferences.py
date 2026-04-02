# preferences.py
#
# Copyright 2025 Diego Povliuk
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import gi

gi.require_version("Adw", "1")
gi.require_version("Gio", "2.0")
gi.require_version("Gtk", "4.0")
gi.require_version("GLib", "2.0")

from gi.repository import Adw, Gio, Gtk, GLib

settings = Gio.Settings.new("io.github.diegopvlk.Tomatillo")


@Gtk.Template(resource_path="/io/github/diegopvlk/Tomatillo/preferences.ui")
class Preferences(Adw.Dialog):
    __gtype_name__ = "Preferences"

    focus_time = Gtk.Template.Child()
    short_b_time = Gtk.Template.Child()
    long_b_time = Gtk.Template.Child()
    long_b_interval = Gtk.Template.Child()
    switch_background = Gtk.Template.Child()
    switch_sound = Gtk.Template.Child()
    switch_dnd = Gtk.Template.Child()
    switch_auto_focus = Gtk.Template.Child()
    switch_auto_break = Gtk.Template.Child()

    def __init__(self, active_window, **kwargs):
        super().__init__(**kwargs)
        self.window = active_window

    @Gtk.Template.Callback()
    def _set_spin_start_val_from_key(self, _dialog, key, spin_row):
        spin_row.sett_key = key
        return settings.get_int(key)

    @Gtk.Template.Callback()
    def _set_spin_value_and_key(self, spin_row, _pspec):
        key = spin_row.sett_key
        value = int(spin_row.get_value())
        minutes = value * 60

        if key == "focus-time":
            self.window.time_focus = minutes
        elif key == "short-b-time":
            self.window.time_short_break = minutes
        elif key == "long-b-time":
            self.window.time_long_break = minutes
        elif key == "long-b-interval":
            self.window.long_b_interval = value

        settings.set_int(key, value)
        self._update_ui()

    @Gtk.Template.Callback()
    def _set_switch_start_state_from_key(self, _dialog, key, switch_row):
        switch_row.sett_key = key
        return settings.get_boolean(key)

    @Gtk.Template.Callback()
    def _set_switch_settings_key(self, switch_row, _pspec):
        settings.set_boolean(switch_row.sett_key, switch_row.get_active())

    @Gtk.Template.Callback()
    def _set_run_in_bg(self, switch_row, _pspec):
        key = switch_row.sett_key
        state = switch_row.get_active()
        settings.set_boolean(key, state)
        self.window.set_hide_on_close(state)

    def _update_ui(self):
        self.window.on_reset_timer_activated()
        self.window.update_ui_timer()
        self.window.update_cycles_label_bg()


# TODO: Add delete button
@Gtk.Template(resource_path="/io/github/diegopvlk/Tomatillo/cycle_preset.ui")
class CyclePreset(Adw.Dialog):
    __gtype_name__ = "CyclePreset"

    preset_name = Gtk.Template.Child()
    focus_time = Gtk.Template.Child()
    short_b_time = Gtk.Template.Child()
    long_b_time = Gtk.Template.Child()
    long_b_interval = Gtk.Template.Child()

    def __init__(self, preset_name, active_window, **kwargs):
        self.window = active_window
        self._preset_name = preset_name

        defaults = {
            "focus-time": settings.get_int("focus-time"),
            "short-b-time": settings.get_int("short-b-time"),
            "long-b-time": settings.get_int("long-b-time"),
            "long-b-interval": settings.get_int("long-b-interval"),
        }
        self._presets = settings.get_value("cycle-presets").unpack()
        
        if self._preset_name is None:
            self._current_preset = defaults
        else:
            existing_params = self._presets.get(self._preset_name, {})
            self._current_preset = {**defaults, **existing_params}

        super().__init__(**kwargs)

    @Gtk.Template.Callback()
    def _set_spin_start_val_from_key(self, _dialog, key, spin_row):
        spin_row.preset_key = key
        return self._current_preset.get(key, settings.get_int(key))

    @Gtk.Template.Callback()
    def _set_preset_name_start_value(self, _dialog):
        return "" if self._preset_name is None else self._preset_name

    @Gtk.Template.Callback()
    def _set_spin_value_and_key(self, spin_row, _pspec):
        key = spin_row.preset_key
        value = int(spin_row.get_value())
        self._current_preset[key] = value

        self._update_preset(self._preset_name)
        self._update_ui()

    @Gtk.Template.Callback()
    def _set_preset_name(self, entry, _pspec):
        self._update_preset(entry.get_text())
        self._update_ui()

    def _update_preset(self, new_preset_name):
        if not new_preset_name:
            return
        
        new_preset_name = new_preset_name.strip()

        if self._preset_name != new_preset_name and self._preset_name is not None:
            self._presets.pop(self._preset_name, None)

        self._preset_name = new_preset_name

        self._presets[self._preset_name] = self._current_preset
        settings.set_value("cycle-presets", GLib.Variant("a{sa{si}}", self._presets))
        
        print(f"Preset {self._preset_name} update from CyclePreset._update_preset")

    def _update_ui(self):
        self.window.on_reset_timer_activated()
        self.window.update_ui_timer()
        self.window.update_cycles_label_bg()


# FIXME: List not updates after adding a new preset, only when the list is closed and open again
@Gtk.Template(resource_path="/io/github/diegopvlk/Tomatillo/cycle_presets_list.ui")
class CyclePresetsList(Adw.Dialog):
    __gtype_name__ = "CyclePresetsList"

    add_preset_btn = Gtk.Template.Child()
    presets_list = Gtk.Template.Child()

    def __init__(self, active_window, **kwargs):
        super().__init__(**kwargs)
        self.window = active_window
        self._repopulate_list()

    def _repopulate_list(self):
        self.presets_list.remove_all()
        preset_names = settings.get_value("cycle-presets").unpack().keys()

        for name in preset_names:
            preset_item = Adw.ActionRow(title=name)
            preset_item.set_activatable(True)
            self.presets_list.append(preset_item)

    @Gtk.Template.Callback()
    def _on_item_clicked(self, list, item):
        preset_name = item.get_title()
        preset_dialog = CyclePreset(preset_name, self.window)
        preset_dialog.present(self)

    @Gtk.Template.Callback()
    def _add_new_preset(self, _btn):
        preset_dialog = CyclePreset(None, self.window)
        preset_dialog.present(self)
        self._repopulate_list()
