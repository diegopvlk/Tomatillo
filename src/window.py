# window.py
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
from gettext import gettext as _

gi.require_version("Adw", "1")
gi.require_version("Gio", "2.0")
gi.require_version("GLib", "2.0")
gi.require_version("GstPlay", "1.0")
gi.require_version("Gtk", "4.0")
gi.require_version("Xdp", "1.0")

from gi.repository import Adw, Gio, GLib, GstPlay, Gtk, Xdp

from .preferences import settings


@Gtk.Template(resource_path="/io/github/diegopvlk/Tomatillo/window.ui")
class TomatilloWindow(Adw.ApplicationWindow):
    __gtype_name__ = "TomatilloWindow"

    breakpoint_1_5 = Gtk.Template.Child()
    breakpoint_2 = Gtk.Template.Child()
    timer_box = Gtk.Template.Child()
    button_box = Gtk.Template.Child()
    focus_icon = Gtk.Template.Child()
    break_icon = Gtk.Template.Child()
    label_cycles = Gtk.Template.Child()
    label_timer = Gtk.Template.Child()
    btn_start_pause = Gtk.Template.Child()
    btn_next = Gtk.Template.Child()
    btn_menu_reset = Gtk.Template.Child()
    presets_menu_label = Gtk.Template.Child()
    presets_section = Gtk.Template.Child()

    time_focus = settings.get_int("focus-time") * 60
    time_short_break = settings.get_int("short-b-time") * 60
    time_long_break = settings.get_int("long-b-time") * 60
    long_b_interval = settings.get_int("long-b-interval")

    current_preset_name = settings.get_string("chosen-cycle-preset")

    portal = Xdp.Portal()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_preset()
        if self.current_preset_name != "" and self.current_preset_name is not None:
            self.presets_menu_label.set_label(self.current_preset_name)
        self.repopulate_presets_section()

        GLib.set_application_name("Tomatillo")

        self.connect_breakpoints(self.breakpoint_1_5, "1-5")
        self.connect_breakpoints(self.breakpoint_2, "2")

        self.btn_start_pause.grab_focus()
        self.btn_start_pause.connect("clicked", self.on_start_pause_clicked)
        self.btn_next.connect("clicked", self.on_next_clicked)

        reset_session = Gio.SimpleAction.new("reset-session", None)
        reset_curr_timer = Gio.SimpleAction.new("reset-curr-timer", None)
        self.choose_preset = Gio.SimpleAction.new_stateful(
            "choose-preset",
            GLib.VariantType.new("s"),
            GLib.Variant("s", settings.get_string("chosen-cycle-preset")),
        )

        reset_session.connect("activate", self.set_start)
        reset_curr_timer.connect("activate", self.on_reset_timer_activated)
        self.choose_preset.connect("activate", self.on_preset_choise)

        self.get_application().add_action(reset_session)
        self.get_application().add_action(reset_curr_timer)
        self.get_application().add_action(self.choose_preset)

        self.sound_alert = GstPlay.Play.new(None)
        self.ogg_uri = "resource:///io/github/diegopvlk/Tomatillo/alert.ogg"
        self.sound_alert.set_uri(self.ogg_uri)

        self.set_start_values()
        self.set_start()

    def repopulate_presets_section(self):
        default_item = Gio.MenuItem.new_from_model(self.presets_section, 0)
        self.presets_section.remove_all()
        default_item.set_action_and_target_value(
            "app.choose-preset", GLib.Variant("s", "")
        )
        self.presets_section.append_item(default_item)

        presets = settings.get_value("cycle-presets").unpack()

        for name in presets.keys():
            menu_item = Gio.MenuItem.new(name, "app.choose-preset")
            menu_item.set_action_and_target_value(
                "app.choose-preset", GLib.Variant("s", name)
            )
            self.presets_section.append_item(menu_item)

    def set_start_values(self):
        self.timer_running = False
        self.timeout_id = None
        self.current_cycle = 1
        self.current_phase = "focus"
        self.time_left = self.time_focus

    # def on_set_defaults(self, *args):
    def on_set_defaults(self, action, parameter):
        settings.set_string("chosen-cycle-preset", "")
        self.choose_preset.change_state(GLib.Variant("s", ""))
        self.set_start()

    def update_preset(self):
        self.current_preset_name = settings.get_string("chosen-cycle-preset")
        # if no preset exists then use default time values
        if self.current_preset_name == "" or self.current_preset_name is None:
            self.time_focus = settings.get_int("focus-time") * 60
            self.time_short_break = settings.get_int("short-b-time") * 60
            self.time_long_break = settings.get_int("long-b-time") * 60
            self.long_b_interval = settings.get_int("long-b-interval")
            self.presets_menu_label.set_label(_("Default"))
            return

        current_preset = settings.get_value("cycle-presets").unpack()[
            self.current_preset_name
        ]

        self.time_focus = current_preset["focus-time"] * 60
        self.time_short_break = current_preset["short-b-time"] * 60
        self.time_long_break = current_preset["long-b-time"] * 60
        self.long_b_interval = current_preset["long-b-interval"]
        self.presets_menu_label.set_label(self.current_preset_name)

    def on_preset_choise(self, action, parameter):
        preset_name = parameter.get_string()
        action.set_state(parameter)
        settings.set_string("chosen-cycle-preset", preset_name)
        self.current_preset_name = preset_name
        self.set_start()

    def set_start(self, *args):
        # before doing reset, stop the timer because otherwise timer will be running
        self.on_reset_timer_activated()
        self.update_preset()
        self.set_start_values()
        self.update_ui_timer()
        self.update_cycles_label_bg()

    def on_start_pause_clicked(self, *args):
        self.get_application().withdraw_notification("timer-complete")
        if self.timer_running:
            self.pause_timer()
            self.btn_menu_reset.set_sensitive(True)
            self.btn_next.set_sensitive(True)
        else:
            self.start_timer()
            self.btn_menu_reset.set_sensitive(False)
            self.btn_next.set_sensitive(False)

    def on_reset_timer_activated(self, *args):
        self.pause_timer()
        self.reset_current_phase()
        self.btn_start_pause.set_label(_("Start"))
        self.btn_menu_reset.set_sensitive(True)
        self.btn_next.set_sensitive(True)

    def on_next_clicked(self, _btn):
        self.pause_timer()
        self.advance_phase()

    def start_timer(self):
        if not self.timer_running:
            self.btn_start_pause.set_label(_("Pause"))
            self.btn_start_pause.remove_css_class("suggested-action")
            self.timer_box.add_css_class("fill-timer-box-shadow")
            self.timer_running = True
            self.timeout_id = GLib.timeout_add(1000, self.on_tick)

    def pause_timer(self):
        if self.timer_running:
            self.btn_start_pause.set_label(_("Resume"))
            self.btn_start_pause.add_css_class("suggested-action")
            self.timer_box.remove_css_class("fill-timer-box-shadow")
            self.timer_running = False
            if self.timeout_id:
                GLib.source_remove(self.timeout_id)
                self.timeout_id = None
            self.set_background_string("")
        else:
            self.btn_start_pause.set_label(_("Start"))

    def on_tick(self):
        if self.time_left > 0:
            self.time_left -= 1
            self.update_ui_timer()
            return GLib.SOURCE_CONTINUE
        else:
            self.handle_timer_complete()
            return GLib.SOURCE_REMOVE

    def handle_timer_complete(self):
        self.btn_menu_reset.set_sensitive(True)
        self.btn_next.set_sensitive(True)

        notification = self.get_notification()

        self.advance_phase()
        self.pause_timer()

        if settings.get_boolean("notif-sound"):
            self.sound_alert.play()

        if settings.get_boolean("auto-focus") and self.current_phase == "focus":
            self.on_start_pause_clicked()

        if settings.get_boolean("auto-break") and self.current_phase != "focus":
            self.on_start_pause_clicked()

        start_cycle = Gio.SimpleAction.new("start-cycle", None)
        start_cycle.connect("activate", self.on_start_pause_clicked)
        self.get_application().add_action(start_cycle)

        self.get_application().send_notification("timer-complete", notification)

    def advance_phase(self):
        if self.current_phase == "focus":
            if self.current_cycle < self.long_b_interval:
                self.current_phase = "short_break"
                self.time_left = self.time_short_break
            else:
                self.current_phase = "long_break"
                self.time_left = self.time_long_break

        elif self.current_phase in ["short_break", "long_break"]:
            if self.current_phase == "long_break":
                self.current_cycle = 1
            else:
                self.current_cycle += 1

            self.current_phase = "focus"
            self.time_left = self.time_focus

        self.update_ui_timer()
        self.update_cycles_label_bg()

    def reset_current_phase(self):
        self.time_left = getattr(
            self,
            {
                "focus": "time_focus",
                "short_break": "time_short_break",
                "long_break": "time_long_break",
            }[self.current_phase],
        )

        if self.current_cycle > self.long_b_interval:
            self.current_cycle = self.long_b_interval

        self.update_ui_timer()

    def update_ui_timer(self):
        hours = self.time_left // 3600
        minutes = (self.time_left % 3600) // 60
        seconds = self.time_left % 60

        time_label = (
            f"{hours}:{minutes:02d}:{seconds:02d}"
            if hours > 0
            else f"{minutes:02d}:{seconds:02d}"
        )

        self.label_timer.set_label(time_label)

        status_label = {
            "focus": _("Focus"),
            "short_break": _("Short Break"),
            "long_break": _("Long Break"),
        }[self.current_phase]

        if not self.get_visible():
            status_label += " • " + time_label
            self.set_background_string(status_label.capitalize())

    def update_cycles_label_bg(self):
        self.add_css_class("teal-bg")
        self.remove_css_class("slate-bg")
        self.remove_css_class("green-bg")
        self.break_icon.set_visible(True)

        if self.current_phase == "focus":
            self.add_css_class("slate-bg")
            self.remove_css_class("teal-bg")
            self.remove_css_class("green-bg")
            self.break_icon.set_visible(False)

        elif self.current_phase == "long_break":
            self.add_css_class("green-bg")
            self.remove_css_class("slate-bg")
            self.remove_css_class("teal-bg")

        if self.long_b_interval > 6:
            label_text = f"{self.current_cycle}/{self.long_b_interval}"
            self.label_cycles.remove_css_class("cycles-dots")
        else:
            current = self.current_cycle
            total = self.long_b_interval
            filled_dots = "●" * current
            empty_dots = "○" * (total - current)
            label_text = filled_dots + empty_dots
            self.label_cycles.add_css_class("cycles-dots")

        self.label_cycles.set_label(label_text)

    def get_notification(self):
        icon = Gio.ThemedIcon.new_from_names(
            [
                "preferences-system-time-symbolic",
                "alarm-symbolic",
                "appointment-soon-symbolic",
            ]
        )

        notification = Gio.Notification.new(_("Break Time"))
        notification.set_icon(icon)

        if settings.get_boolean("bypass-dnd"):
            notification.set_priority(Gio.NotificationPriority.URGENT)

        if self.current_phase == "focus":
            if self.current_cycle != 4:
                notification.set_body(_("Time for a short break."))
            else:
                notification.set_body(_("Time for a long break."))
            if not settings.get_boolean("auto-break"):
                notification.add_button(_("Start Break"), "app.start-cycle")
        else:
            notification.set_title(_("Focus Mode"))
            notification.set_body(_("Break is over!"))
            if not settings.get_boolean("auto-focus"):
                notification.add_button(_("Start Focus"), "app.start-cycle")

        return notification

    def connect_breakpoints(self, bp, scale):
        bp.connect("apply", lambda *a: self.add_css_scaling(scale, *a))
        bp.connect("unapply", lambda *a: self.remove_css_scaling(scale, *a))

    def add_css_scaling(self, scale, *args):
        self.button_box.add_css_class(f"button-box-{scale}")
        self.timer_box.add_css_class(f"timer-box-{scale}")

    def remove_css_scaling(self, scale, *args):
        self.button_box.remove_css_class(f"button-box-{scale}")
        self.timer_box.remove_css_class(f"timer-box-{scale}")

    def set_background_string(self, string):
        self.portal.set_background_status(
            string,  # String
            None,  # Gio.Cancellable
            None,  # Gio.AsyncReadyCallback
        )
