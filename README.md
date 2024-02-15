# Spotimote

GTK based Spotify Connect remote.

NOTE: This application doesn't play any audio. This decision was made to keep the scope of the project small enough to maintain. Workaround is to run the official Spotify client or other clients like spotifyd alongside.

# Usage

NOTE: This is a MVP, so it is not packaged properly yet

Fedora dependencies: `gcc gobject-introspection-devel cairo-gobject-devel pkg-config python3-devel gtk4`
For other distrubutions, have a look at PyGObject-documentation ([here](https://gnome.pages.gitlab.gnome.org/pygobject/getting_started.html#fedora-getting-started)) for installing in virtual environment.

1. Download `poetry` for package management
2. Run `poetry install`
3. Run `poetry run start`



