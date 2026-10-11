import tempfile
import unittest

from game.engine import Game
from game.navigation import ObjectTracker


class NavigationTests(unittest.TestCase):
    def setUp(self):
        self.game = Game(42)
        self.addCleanup(self.game.world.close)
        for cy in (-1, 0, 1):
            for cx in (-1, 0, 1):
                self.game.world.chunk(cx, cy)["creatures"].clear()
        self.tracker = ObjectTracker(self.game)

    def choose(self, kind, item_type, x, y):
        self.tracker.select({"kind": kind, "type": item_type, "x": x, "y": y})

    def test_survey_and_tracking_are_free_and_cache_is_bounded(self):
        targets = self.tracker.targets()
        self.assertTrue(any(target["type"] == "cabinet" for target in targets))
        self.choose("object", "cabinet", 7, 5)
        self.tracker.status()
        self.assertIsNotNone(self.tracker.route())
        self.assertEqual(self.game.turn, 0)
        self.assertLessEqual(len(self.game.world.cache), 9)

    def test_route_opens_doors_and_arrives_with_normal_steps(self):
        game = self.game
        self.choose("object", "cabinet", 7, 5)
        opened = False
        step_sounds = 0
        arrived = False
        for _ in range(50):
            before = (game.x, game.y)
            events, keep_walking = self.tracker.step()
            self.assertLessEqual(abs(game.x - before[0]) + abs(game.y - before[1]), 1)
            opened |= any(event.sound == "open" for event in events)
            step_sounds += sum(event.sound == "step" for event in events)
            arrived |= any("Arrived at" in event.text for event in events)
            if not keep_walking:
                break
        self.assertTrue(opened)
        self.assertGreater(step_sounds, 0)
        self.assertTrue(arrived)
        self.assertEqual(self.tracker.distance(game.tracked_object), 1)
        self.assertFalse(game.world.at(7, 5)[1][0]["searched"])
        self.assertGreater(game.turn, step_sounds)

    def test_arrival_at_door_does_not_open_or_step_into_target(self):
        game = self.game
        self.choose("object", "door", 5, 8)
        events, keep_walking = self.tracker.step()
        self.assertFalse(keep_walking)
        self.assertEqual((game.x, game.y), (4, 8))
        self.assertFalse(game.world.at(5, 8)[1][0]["opened"])
        self.assertTrue(any("Arrived at" in event.text for event in events))

    def test_route_crosses_chunks_without_teleporting(self):
        game = self.game
        game.x, game.y = 15, 8
        self.choose("object", "door", 21, 8)
        for _ in range(12):
            _, keep_walking = self.tracker.step()
            if not keep_walking:
                break
        self.assertEqual((game.x, game.y), (20, 8))
        self.assertEqual(game.turn, 5)

    def test_unreachable_target_stops_without_advancing_time(self):
        game = self.game
        self.choose("object", "cabinet", 7, 5)
        chunk = game.world.chunk(0, 0)
        for x, y in ((6, 5), (8, 5), (7, 4), (7, 6)):
            chunk["tiles"][y][x] = "#"
        events, keep_walking = self.tracker.step()
        self.assertFalse(keep_walking)
        self.assertEqual(game.turn, 0)
        self.assertTrue(any("No route" in event.text for event in events))

    def test_danger_stops_before_taking_another_step(self):
        game = self.game
        self.choose("object", "cabinet", 7, 5)
        dog = dict(
            type="dog",
            name="feral dog",
            health=36,
            damage=7,
            x=3,
            y=11,
            surface="grass",
            color="#c78462",
        )
        game.world.chunk(0, 0)["creatures"].append(dog)
        events, keep_walking = self.tracker.step()
        self.assertFalse(keep_walking)
        self.assertEqual((game.x, game.y, game.turn), (3, 8, 0))
        self.assertTrue(any("enemies nearby" in event.text for event in events))

    def test_missing_loose_item_stops_and_tracking_survives_save(self):
        game = self.game
        game.drop_item("ammo", 1)
        self.choose("item", "ammo", 3, 8)
        with tempfile.TemporaryDirectory() as directory:
            restored = Game.load(game.save(directory))
            self.addCleanup(restored.world.close)
            tracker = ObjectTracker(restored)
            self.assertEqual(restored.tracked_object, game.tracked_object)
            restored.pickup(3, 8, "ammo")
            before = restored.turn
            _, keep_walking = tracker.step()
            self.assertFalse(keep_walking)
            self.assertEqual(restored.turn, before)

    def test_movement_omits_direction_announcements_but_keeps_footsteps(self):
        game = self.game
        for mode in ("walk", "run", "crouch", "dodge"):
            game.x, game.y = 1, 8
            events = game.move("east", mode)
            text = " ".join(event.text for event in events)
            self.assertNotIn("east", text.lower())
            self.assertTrue(any(event.sound == "step" for event in events))
            self.assertIn("Position", text)
        self.assertEqual(game.facing, "east")


if __name__ == "__main__":
    unittest.main()
