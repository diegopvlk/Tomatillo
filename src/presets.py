# presets.py
#
# Copyright 2025 Diego Povliuk, KolomarenkoDmytrii
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

import uuid

import gi
from gettext import gettext as _

gi.require_version("Adw", "1")
gi.require_version("Gtk", "4.0")
gi.require_version("GLib", "2.0")

from gi.repository import Adw, Gtk, GLib
from .preferences import settings


@Gtk.Template(resource_path="/io/github/diegopvlk/Tomatillo/cycle-preset.ui")
class CyclePreset(Adw.Dialog):
    __gtype_name__ = "CyclePreset"

    preset_toast_overlay = Gtk.Template.Child()
    preset_name = Gtk.Template.Child()
    focus_time = Gtk.Template.Child()
    short_b_time = Gtk.Template.Child()
    long_b_time = Gtk.Template.Child()
    long_b_interval = Gtk.Template.Child()
    save_btn = Gtk.Template.Child()
    deletion_btn_group = Gtk.Template.Child()

    def __init__(self, preset_id, active_window, presets_list, **kwargs):
        self.window = active_window
        self._presets_list = presets_list
        self._preset_id = preset_id

        defaults = {
            "name": GLib.Variant("s", ""),
            "focus-time": GLib.Variant("i", settings.get_int("focus-time")),
            "short-b-time": GLib.Variant("i", settings.get_int("short-b-time")),
            "long-b-time": GLib.Variant("i", settings.get_int("long-b-time")),
            "long-b-interval": GLib.Variant("i", settings.get_int("long-b-interval")),
        }

        self._presets = settings.get_value("cycle-presets").unpack()
        for preset_id in self._presets.keys():
            preset = self._presets[preset_id]
            self._presets[preset_id] = {
                "name": GLib.Variant("s", preset["name"]),
                "focus-time": GLib.Variant("i", preset["focus-time"]),
                "short-b-time": GLib.Variant("i", preset["short-b-time"]),
                "long-b-time": GLib.Variant("i", preset["long-b-time"]),
                "long-b-interval": GLib.Variant("i", preset["long-b-interval"]),
            }

        if self._preset_id is None:
            self._preset_id = str(uuid.uuid4())
            self._presets[self._preset_id] = defaults
        else:
            existing_params = self._presets.get(self._preset_id, {})
            self._presets[self._preset_id] = {**defaults, **existing_params}

        # call the constructor of the parent class after initializing variables
        # because, maybe, callbacks are defined in a Blueprint file, so they are
        # declared before the parent constructor (which is responsible for widget
        # creation by a template) is called so they cannot access object attributes
        super().__init__(**kwargs)

        if self._preset_id is None:
            self.set_title(_("New Preset"))
            self.save_btn.set_label(_("Add"))
            self.deletion_btn_group.set_visible(False)
        elif self._preset_id is False:
            # default preset
            self.preset_name.set_sensitive(False)
            self.preset_name.set_text(_("Default"))
            self.deletion_btn_group.set_visible(False)

    @Gtk.Template.Callback()
    def _on_cancel_clicked(self, _obj):
        self.close()

    @Gtk.Template.Callback()
    def _set_spin_start_val_from_key(self, _dialog, key, spin_row):
        spin_row.preset_key = key
        return self._presets[self._preset_id][key].unpack()

    @Gtk.Template.Callback()
    def _set_preset_name_start_value(self, _dialog):
        return self._presets[self._preset_id]["name"].unpack()

    @Gtk.Template.Callback()
    def _on_save_preset(self, _obj):
        current_text = self.preset_name.get_text()
        if current_text.strip() in [p["name"].unpack() for p in self._presets.values()]:
            toast = Adw.Toast(title=_("A preset with this name already exists"))
            self.preset_toast_overlay.dismiss_all()
            self.preset_toast_overlay.add_toast(toast)
        else:
            self._update_preset(current_text)
            self._update_ui()
            self.close()

    @Gtk.Template.Callback()
    def _on_deletion_request(self, _btn):
        deletion_dialog = CyclePresetDeletion(
            self._presets_list, self._preset_id, self.window, self
        )
        deletion_dialog.present(self)

    def _update_preset(self, new_preset_name):
        if not new_preset_name:
            return

        preset_values = {
            "name": GLib.Variant("s", new_preset_name.strip()),
            "focus-time": GLib.Variant("i", self.focus_time.props.value),
            "short-b-time": GLib.Variant("i", self.short_b_time.props.value),
            "long-b-time": GLib.Variant("i", self.long_b_time.props.value),
            "long-b-interval": GLib.Variant("i", self.long_b_interval.props.value),
        }

        self._presets[self._preset_id] = preset_values
        settings.set_value("cycle-presets", GLib.Variant("a{sa{sv}}", self._presets))

        self._presets_list.repopulate_list()
        # after a change in the preset reset the current session
        self.window.set_start()
        self.window.repopulate_presets_section()

    def _update_ui(self):
        self.window.on_reset_timer_activated()
        self.window.update_ui_timer()
        self.window.update_cycles_label_bg()


