import os

os.environ["SDL_AUDIODRIVER"] = "dummy"
import unittest
from game.audio import Audio
from game.settings import DEFAULTS


class AudioTests(unittest.TestCase):
    def test_every_sound_decodes_and_footsteps_vary(self):
        audio = Audio(dict(DEFAULTS))
        self.addCleanup(audio.close)
        self.assertTrue(audio.enabled, audio.error)
        for surface, pool in audio.surfaces.items():
            self.assertGreaterEqual(len(pool), 5)
            first = audio.choose(surface, pool)
            second = audio.choose(surface, pool)
            self.assertIsNot(first, second)
            audio.play("step", surface)
        for key in audio.sounds:
            audio.play(key)
        audio.environment(True)
        audio.duck("You open a wooden door.")
        audio.update()


if __name__ == "__main__":
    unittest.main()
