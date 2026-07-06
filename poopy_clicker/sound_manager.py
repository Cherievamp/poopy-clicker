import os
from PyQt6.QtMultimedia import QSoundEffect, QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl


SUPPORTED_MUSIC_EXT = {".mp3", ".ogg", ".wav", ".flac", ".m4a", ".wma"}


class SoundManager:
    def __init__(self, asset_path):
        self.asset_path = asset_path
        self._sfx = {}
        self._player = QMediaPlayer()
        self._audio_output = QAudioOutput()
        self._player.setAudioOutput(self._audio_output)
        self._tracks = []
        self._current_track_index = -1
        self._sfx_enabled = True
        self._music_enabled = True
        self._sfx_volume = 0.7
        self._music_volume = 0.5

        self._player.mediaStatusChanged.connect(self._on_media_status)

    def load_all(self):
        self._load_sfx()
        self._load_music()

    def _load_sfx(self):
        sfx_dir = os.path.join(self.asset_path, "sfx")
        if not os.path.isdir(sfx_dir):
            return
        for fname in os.listdir(sfx_dir):
            if not fname.endswith(".wav"):
                continue
            name = fname[:-4]
            path = os.path.join(sfx_dir, fname)
            effect = QSoundEffect()
            effect.setSource(QUrl.fromLocalFile(path))
            effect.setVolume(self._sfx_volume)
            self._sfx[name] = effect

    def _load_music(self):
        music_dir = os.path.join(self.asset_path, "music")
        self._tracks = []
        if not os.path.isdir(music_dir):
            return
        for fname in sorted(os.listdir(music_dir)):
            ext = os.path.splitext(fname)[1].lower()
            if ext in SUPPORTED_MUSIC_EXT:
                self._tracks.append({
                    "name": fname,
                    "path": os.path.join(music_dir, fname),
                })

    def get_tracks(self):
        return list(self._tracks)

    def get_current_track_index(self):
        return self._current_track_index

    def play_track(self, index):
        if index < 0 or index >= len(self._tracks):
            return
        self._current_track_index = index
        self._player.setSource(QUrl.fromLocalFile(self._tracks[index]["path"]))
        if self._music_enabled:
            self._player.play()

    def stop_music(self):
        self._player.stop()

    def _on_media_status(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia and self._current_track_index >= 0:
            self._player.setPosition(0)
            if self._music_enabled:
                self._player.play()

    def play(self, name):
        if not self._sfx_enabled:
            return
        effect = self._sfx.get(name)
        if effect is not None:
            effect.play()

    def stop(self, name):
        effect = self._sfx.get(name)
        if effect is not None:
            effect.stop()

    def stop_all(self):
        for effect in self._sfx.values():
            effect.stop()

    def is_playing(self, name):
        effect = self._sfx.get(name)
        return effect is not None and effect.isPlaying()

    def set_sfx_volume(self, vol):
        self._sfx_volume = max(0.0, min(1.0, vol))
        for effect in self._sfx.values():
            effect.setVolume(self._sfx_volume)

    def get_sfx_volume(self):
        return self._sfx_volume

    def set_music_volume(self, vol):
        self._music_volume = max(0.0, min(1.0, vol))
        self._audio_output.setVolume(self._music_volume)

    def get_music_volume(self):
        return self._music_volume

    def set_sfx_enabled(self, enabled):
        self._sfx_enabled = enabled
        if not enabled:
            for effect in self._sfx.values():
                effect.stop()

    def get_sfx_enabled(self):
        return self._sfx_enabled

    def set_music_enabled(self, enabled):
        self._music_enabled = enabled
        if enabled and self._current_track_index >= 0:
            self._player.play()
        elif not enabled:
            self._player.pause()

    def get_music_enabled(self):
        return self._music_enabled

    def apply_settings(self, settings):
        self.set_sfx_enabled(settings.get("sound_enabled", True))
        self.set_music_enabled(settings.get("music_enabled", True))
        self.set_sfx_volume(settings.get("sfx_volume", 0.7))
        self.set_music_volume(settings.get("music_volume", 0.5))
        selected = settings.get("selected_music_track", "")
        if selected and self._tracks:
            for i, t in enumerate(self._tracks):
                if t["name"] == selected:
                    self.play_track(i)
                    break
