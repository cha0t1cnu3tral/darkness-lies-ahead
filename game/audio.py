"""Recorded audio: reserved ambience channels, pooled effects, speech ducking."""

import json
import logging
import math
import os
import random
import time

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame
from .paths import ASSETS, DATA


class Audio:
    def __init__(self, settings):
        self.settings = settings
        self.enabled = False
        self.error = ""
        self.last = {}
        self.indoor = False
        self.duck_until = 0
        self.positioned = {}
        self.next_creak = time.monotonic() + 8
        self.ambient_gain = 0
        self.manifest = json.loads((DATA / "audio.json").read_text(encoding="utf-8"))
        self.sounds = {}
        self.surfaces = {}
        root = ASSETS / "audio"
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            pygame.mixer.set_num_channels(24)
            pygame.mixer.set_reserved(2)
            for key, files in self.manifest["effects"].items():
                self.sounds[key] = [pygame.mixer.Sound(str(root / f)) for f in files]
            for surface, pattern in self.manifest["surfaces"].items():
                paths = sorted((root / "impact-sounds").glob(pattern))
                if not paths:
                    raise FileNotFoundError("Missing footsteps for " + surface)
                self.surfaces[surface] = [pygame.mixer.Sound(str(p)) for p in paths]
            self.wind = pygame.mixer.Sound(str(root / self.manifest["ambience"]))
            self.creaks = [
                pygame.mixer.Sound(str(root / "rpg-audio" / f"creak{i}.ogg")) for i in range(1, 4)
            ]
            pygame.mixer.music.load(str(root / self.manifest["music"]))
            pygame.mixer.music.play(-1, fade_ms=2000)
            pygame.mixer.Channel(0).play(self.wind, loops=-1, fade_ms=2000)
            self.enabled = True
            self.update()
        except (pygame.error, OSError) as error:
            self.error = str(error)
            logging.exception("Audio startup failed")
            pygame.mixer.quit()

    def choose(self, key, pool):
        # Avoid identical adjacent footsteps while preserving recorded variants.
        candidates = [i for i in range(len(pool)) if i != self.last.get(key)] or [0]
        index = random.choice(candidates)
        self.last[key] = index
        return pool[index]

    def play(self, key, surface="", dx=0, dy=0, gain=1):
        if not self.enabled:
            return
        pool = (
            self.surfaces.get(surface, [])
            if key in ("step", "enemy_step", "land")
            else self.sounds.get(key, [])
        )
        if not pool:
            return
        sound = self.choose(surface if surface else key, pool)
        channel_index = next(
            (i for i in range(2, 24) if not pygame.mixer.Channel(i).get_busy()), None
        )
        if channel_index is not None:
            channel = pygame.mixer.Channel(channel_index)
            distance = math.hypot(dx, dy)
            pan = max(-0.9, min(0.9, dx / 8))
            attenuation = gain / (1 + distance * 0.15)
            # All directions also have text; stereo panning is supplementary.
            self.positioned[channel_index] = (
                channel,
                attenuation,
                pan,
            )
            volume = self.settings["master"] * self.settings["effects"] / 10000 * attenuation
            channel.set_volume(volume * min(1, 1 - pan), volume * min(1, 1 + pan))
            channel.play(sound)

    def duck(self, text):
        if self.settings["duck"]:
            self.duck_until = time.monotonic() + min(12, max(1, len(text.split()) / 3))

    def environment(self, indoor):
        self.indoor = indoor
        self.update()

    def update(self):
        if not self.enabled:
            return
        master = self.settings["master"] / 100
        duck = 0.3 if time.monotonic() < self.duck_until and self.settings["duck"] else 1
        pygame.mixer.music.set_volume(master * self.settings["music"] / 100 * duck)
        target_gain = master * self.settings["ambience"] / 100 * (0.18 if self.indoor else 1) * duck
        self.ambient_gain += (target_gain - self.ambient_gain) * 0.2
        pygame.mixer.Channel(0).set_volume(self.ambient_gain)
        if self.indoor and time.monotonic() >= self.next_creak:
            channel = pygame.mixer.Channel(1)
            channel.play(self.choose("ambient_creak", self.creaks), fade_ms=50)
            self.next_creak = time.monotonic() + random.uniform(9, 24)
        room_gain = master * self.settings["ambience"] / 100 * 0.35 * duck if self.indoor else 0
        pygame.mixer.Channel(1).set_volume(room_gain * 0.6, room_gain)
        for key, (channel, gain, pan) in list(self.positioned.items()):
            if not channel.get_busy():
                del self.positioned[key]
                continue
            volume = master * self.settings["effects"] / 100 * gain
            channel.set_volume(volume * min(1, 1 - pan), volume * min(1, 1 + pan))

    def close(self):
        if self.enabled:
            pygame.mixer.quit()
