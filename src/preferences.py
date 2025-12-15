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

gi.require_version("Gio", "2.0")
gi.require_version("Gtk", "4.0")

from gi.repository import Gio, Gtk

settings = Gio.Settings.new("io.github.diegopvlk.Tomatillo")


def open_preferences(active_window):
    builder = Gtk.Builder.new_from_resource(
        "/io/github/diegopvlk/Tomatillo/preferences.ui"
    )

    focus_time = builder.get_object("focus_time")
    short_b_time = builder.get_object("short_b_time")
    long_b_time = builder.get_object("long_b_time")
    long_b_interval = builder.get_object("long_b_interval")
    prefs_dialog = builder.get_object("prefs_dialog")
    switch_background = builder.get_object("switch_background")
    switch_sound = builder.get_object("switch_sound")
    switch_dnd = builder.get_object("switch_dnd")
    switch_auto_focus = builder.get_object("switch_auto_focus")
    switch_auto_break = builder.get_object("switch_auto_break")

    def update_ui():
        active_window.on_reset_timer_activated()
        active_window.update_ui_timer()
        active_window.update_cycles_label_bg()

    def set_focus_time(spin_row, _param):
        value = int(spin_row.get_value())
        active_window.time_focus = value * 60
        update_ui()
        settings.set_int("focus-time", value)

    def set_short_b_time(spin_row, _param):
        value = int(spin_row.get_value())
        active_window.time_short_break = value * 60
        update_ui()
        settings.set_int("short-b-time", value)

    def set_long_b_time(spin_row, _param):
        value = int(spin_row.get_value())
        active_window.time_long_break = value * 60
        update_ui()
        settings.set_int("long-b-time", value)

    def set_long_b_interval(spin_row, _param):
        value = int(spin_row.get_value())
        active_window.time_long_interval = value
        update_ui()
        settings.set_int("long-b-interval", value)

    def run_in_bg_changed(sett, key):
        state = sett.get_boolean(key)
        active_window.set_hide_on_close(state)

    def set_state_run_in_bg(_switch, state):
        settings.set_boolean("run-in-background", state)

    def set_state_notif_sound(_switch, state):
        settings.set_boolean("notif-sound", state)

    def set_state_bypass_dnd(_switch, state):
        settings.set_boolean("bypass-dnd", state)

    def set_state_auto_focus(_switch, state):
        settings.set_boolean("auto-focus", state)

    def set_state_auto_break(_switch, state):
        settings.set_boolean("auto-break", state)

    focus_time.set_value(settings.get_int("focus-time"))
    short_b_time.set_value(settings.get_int("short-b-time"))
    long_b_time.set_value(settings.get_int("long-b-time"))
    long_b_interval.set_value(settings.get_int("long-b-interval"))
    switch_background.set_active(settings.get_boolean("run-in-background"))
    switch_sound.set_active(settings.get_boolean("notif-sound"))
    switch_dnd.set_active(settings.get_boolean("bypass-dnd"))
    switch_auto_focus.set_active(settings.get_boolean("auto-focus"))
    switch_auto_break.set_active(settings.get_boolean("auto-break"))

    focus_time.connect("notify::value", set_focus_time)
    short_b_time.connect("notify::value", set_short_b_time)
    long_b_time.connect("notify::value", set_long_b_time)
    long_b_interval.connect("notify::value", set_long_b_interval)
    switch_background.connect("state-set", set_state_run_in_bg)
    switch_sound.connect("state-set", set_state_notif_sound)
    switch_dnd.connect("state-set", set_state_bypass_dnd)
    switch_auto_focus.connect("state-set", set_state_auto_focus)
    switch_auto_break.connect("state-set", set_state_auto_break)

    settings.connect("changed::run-in-background", run_in_bg_changed)

    prefs_dialog.present(active_window)