@Gtk.Template(resource_path="/io/github/diegopvlk/Tomatillo/cycle-preset-deletion.ui")
class CyclePresetDeletion(Adw.AlertDialog):
    __gtype_name__ = "CyclePresetDeletion"

    def __init__(self, presets_list, preset_id, active_window, parent, **kwargs):
        super().__init__(**kwargs)
        self._presets_list = presets_list
        self._preset_id = preset_id
        self._parent = parent
        self.window = active_window

    @Gtk.Template.Callback()
    def _on_dialog_choise(self, _dialog, response):
        if response == "delete":
            presets = settings.get_value("cycle-presets").unpack()
            presets.pop(self._preset_id, None)
            for preset_id in presets.keys():
                preset = presets[preset_id]
                presets[preset_id] = {
                    "name": GLib.Variant("s", preset["name"]),
                    "focus-time": GLib.Variant("i", preset["focus-time"]),
                    "short-b-time": GLib.Variant("i", preset["short-b-time"]),
                    "long-b-time": GLib.Variant("i", preset["long-b-time"]),
                    "long-b-interval": GLib.Variant("i", preset["long-b-interval"]),
                }

            settings.set_value("cycle-presets", GLib.Variant("a{sa{sv}}", presets))
            current_preset_id = settings.get_string("chosen-cycle-preset")
            if current_preset_id == self._preset_id:
                settings.set_string("chosen-cycle-preset", "")

            self._presets_list.repopulate_list()
            self.window.current_preset_name = None
            self.window.repopulate_presets_section()
            self.window.set_start()
            self._parent.close()


@Gtk.Template(resource_path="/io/github/diegopvlk/Tomatillo/cycle-presets-list.ui")
class CyclePresetsList(Adw.Dialog):
    __gtype_name__ = "CyclePresetsList"

    add_preset_btn = Gtk.Template.Child()
    presets_list = Gtk.Template.Child()

    def __init__(self, active_window, **kwargs):
        super().__init__(**kwargs)
        self.window = active_window
        self._names_to_ids = {}
        self.repopulate_list()

    def repopulate_list(self):
        self.presets_list.remove_all()

        preset_default_row = Adw.ActionRow(title=_("Default"), activatable=True)
        end_icon = Gtk.Image(icon_name="pan-end-symbolic", margin_end=2)
        preset_default_row.add_suffix(end_icon)
        self.presets_list.append(preset_default_row)

        preset_default_row.connect("activated", self._on_default_preset_activated)

        presets = settings.get_value("cycle-presets").unpack()
        self._names_to_ids = {
            presets[preset_id]["name"]: preset_id for preset_id in presets.keys()
        }
        for preset_id in presets.keys():
            preset_row = Adw.ActionRow(
                title=presets[preset_id]["name"], activatable=True, use_markup=False
            )
            preset_del_btn = Gtk.Button(
                valign=Gtk.Align.CENTER,
                icon_name="user-trash-symbolic",
                css_classes=["circular", "destructive-action", "flat"],
                tooltip_text=_("Delete"),
                margin_end=3,
            )
            end_icon = Gtk.Image(icon_name="pan-end-symbolic", margin_end=2)
            preset_row.add_suffix(preset_del_btn)
            preset_row.add_suffix(end_icon)
            preset_row.connect("activated", self._on_preset_activated)
            self.presets_list.append(preset_row)

    def _on_default_preset_activated(self, row):
        preset_dialog = CyclePreset(False, self.window, self)
        preset_dialog.present(self)

    def _on_preset_activated(self, row):
        preset_id = self._names_to_ids[row.get_title()]
        preset_dialog = CyclePreset(preset_id, self.window, self)
        preset_dialog.present(self)

    @Gtk.Template.Callback()
    def _add_new_preset(self, _btn):
        preset_dialog = CyclePreset(None, self.window, self)
        preset_dialog.present(self)
        self.repopulate_list()
