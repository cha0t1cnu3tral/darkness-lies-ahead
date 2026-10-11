import tempfile
import unittest
from unittest.mock import patch

from game.engine import Game, World, WORLD, SIZE


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.game = Game(42)
        self.addCleanup(self.game.world.close)

    def test_walk_opens_door_before_entering_and_wall_is_solid(self):
        game = self.game
        game.move("east")
        self.assertEqual((game.x, game.y), (4, 8))
        game.move("east")
        self.assertEqual((game.x, game.y), (4, 8))
        self.assertTrue(game.world.at(5, 8)[1][0]["opened"])
        game.move("east")
        self.assertEqual((game.x, game.y), (5, 8))
        before = game.turn
        game.move("north")
        self.assertEqual((game.x, game.y), (5, 8))
        self.assertEqual(game.turn, before)

    def test_search_once_and_inspect_without_advancing(self):
        game = self.game
        game.x, game.y = 7, 6
        game.describe()
        game.nearby()
        game.status()
        game.interactions()
        game.threats()
        game.cycle_target()
        self.assertEqual(game.turn, 0)
        game.interact(7, 5, "search")
        self.assertEqual(game.inventory["water"], 1)
        self.assertEqual(game.turn, 2)
        game.interact(7, 5, "search")
        self.assertEqual(game.inventory["water"], 1)
        self.assertEqual(game.turn, 2)

    def test_running_crouching_jumping_and_stamina(self):
        game = self.game
        game.x, game.y = 0, 8
        game.move("east", "run")
        self.assertEqual((game.x, game.y), (2, 8))
        self.assertEqual(game.stamina, 94)
        game.move("east", "crouch")
        self.assertEqual((game.x, game.y), (3, 8))
        self.assertEqual(game.turn, 3)
        game.stamina = 0
        game.move("west", "run")
        self.assertEqual(game.x, 3)
        game.wait()
        self.assertEqual(game.stamina, 8)
        game.jump()
        self.assertEqual(game.x, 1)
        self.assertEqual(game.stamina, 3)

    def test_chunks_are_deterministic_and_cache_bounded(self):
        world = self.game.world
        other = World(42)
        self.addCleanup(other.close)
        self.assertEqual(world.chunk(-1, -1), other.chunk(-1, -1))
        world.at(5, 8)[1][0]["opened"] = True
        for cx in range(20):
            world.chunk(cx, 5)
        self.assertLessEqual(len(world.cache), 9)
        self.assertTrue(world.at(5, 8)[1][0]["opened"])

    def test_save_round_trip_after_eviction(self):
        game = self.game
        game.x, game.y = 7, 6
        game.interact(7, 5, "search")
        game.world.at(5, 8)[1][0]["opened"] = True
        for cx in range(20):
            game.world.chunk(cx, 5)
        with tempfile.TemporaryDirectory() as directory:
            manifest = game.save(directory)
            restored = Game.load(manifest)
            self.addCleanup(restored.world.close)
            self.assertEqual(restored.inventory, game.inventory)
            self.assertEqual(restored.turn, game.turn)
            self.assertEqual((restored.x, restored.y), (7, 6))
            self.assertTrue(restored.world.at(5, 8)[1][0]["opened"])
            restored.interact(7, 5, "search")
            self.assertEqual(restored.inventory["water"], 1)
            self.assertEqual(restored.world.chunk(19, 5), game.world.chunk(19, 5))

    def test_failed_checkpoint_preserves_previous_manifest(self):
        game = self.game
        game.world.at(3, 8)
        with tempfile.TemporaryDirectory() as directory:
            manifest = game.save(directory)
            original = manifest.read_bytes()
            with patch.object(game.world, "checkpoint", side_effect=OSError("Disk full")):
                with self.assertRaises(OSError):
                    game.save(directory)
            self.assertEqual(manifest.read_bytes(), original)
            restored = Game.load(manifest)
            restored.world.close()

    def test_combat_death_block_and_cover(self):
        game = self.game
        dog = game.world.chunk(0, 0)["creatures"][0]
        game.x, game.y = 14, 13
        game.block()
        self.assertEqual(game.health, 98)
        game.attack(heavy=True)
        self.assertEqual(dog["health"], 12)
        game.attack()
        self.assertEqual(dog["health"], 0)
        game.health = 0
        before = game.turn
        for action in (game.wait, game.jump, game.attack, game.block, game.reload, game.aim_action):
            action()
        game.move("north")
        self.assertEqual(game.turn, before)

    def test_ranged_shot_cannot_pass_through_walls(self):
        game = self.game
        dog = game.world.chunk(0, 0)["creatures"][0]
        dog["x"], dog["y"] = 14, 8
        game.x, game.y = 11, 8
        game.aiming = True
        game.target = (14, 8)
        game.attack()
        self.assertEqual(game.ammo, 6)
        self.assertEqual(dog["health"], 36)
        self.assertEqual(game.turn, 0)

    def test_data_templates_and_surfaces_are_valid(self):
        for template in WORLD["buildings"].values():
            self.assertEqual(len(template["rows"]), SIZE)
            for row in template["rows"]:
                self.assertEqual(len(row), SIZE)
                self.assertTrue(set(row).issubset(WORLD["tiles"]))


if __name__ == "__main__":
    unittest.main()
