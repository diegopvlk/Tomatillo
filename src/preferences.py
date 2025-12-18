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

from gi.repository import Adw, Gio, Gtk

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
    combo_sound = Gtk.Template.Child()
    switch_dnd = Gtk.Template.Child()
    switch_auto_focus = Gtk.Template.Child()
    switch_auto_break = Gtk.Template.Child()

    sound_map = {
        0: "alert.ogg",
        1: "alert2.ogg",
        2: "alert3.ogg",
        3: "alert4.ogg",
        4: "alert5.ogg",
        5: "air-raid.ogg",
        6: "applause.ogg",
        7: "laughter.ogg",
        8: "siren.ogg",
    }

    def __init__(self, active_window, **kwargs):
        super().__init__(**kwargs)
        self.window = active_window
        self._init_combo_sound()

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

    def _init_combo_sound(self):
        current_sound = settings.get_string("alert-sound")
        for index, sound_file in self.sound_map.items():
            if sound_file == current_sound:
                self.combo_sound.set_selected(index)
                break

    @Gtk.Template.Callback()
    def _set_combo_sound(self, combo_row, _pspec):
        selected = combo_row.get_selected()
        sound_file = self.sound_map.get(selected, "alert.ogg")
        settings.set_string("alert-sound", sound_file)
        self.window.update_sound_alert(sound_file)

    def _update_ui(self):
        self.window.on_reset_timer_activated()
        self.window.update_ui_timer()
        self.window.update_cycles_label_bg()
