import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dataclasses import dataclass
from enum import Enum
from typing import Callable
import threading


@dataclass
class NowPlaying:
    is_playing: bool
    name: str
    artist_names: list[str]
    image_url: str | None


class ApiClient:
    def __init__(self) -> None:
        scope = [
            "user-read-playback-state",
            "user-modify-playback-state",
        ]
        self.spotify = spotipy.Spotify(
            client_credentials_manager=SpotifyOAuth(scope=",".join(scope))
        )

        self.now_playing_change_listeners = []

    def pause(self):
        self.spotify.pause_playback()
        self.__delayed_poll_now_playing()

    def play(self):
        self.spotify.start_playback()
        self.__delayed_poll_now_playing()

    def __delayed_poll_now_playing(self):
        threading.Timer(0.1, self.poll_now_playing).start()

    def poll_now_playing(self):
        now_playing = NowPlaying(
            is_playing=False,
            name="No session is active",
            artist_names=[],
            image_url=None,
        )
        data = self.spotify.currently_playing()
        if data:
            now_playing = NowPlaying(
                is_playing=data["is_playing"],
                name=data["item"]["name"],
                artist_names=[artist["name"] for artist in data["item"]["artists"]],
                image_url=data["item"]["album"]["images"][0]["url"],
            )

        for callback in self.now_playing_change_listeners:
            callback(now_playing)

    def connect_now_playing_change(self, callback: Callable[[NowPlaying], None]):
        self.now_playing_change_listeners.append(callback)
        return lambda: self.now_playing_change_listeners.remove(callback)

    def next_track(self):
        self.spotify.next_track()
        self.__delayed_poll_now_playing()

    def previous_track(self):
        self.spotify.previous_track()
        self.__delayed_poll_now_playing()
