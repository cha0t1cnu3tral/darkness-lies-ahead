import unittest
from game.engine import Game, World, WORLD, SIZE


class WorldTests(unittest.TestCase):
    def test_generation_is_independent_of_exploration_order(self):
        first, second = World(31415), World(31415)
        self.addCleanup(first.close)
        self.addCleanup(second.close)
        points = [(x, y) for x in range(-4, 4) for y in range(-2, 2)]
        snapshots = {point: first.generate(*point) for point in points}
        for point in reversed(points):
            self.assertEqual(second.chunk(*point), snapshots[point])
        self.assertLessEqual(len(second.cache), 9)

    def test_seed_varies_layouts_but_starter_is_reliable(self):
        first, second = World(1), World(2)
        self.addCleanup(first.close)
        self.addCleanup(second.close)
        self.assertTrue(any(first.generate(x, 4) != second.generate(x, 4) for x in range(15)))
        self.assertEqual(first.chunk(0, 0)["building"], "suburban_house")
        self.assertEqual(first.chunk(1, 0)["building"], "workshop")
        self.assertEqual(first.chunk(0, -1)["building"], "cabin")
        self.assertEqual(first.at(5, 8)[1][0]["type"], "door")

    def test_generated_objects_and_creatures_are_on_valid_tiles_and_edges_connect(self):
        world = World(1234)
        self.addCleanup(world.close)
        for cx in range(-5, 5):
            for cy in range(-5, 5):
                chunk = world.generate(cx, cy)
                for actor in chunk["objects"] + chunk["creatures"]:
                    self.assertTrue(0 <= actor["x"] < SIZE and 0 <= actor["y"] < SIZE)
                    self.assertTrue(
                        WORLD["tiles"][chunk["tiles"][actor["y"]][actor["x"]]]["passable"]
                    )
                for i in range(SIZE):
                    self.assertEqual(chunk["tiles"][0][i], ",")
                    self.assertEqual(chunk["tiles"][-1][i], ",")
                    self.assertEqual(chunk["tiles"][i][0], ",")
                    self.assertEqual(chunk["tiles"][i][-1], ",")

    def test_enemy_crosses_chunk_boundary_without_duplicate_or_respawn(self):
        game = Game(42)
        self.addCleanup(game.world.close)
        for cy in (-1, 0):
            for cx in (0, 1):
                game.world.chunk(cx, cy)["creatures"].clear()
        dog = dict(
            type="dog",
            name="feral dog",
            health=36,
            damage=7,
            x=15,
            y=0,
            surface="grass",
            color="#c78462",
        )
        game.world.chunk(0, 0)["creatures"].append(dog)
        game.x, game.y = 17, 0
        game.target = (15, 0)
        game.advance(1)
        self.assertNotIn(dog, game.world.chunk(0, 0)["creatures"])
        self.assertEqual(game.world.chunk(1, 0)["creatures"].count(dog), 1)
        self.assertEqual(game.target, (16, 0))
        game.advance(2)
        self.assertEqual(game.health, 93)

    def test_long_actions_allow_multiple_enemy_turns(self):
        game = Game(42)
        self.addCleanup(game.world.close)
        game.x, game.y = 14, 13
        game.advance(5)
        self.assertEqual(game.health, 79)


if __name__ == "__main__":
    unittest.main()
