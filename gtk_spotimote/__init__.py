import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import GLib, Gtk, Adw, Gio, Pango, Gdk, GdkPixbuf
from gtk_spotimote import constants
from gtk_spotimote.api_client import ApiClient, NowPlaying
from time import sleep
from pathlib import Path
import urllib


class WebImage(Gtk.Image):
    def set_url(self, url: str):
        if hasattr(self, "current_url") and self.current_url == url:
            # Avoid reloading same image
            return
        response = urllib.request.urlopen(url)
        input_stream = Gio.MemoryInputStream.new_from_data(response.read())
        pixbuf = GdkPixbuf.Pixbuf.new_from_stream(input_stream)
        texture = Gdk.Texture.new_for_pixbuf(pixbuf)
        self.set_from_paintable(texture)
        self.current_url = url


class MainWindow(Gtk.ApplicationWindow):

    def __init__(self, application: Gtk.Application):
        super().__init__(application=application, title=constants.APP_NAME)

        self.api_client = ApiClient()

        self.is_playing = False

        self.api_client.connect_now_playing_change(self.handle_now_playing_change)

        self.load_css()

        root_object = self.ui_create_root_object()
        self.set_child(root_object)

        self.api_client.poll_now_playing()

    def handle_now_playing_change(self, now_playing: NowPlaying):
        self.is_playing = now_playing.is_playing

    def load_css(self):
        provider = Gtk.CssProvider()
        css_file = Gio.File.new_for_path(str(Path(__file__).parent / "style.css"))
        provider.load_from_file(css_file)

        display = self.get_display()
        self.get_style_context().add_provider_for_display(
            display,
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_USER,
        )

    def ui_create_root_object(self):

        main_container = self.ui_create_main_container()

        start_spacer = Gtk.Box(vexpand=True)
        end_spacer = Gtk.Box(vexpand=True)

        root_object = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            height_request=300,
            width_request=500,
            valign=Gtk.Align.FILL,
            halign=Gtk.Align.FILL,
        )
        root_object.add_css_class("root-object")

        for child in [start_spacer, main_container, end_spacer]:
            root_object.append(child)

        return root_object

    def ui_create_main_container(self):
        main_container = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            halign=Gtk.Align.CENTER,
            valign=Gtk.Align.CENTER,
            spacing=32,
        )
        main_container.add_css_class("main-container")

        now_playing_container = self.ui_create_now_playing_container()

        buttons_container = self.ui_create_buttons()

        for child in [now_playing_container, buttons_container]:
            main_container.append(child)

        return main_container

    def ui_create_now_playing_container(self):
        track_name_label = Gtk.Label(
            ellipsize=Pango.EllipsizeMode.END,
            max_width_chars=32,
            css_classes=["track-name-label"],
        )
        track_artists_label = Gtk.Label(
            ellipsize=Pango.EllipsizeMode.END,
            max_width_chars=32,
        )

        image = WebImage(
            css_classes=["track-image"],
            overflow=Gtk.Overflow.HIDDEN,
        )
        image.set_size_request(200, 200)
        image_container = Gtk.AspectFrame(
            child=image,
            ratio=1,
            css_classes=["track-image-container"],
        )

        def callback(now_playing: NowPlaying):
            track_artists_label.set_label(", ".join(now_playing.artist_names))
            track_name_label.set_label(now_playing.name)
            if now_playing.image_url:
                image.set_url(now_playing.image_url)

        self.api_client.connect_now_playing_change(callback)

        now_playing_container = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            halign=Gtk.Align.START,
            spacing=8,
        )

        for child in [image_container, track_name_label, track_artists_label]:
            now_playing_container.append(child)

        return now_playing_container

    def ui_create_buttons(self):

        previous_button = Gtk.Button(
            label="Previous Track",
            valign=Gtk.Align.CENTER,
        )
        previous_button.connect("clicked", self.handle_previous_click)
        previous_button.add_css_class("controls-skip-buttons")
        previous_button.set_icon_name("media-skip-backward-symbolic")

        pause_play_button = Gtk.Button(
            label="Pause/Play",
            valign=Gtk.Align.CENTER,
        )
        pause_play_button.connect("clicked", self.handle_play_pause_click)
        pause_play_button.add_css_class("controls-play-pause")
        pause_play_button.set_icon_name("media-playback-start-symbolic")

        def callback(now_playing: NowPlaying):
            if now_playing.is_playing:
                pause_play_button.set_icon_name("media-playback-pause-symbolic")
            else:
                pause_play_button.set_icon_name("media-playback-start-symbolic")

        self.api_client.connect_now_playing_change(callback)

        next_button = Gtk.Button(
            label="Next Track",
            valign=Gtk.Align.CENTER,
        )
        next_button.connect("clicked", self.handle_next_click)
        next_button.add_css_class("controls-skip-buttons")
        next_button.set_icon_name("media-skip-forward-symbolic")

        buttons_container = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=24,
            halign=Gtk.Align.CENTER,
        )
        for button in [previous_button, pause_play_button, next_button]:
            buttons_container.append(button)

        return buttons_container

    def handle_play_pause_click(self, _):
        if self.is_playing:
            self.api_client.pause()
        else:
            self.api_client.play()

    def handle_previous_click(self, _):
        self.api_client.previous_track()

    def handle_next_click(self, _):
        self.api_client.next_track()


class MyApplication(Adw.Application):
    def __init__(self):
        super().__init__(application_id=constants.APPLICATION_ID)
        GLib.set_application_name(constants.APP_NAME)

    def do_activate(self):
        window = MainWindow(application=self)
        window.present()


app = MyApplication()
exit_status = app.run(sys.argv)
sys.exit(exit_status)
