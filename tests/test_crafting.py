import json
import tempfile
import unittest

from game.engine import Game


class CraftingTests(unittest.TestCase):
    def setUp(self):
        self.game = Game(42)
        self.addCleanup(self.game.world.close)
        for cy in (-1, 0, 1):
            for cx in (-1, 0, 1):
                self.game.world.chunk(cx, cy)["creatures"].clear()

    def test_gather_and_dismantle_are_persistent_one_time_sources(self):
        game = self.game
        game.x, game.y = 3, 9
        game.interact(3, 10, "gather")
        self.assertEqual(game.inventory["wood"], 3)
        self.assertEqual(game.inventory["fiber"], 6)
        game.interact(3, 10, "gather")
        self.assertEqual(game.inventory["fiber"], 6)
        game.x, game.y = 7, 9
        game.interact(7, 10, "dismantle")
        self.assertEqual(game.inventory["wood"], 5)
        self.assertEqual(game.inventory["scrap"], 1)

    def test_inspection_and_unavailable_recipes_do_not_consume_time_or_items(self):
        game = self.game
        before = dict(game.inventory)
        self.assertIn("Missing", game.recipe_description("spear"))
        game.start_craft("spear")
        game.start_craft("unknown")
        self.assertEqual(game.turn, 0)
        self.assertEqual(game.inventory, before)
        self.assertIsNone(game.crafting)

    def test_crafting_reserves_materials_and_finishes_in_work_steps(self):
        game = self.game
        game.inventory["fiber"] = 3
        game.start_craft("cordage")
        self.assertEqual(game.inventory["fiber"], 0)
        self.assertNotIn("cordage", game.inventory)
        game.continue_craft()
        self.assertEqual(game.crafting["progress"], 3)
        self.assertNotIn("cordage", game.inventory)
        for _ in range(3):
            game.continue_craft()
        self.assertEqual(game.inventory["cordage"], 1)
        self.assertIsNone(game.crafting)
        self.assertEqual(game.turn, 13)

    def test_cancel_returns_reserved_materials_without_duplicate_output(self):
        game = self.game
        game.inventory["fiber"] = 3
        game.start_craft("cordage")
        game.continue_craft()
        game.cancel_craft()
        game.cancel_craft()
        self.assertEqual(game.inventory["fiber"], 3)
        self.assertNotIn("cordage", game.inventory)
        self.assertEqual(game.turn, 5)

    def test_ground_materials_can_be_used_across_chunk_boundary(self):
        game = self.game
        game.x, game.y = 16, 8
        game.inventory["cloth"] = 2
        game.drop_item("cloth", 2)
        game.x = 15
        self.assertEqual(game.crafting_requirements("bandage"), [])
        game.start_craft("bandage")
        self.assertEqual(game.ground_at(16, 8), [])
        game.continue_craft()
        game.continue_craft()
        self.assertEqual(game.inventory["bandage"], 1)
        self.assertEqual(game.inventory["cloth"], 0)

    def test_tool_and_workbench_required_when_starting_and_resuming(self):
        game = self.game
        game.inventory.update(wood=1, cloth=1, cordage=1)
        game.start_craft("splint")
        self.assertIsNone(game.crafting)
        game.x, game.y = 24, 7
        game.start_craft("splint")
        self.assertIsNotNone(game.crafting)
        game.x, game.y = 3, 8
        before = game.turn
        game.continue_craft()
        self.assertEqual(game.crafting["progress"], 0)
        self.assertEqual(game.turn, before)
        game.x, game.y = 24, 7
        game.drop_item("knife")
        before = game.turn
        game.continue_craft()
        self.assertEqual(game.turn, before)
        game.pickup(24, 7, "knife")
        game.continue_craft()
        self.assertEqual(game.crafting["progress"], 3)

    def test_drop_pickup_and_pistol_rounds_are_conserved(self):
        game = self.game
        total = game.ammo + game.inventory["ammo"]
        game.drop_item("pistol")
        self.assertEqual(game.ammo, 0)
        self.assertEqual(game.inventory["ammo"], total)
        self.assertFalse(game.aiming)
        game.aim_action()
        self.assertFalse(game.aiming)
        game.pickup(3, 8, "pistol")
        game.reload()
        self.assertEqual(game.inventory["pistol"], 1)
        self.assertEqual(game.ammo + game.inventory["ammo"], total)
        game.pickup(3, 8, "pistol")
        self.assertEqual(game.inventory["pistol"], 1)
        game.drop_item("knife")
        self.assertEqual(game.melee()["name"], "bare hands")

    def test_dropped_ground_items_and_partial_projects_survive_save_and_eviction(self):
        game = self.game
        game.inventory.update(fiber=3, cloth=2)
        game.drop_item("cloth", 2)
        game.start_craft("cordage")
        game.continue_craft()
        for cx in range(20):
            game.world.chunk(cx, 5)
        with tempfile.TemporaryDirectory() as directory:
            path = game.save(directory)
            restored = Game.load(path)
            self.addCleanup(restored.world.close)
            self.assertEqual(restored.crafting["progress"], 3)
            self.assertEqual(restored.ground_at(3, 8)[0]["count"], 2)
            restored.cancel_craft()
            self.assertEqual(restored.inventory["fiber"], 3)
            restored.pickup(3, 8, "cloth")
            self.assertEqual(restored.inventory["cloth"], 2)

    def test_version_one_saves_load_without_regenerating_visited_chunks(self):
        game = self.game
        game.world.at(5, 8)[1][0]["opened"] = True
        with tempfile.TemporaryDirectory() as directory:
            path = game.save(directory)
            state = json.loads(path.read_text())
            state["version"] = 1
            state.pop("melee_weapon")
            state.pop("crafting")
            chunk_path = path.parent / "chunks" / state["chunks"]["0,0"]
            chunk = json.loads(chunk_path.read_text())
            chunk.pop("building")
            chunk.pop("ground")
            chunk_path.write_text(json.dumps(chunk))
            path.write_text(json.dumps(state))
            restored = Game.load(path)
            self.addCleanup(restored.world.close)
            self.assertTrue(restored.world.at(5, 8)[1][0]["opened"])
            self.assertEqual(restored.melee_weapon, "knife")
            self.assertIsNone(restored.crafting)
            self.assertEqual(restored.world.chunk(0, 0)["building"], "suburban_house")

    def test_closed_door_blocks_access_to_ground_materials(self):
        game = self.game
        game.x, game.y = 5, 8
        game.inventory["cloth"] = 2
        game.world.at(5, 8)[1][0]["opened"] = True
        game.drop_item("cloth", 2)
        game.x = 4
        game.interact(5, 8, "close")
        self.assertIn("2 clean cloth", game.crafting_requirements("bandage"))
        game.pickup(5, 8, "cloth")
        self.assertEqual(game.inventory["cloth"], 0)

    def test_equipped_spear_has_reach_and_cannot_attack_through_cover(self):
        game = self.game
        game.inventory["spear"] = 1
        game.x, game.y = 14, 12
        game.equip("spear")
        dog = dict(
            type="dog",
            name="feral dog",
            health=36,
            damage=7,
            x=14,
            y=14,
            surface="grass",
            color="#c78462",
        )
        game.world.chunk(0, 0)["creatures"].append(dog)
        game.target = (14, 14)
        game.attack()
        self.assertEqual(dog["health"], 20)
        self.assertEqual(game.melee()["reach"], 2)
        dog["x"], dog["y"] = 14, 8
        game.x, game.y = 12, 8
        game.target = (14, 8)
        game.attack()
        self.assertEqual(dog["health"], 20)


if __name__ == "__main__":
    unittest.main()
