# main.py
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

import sys
import gi
from gettext import gettext as _

gi.require_version("Adw", "1")
gi.require_version("Gio", "2.0")
gi.require_version("Gtk", "4.0")

from gi.repository import Adw, Gio, Gtk
from .window import TomatilloWindow
from .preferences import open_preferences, settings


class TomatilloApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(
            application_id="io.github.diegopvlk.Tomatillo",
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
            resource_base_path="/io/github/diegopvlk/Tomatillo",
        )
        self.create_action("quit", lambda *_: self.quit(), ["<control>q"])
        self.create_action("about", self.on_about_action)
        self.create_action(
            "preferences", self.on_preferences_action, ["<primary>comma"]
        )

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        win = self.props.active_window
        if not win:
            win = TomatilloWindow(application=self)
        win.present()

        run_in_bg = settings.get_boolean("run-in-background")
        win.set_hide_on_close(run_in_bg)

    def on_about_action(self, *args):
        """Callback for the app.about action."""
        about = Adw.AboutDialog(
            application_name="Tomatillo",
            application_icon="io.github.diegopvlk.Tomatillo",
            developer_name="Diego Povliuk",
            version="1.0.0",
            developers=["Diego Povliuk"],
            copyright="© 2025 Diego Povliuk",
            issue_url="https://github.com/diegopvlk/Tomatillo/issues",
            license_type=Gtk.License.GPL_3_0,
        )
        # Translators: Replace "translator-credits" with your name/username, and optionally an email or URL.
        about.set_translator_credits(_("translator-credits"))
        about.add_link("Donate", "https://github.com/diegopvlk/Tomatillo#donate")
        about.add_other_app(
            "io.github.diegopvlk.Dosage", "Dosage", "Keep track of your treatments"
        )
        about.present(self.props.active_window)

    def on_preferences_action(self, *args):
        """Callback for the app.preferences action."""
        open_preferences(self.props.active_window)

    def create_action(self, name, callback, shortcuts=None):
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)


def main(_version):
    """The application's entry point."""
    app = TomatilloApplication()
    return app.run(sys.argv)
