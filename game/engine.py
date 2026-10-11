"""UI-free, deterministic turn simulation and bounded chunk storage."""

from collections import OrderedDict
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import random
import tempfile
import uuid

from .paths import DATA

WORLD = json.loads((DATA / "world.json").read_text(encoding="utf-8"))
ITEMS = json.loads((DATA / "items.json").read_text(encoding="utf-8"))
CREATURES = json.loads((DATA / "creatures.json").read_text(encoding="utf-8"))
RECIPES = json.loads((DATA / "recipes.json").read_text(encoding="utf-8"))
SIZE = WORLD["chunk_size"]
DIRECTIONS = {"north": (0, -1), "south": (0, 1), "west": (-1, 0), "east": (1, 0)}


@dataclass
class Event:
    text: str
    sound: str = ""
    surface: str = ""
    x: int | None = None
    y: int | None = None


class World:
    """Keep nine detailed chunks; evicted changes go to an independent disk file."""

    def __init__(self, seed, references=None):
        self.seed = seed
        self.cache = OrderedDict()
        self.references = dict(references or {})
        self.session = tempfile.TemporaryDirectory(prefix="dla-world-")

    def generate(self, cx, cy):
        rng = random.Random(f"{self.seed}:{cx}:{cy}")
        building = WORLD["starting_buildings"].get(f"{cx},{cy}")
        if not building and rng.random() < WORLD["building_chance"]:
            building = rng.choice(list(WORLD["buildings"]))
        if building:
            template = WORLD["buildings"][building]
            rows = template["rows"]
            objects = [dict(o, opened=False, searched=False) for o in template["objects"]]
            if (cx, cy) != (0, 0):
                objects = [o for o in objects if o["type"] != "scavenger"]
            tiles = [list(row) for row in rows]
            if f"{cx},{cy}" not in WORLD["starting_buildings"]:
                # Rotate and mirror entire templates, including doors and their paths.
                turns = rng.randrange(4)
                mirror = rng.choice((True, False))
                for _ in range(turns):
                    tiles = [list(row) for row in zip(*tiles[::-1])]
                    for obj in objects:
                        obj["x"], obj["y"] = SIZE - 1 - obj["y"], obj["x"]
                if mirror:
                    tiles = [row[::-1] for row in tiles]
                    for obj in objects:
                        obj["x"] = SIZE - 1 - obj["x"]
        else:
            tiles = [
                [
                    ","
                    if y == 8
                    else ("T" if rng.random() < WORLD["generation"]["tree_chance"] else ".")
                    for x in range(SIZE)
                ]
                for y in range(SIZE)
            ]
            objects = []
        # Shared clear borders connect adjacent chunks into continuous streets.
        for coordinate in range(SIZE):
            for x, y in (
                (coordinate, 0),
                (coordinate, SIZE - 1),
                (0, coordinate),
                (SIZE - 1, coordinate),
            ):
                tiles[y][x] = ","
        occupied = {(obj["x"], obj["y"]) for obj in objects}
        outdoor = [
            (x, y)
            for y in range(1, SIZE - 1)
            for x in range(1, SIZE - 1)
            if tiles[y][x] == "." and (x, y) not in occupied
        ]
        rng.shuffle(outdoor)
        for _ in range(
            rng.randint(WORLD["generation"]["brush_min"], WORLD["generation"]["brush_max"])
        ):
            if outdoor:
                x, y = outdoor.pop()
                objects.append(
                    {"type": "brush", "x": x, "y": y, "opened": False, "searched": False}
                )
        creatures = []
        if (cx, cy) == (0, 0) or rng.random() < WORLD["generation"]["encounter_chance"]:
            x, y = (14, 14) if (cx, cy) == (0, 0) else rng.choice(outdoor or [(0, 0)])
            creatures.append(dict(CREATURES["dog"], type="dog", x=x, y=y, blocking=False))
        return {
            "cx": cx,
            "cy": cy,
            "tiles": tiles,
            "objects": objects,
            "creatures": creatures,
            "last_turn": 0,
            "building": building,
            "ground": [],
        }

    def chunk(self, cx, cy):
        key = f"{cx},{cy}"
        if key not in self.cache:
            reference = self.references.get(key)
            self.cache[key] = (
                json.loads(Path(reference).read_text(encoding="utf-8"))
                if reference
                else self.generate(cx, cy)
            )
        self.cache.move_to_end(key)
        chunk = self.cache[key]
        chunk.setdefault("ground", [])
        if "building" not in chunk:
            # Version 1 only had one building type; do not regenerate visited tiles.
            chunk["building"] = (
                "suburban_house"
                if any(
                    WORLD["tiles"][symbol].get("indoors")
                    for row in chunk["tiles"]
                    for symbol in row
                )
                else None
            )
        while len(self.cache) > 9:
            old_key, old = self.cache.popitem(last=False)
            path = Path(self.session.name) / (old_key + ".json")
            path.write_text(json.dumps(old), encoding="utf-8")
            self.references[old_key] = str(path)
        return self.cache[key]

    def at(self, x, y):
        chunk = self.chunk(x // SIZE, y // SIZE)
        tile = WORLD["tiles"][chunk["tiles"][y % SIZE][x % SIZE]]
        objects = [o for o in chunk["objects"] if (o["x"], o["y"]) == (x % SIZE, y % SIZE)]
        return tile, objects

    def blocked(self, x, y, creatures=True):
        tile, objects = self.at(x, y)
        if not tile["passable"]:
            return True
        if any(WORLD["objects"][o["type"]]["blocking"] and not o.get("opened") for o in objects):
            return True
        return creatures and any(
            c["health"] > 0 and (c["x"], c["y"]) == (x % SIZE, y % SIZE)
            for c in self.chunk(x // SIZE, y // SIZE)["creatures"]
        )

    def checkpoint(self, directory):
        directory.mkdir(parents=True, exist_ok=True)
        refs = {}
        for key in sorted(set(self.references) | set(self.cache)):
            value = self.cache.get(key)
            if value is None:
                value = json.loads(Path(self.references[key]).read_text(encoding="utf-8"))
            payload = json.dumps(value, sort_keys=True).encode("utf-8")
            digest = hashlib.sha256(payload).hexdigest()[:20]
            path = directory / (key + "-" + digest + ".json")
            if not path.exists():
                temporary = path.with_suffix(".tmp")
                temporary.write_bytes(payload)
                temporary.replace(path)
            refs[key] = path.name
        return refs

    def close(self):
        self.session.cleanup()


class Game:
    def __init__(self, seed=1, world=None):
        self.seed = seed
        self.world = world or World(seed)
        self.x, self.y = 3, 8
        self.facing = "east"
        self.turn = 0
        self.health = 100
        self.stamina = 100
        self.inventory = {"knife": 1, "pistol": 1, "ammo": 12}
        self.ammo = 6
        self.aiming = False
        self.aim = 0
        self.blocking = False
        self.target = None
        self.slot = uuid.uuid4().hex
        self.name = "Survivor"
        self.melee_weapon = "knife"
        self.crafting = None

    def ground_at(self, x, y):
        return [
            pile
            for pile in self.world.chunk(x // SIZE, y // SIZE)["ground"]
            if (pile["x"], pile["y"]) == (x % SIZE, y % SIZE) and pile["count"] > 0
        ]

    def nearby_ground(self):
        result = []
        for x, y in [(self.x, self.y)] + [
            (self.x + dx, self.y + dy) for dx, dy in DIRECTIONS.values()
        ]:
            if self.world.blocked(x, y, creatures=False):
                continue
            result.extend((pile, x, y) for pile in self.ground_at(x, y))
        return result

    def drop_item(self, item, count=1):
        if (
            self.health <= 0
            or type(count) is not int
            or count < 1
            or self.inventory.get(item, 0) < count
        ):
            return [Event("You cannot drop that quantity.")]
        self.inventory[item] -= count
        unloaded = ""
        if item == "pistol" and not self.inventory[item]:
            self.inventory["ammo"] = self.inventory.get("ammo", 0) + self.ammo
            self.ammo = 0
            self.aiming = False
            unloaded = " Loaded rounds returned to your inventory."
        if item == self.melee_weapon and not self.inventory[item]:
            self.melee_weapon = None
        piles = self.world.chunk(self.x // SIZE, self.y // SIZE)["ground"]
        pile = next(
            (
                p
                for p in piles
                if p["item"] == item and (p["x"], p["y"]) == (self.x % SIZE, self.y % SIZE)
            ),
            None,
        )
        if pile:
            pile["count"] += count
        else:
            piles.append({"item": item, "count": count, "x": self.x % SIZE, "y": self.y % SIZE})
        return [
            Event(f"You put down {count} {ITEMS[item]['name']}." + unloaded, "drop")
        ] + self.advance(1)

    def pickup(self, x, y, item):
        if self.health <= 0:
            return [Event("You cannot gather items after death.")]
        pile = next(
            (p for p, px, py in self.nearby_ground() if (px, py) == (x, y) and p["item"] == item),
            None,
        )
        if not pile:
            return [Event("That item is out of reach or no longer there.")]
        count = pile["count"]
        self.inventory[item] = self.inventory.get(item, 0) + count
        pile["count"] = 0
        return [
            Event(f"You pick up {count} {ITEMS[item]['name']}.", "pickup", x=x, y=y)
        ] + self.advance(1)

    def equip(self, item):
        if (
            self.health <= 0
            or not self.inventory.get(item)
            or ITEMS.get(item, {}).get("weapon") != "melee"
        ):
            return [Event("You cannot equip that weapon.")]
        self.melee_weapon = item
        self.aiming = False
        self.aim = 0
        return [
            Event(
                f"You ready your {ITEMS[item]['name']}. Reach {ITEMS[item]['reach']} tiles.",
                "equip",
            )
        ] + self.advance(1)

    def melee(self):
        if self.melee_weapon and self.inventory.get(self.melee_weapon):
            return ITEMS[self.melee_weapon]
        return {"name": "bare hands", "damage": 4, "reach": 1}

    def crafting_requirements(self, recipe):
        definition = RECIPES[recipe]
        available = dict(self.inventory)
        for pile, x, y in self.nearby_ground():
            available[pile["item"]] = available.get(pile["item"], 0) + pile["count"]
        missing = [
            f"{quantity - available.get(item, 0)} {ITEMS[item]['name']}"
            for item, quantity in definition["materials"].items()
            if available.get(item, 0) < quantity
        ]
        return missing + self.crafting_environment_requirements(recipe)

    def crafting_environment_requirements(self, recipe):
        definition = RECIPES[recipe]
        missing = []
        for tool in definition["tools"]:
            if not any(
                count > 0 and ITEMS[item].get("tool") == tool
                for item, count in self.inventory.items()
            ):
                missing.append(tool + " tool")
        station = definition.get("workstation")
        if station and not any(
            WORLD["objects"][obj["type"]].get("station") == station
            for x, y in [(self.x, self.y)]
            + [(self.x + dx, self.y + dy) for dx, dy in DIRECTIONS.values()]
            for obj in self.world.at(x, y)[1]
        ):
            missing.append("nearby " + station)
        return missing

    def recipe_description(self, recipe):
        definition = RECIPES[recipe]
        materials = ", ".join(
            f"{count} {ITEMS[item]['name']}" for item, count in definition["materials"].items()
        )
        missing = self.crafting_requirements(recipe)
        return (
            f"{definition['category']}: {definition['name']}. Requires {materials}. Tools: {', '.join(definition['tools']) or 'none'}. Workstation: {definition.get('workstation', 'none')}. Work time {definition['seconds']} seconds. "
            + ("Missing: " + ", ".join(missing) + "." if missing else "Ready to begin.")
        )

    def start_craft(self, recipe):
        if self.health <= 0:
            return [Event("You cannot craft after death.")]
        if self.crafting:
            return [Event("Finish or cancel your current project first.")]
        if recipe not in RECIPES:
            return [Event("Unknown recipe.")]
        missing = self.crafting_requirements(recipe)
        if missing:
            return [Event("Cannot craft. Missing: " + ", ".join(missing) + ".")]
        materials = RECIPES[recipe]["materials"]
        sources = self.nearby_ground()
        for item, quantity in materials.items():
            from_inventory = min(quantity, self.inventory.get(item, 0))
            self.inventory[item] = self.inventory.get(item, 0) - from_inventory
            remaining = quantity - from_inventory
            for pile, x, y in sources:
                if pile["item"] == item:
                    taken = min(remaining, pile["count"])
                    pile["count"] -= taken
                    remaining -= taken
        self.crafting = {"recipe": recipe, "progress": 0, "reserved": dict(materials)}
        return [
            Event(
                f"You begin {RECIPES[recipe]['name']}. Materials reserved. Press C to continue or cancel.",
                "search",
            )
        ] + self.advance(1)

    def continue_craft(self):
        if self.health <= 0 or not self.crafting:
            return [Event("No crafting project you can work on.")]
        recipe = RECIPES[self.crafting["recipe"]]
        # Materials are already reserved; only tools and workstation remain required.
        missing = self.crafting_environment_requirements(self.crafting["recipe"])
        if missing:
            return [Event("Project paused. Missing: " + ", ".join(missing) + ".")]
        seconds = min(3, recipe["seconds"] - self.crafting["progress"])
        self.crafting["progress"] += seconds
        finished = self.crafting["progress"] >= recipe["seconds"]
        if finished:
            for item, count in recipe["output"].items():
                self.inventory[item] = self.inventory.get(item, 0) + count
            self.crafting = None
            message = f"Finished {recipe['name']}. Added to inventory."
        else:
            message = f"Working on {recipe['name']}. {self.crafting['progress']} of {recipe['seconds']} seconds complete."
        return [Event(message, recipe["sound"])] + self.advance(seconds)

    def cancel_craft(self):
        if self.health <= 0 or not self.crafting:
            return [Event("No crafting project you can cancel.")]
        for item, count in self.crafting["reserved"].items():
            self.inventory[item] = self.inventory.get(item, 0) + count
        self.crafting = None
        return [
            Event("Project cancelled. Reserved materials returned to inventory.", "pickup")
        ] + self.advance(1)

    def describe(self):
        tile, objects = self.world.at(self.x, self.y)
        names = [WORLD["objects"][o["type"]]["name"] for o in objects]
        chunk = self.world.chunk(self.x // SIZE, self.y // SIZE)
        building = chunk["building"]
        region = (
            "Inside " + WORLD["buildings"][building]["name"]
            if building and tile.get("indoors")
            else "Outside in the overgrown suburb"
        )
        ground = self.ground_at(self.x, self.y)
        names.extend(
            f"{pile['count']} {ITEMS[pile['item']]['name']} on the ground" for pile in ground
        )
        return f"{region}. {tile['name']}. Position {self.x}, {self.y}." + (
            " Here: " + ", ".join(names) + "." if names else ""
        )

    def status(self):
        project = ""
        if self.crafting:
            recipe = RECIPES[self.crafting["recipe"]]
            project = f" Crafting {recipe['name']}, {self.crafting['progress']} of {recipe['seconds']} seconds."
        return (
            f"Health {self.health} of 100. Stamina {self.stamina} of 100. Time {self.turn} seconds. Facing {self.facing}. {'Aiming pistol' if self.aiming else self.melee()['name'] + ' ready'}. Pistol {self.ammo} rounds loaded. World seed {self.seed}."
            + project
        )

    def nearby(self):
        result = []
        for direction, (dx, dy) in DIRECTIONS.items():
            tile, objects = self.world.at(self.x + dx, self.y + dy)
            names = [
                WORLD["objects"][o["type"]]["name"] + (", open" if o.get("opened") else "")
                for o in objects
            ]
            names.extend(
                f"{pile['count']} {ITEMS[pile['item']]['name']} on the ground"
                for pile in self.ground_at(self.x + dx, self.y + dy)
            )
            result.append(direction + ": " + ", ".join(names or [tile["name"]]))
        return ". ".join(result) + "."

    def threats(self):
        result = []
        for cy in range((self.y - 8) // SIZE, (self.y + 8) // SIZE + 1):
            for cx in range((self.x - 8) // SIZE, (self.x + 8) // SIZE + 1):
                chunk = self.world.chunk(cx, cy)
                for c in chunk["creatures"]:
                    x, y = cx * SIZE + c["x"], cy * SIZE + c["y"]
                    distance = abs(x - self.x) + abs(y - self.y)
                    if c["health"] > 0 and distance <= 8:
                        result.append((c, x, y, distance))
        return sorted(result, key=lambda entry: entry[3])

    def cycle_target(self):
        threats = self.threats()
        if not threats:
            self.target = None
            return [Event("No nearby enemies.")]
        identities = [(x, y) for _, x, y, _ in threats]
        index = (
            (identities.index(tuple(self.target)) + 1) % len(threats)
            if self.target and tuple(self.target) in identities
            else 0
        )
        c, x, y, distance = threats[index]
        self.target = (x, y)
        return [
            Event(
                f"Target: {c['name']}, {distance} tiles away, {c['health']} health. {self.relative(x, y)}.",
                "target",
                x=x,
                y=y,
            )
        ]

    def relative(self, x, y):
        parts = []
        if y != self.y:
            parts.append(f"{abs(y - self.y)} {'north' if y < self.y else 'south'}")
        if x != self.x:
            parts.append(f"{abs(x - self.x)} {'west' if x < self.x else 'east'}")
        return ", ".join(parts) or "on your tile"

    def advance(self, seconds, quiet=False):
        first_tick = self.turn + 1
        self.turn += seconds
        events = []
        # Detailed behavior only runs nearby. Time spent on longer actions gives
        # enemies more opportunities, while distant actors receive no catch-up burst.
        for tick in range(first_tick, self.turn + 1):
            events.extend(self.enemy_turn(tick, quiet))
            if self.health == 0:
                break
        self.blocking = False
        if self.health == 0:
            events.append(Event("You have died. Press Escape for the main menu."))
        return events

    def enemy_turn(self, tick, quiet=False):
        events = []
        for c, x, y, distance in self.threats():
            if distance > (3 if quiet else CREATURES[c["type"]]["awareness"]):
                c["next_action"] = tick + 1
                continue
            if tick < c.get("next_action", tick):
                continue
            c["next_action"] = tick + CREATURES[c["type"]]["action_seconds"]
            chunk = self.world.chunk(x // SIZE, y // SIZE)
            chunk["last_turn"] = tick
            if distance == 1:
                damage = max(1, c["damage"] // 3) if self.blocking else c["damage"]
                self.health = max(0, self.health - damage)
                events.append(
                    Event(
                        f"{c['name']} bites you for {damage} damage. Health {self.health}.",
                        "hurt",
                        x=x,
                        y=y,
                    )
                )
            else:
                choices = [(x + (1 if self.x > x else -1), y)] if x != self.x else []
                if y != self.y:
                    choices.append((x, y + (1 if self.y > y else -1)))
                for nx, ny in choices:
                    if not self.world.blocked(nx, ny) and (nx, ny) != (self.x, self.y):
                        if (nx // SIZE, ny // SIZE) != (x // SIZE, y // SIZE):
                            destination = self.world.chunk(nx // SIZE, ny // SIZE)
                            chunk["creatures"].remove(c)
                            destination["creatures"].append(c)
                            destination["last_turn"] = tick
                        c["x"], c["y"] = nx % SIZE, ny % SIZE
                        if self.target == (x, y):
                            self.target = (nx, ny)
                        events.append(
                            Event(
                                f"{c['name']} moves: {self.relative(nx, ny)}.",
                                "enemy_step",
                                surface=self.world.at(nx, ny)[0]["surface"],
                                x=nx,
                                y=ny,
                            )
                        )
                        break
            if self.health == 0:
                break
        return events

    def move(self, direction, mode="walk"):
        if self.health <= 0:
            return [Event("You cannot move. Press Escape for the main menu.")]
        self.facing = direction
        self.aim = 0
        dx, dy = DIRECTIONS[direction]
        steps = 2 if mode == "run" else 1
        cost = 6 if mode == "run" else 4 if mode == "dodge" else 0
        if self.stamina < cost:
            return [Event("Not enough stamina. Press period to rest.", "blocked")]
        events = []
        moved = False
        for _ in range(steps):
            nx, ny = self.x + dx, self.y + dy
            tile, objects = self.world.at(nx, ny)
            door = next((o for o in objects if o["type"] == "door" and not o["opened"]), None)
            if door:
                events += self.interact(nx, ny, "open")
                break
            if self.world.blocked(nx, ny):
                events.append(
                    Event(
                        f"{direction}: blocked by "
                        + (
                            WORLD["objects"][objects[0]["type"]]["name"]
                            if objects
                            else tile["name"]
                        )
                        + ".",
                        "blocked",
                    )
                )
                break
            self.x, self.y = nx, ny
            moved = True
            events.append(
                Event(f"{mode.capitalize()} {direction}. {tile['name']}.", "step", tile["surface"])
            )
        if moved:
            self.stamina = min(100, self.stamina - cost + (1 if mode == "walk" else 0))
            events.append(Event(self.describe()))
            events += self.advance(2 if mode == "crouch" else 1, mode == "crouch")
        return events

    def interactions(self):
        points = [(self.x, self.y)] + [(self.x + dx, self.y + dy) for dx, dy in DIRECTIONS.values()]
        choices = []
        for x, y in points:
            _, objects = self.world.at(x, y)
            for obj in objects:
                definition = WORLD["objects"][obj["type"]]
                for action in definition["actions"]:
                    if obj["type"] == "door" and ((action == "open") == obj["opened"]):
                        continue
                    choices.append(
                        (
                            f"{action.capitalize()} {definition['name']}, {self.relative(x, y)}",
                            x,
                            y,
                            action,
                        )
                    )
        return choices

    def interact(self, x, y, action):
        if self.health <= 0:
            return [Event("You cannot act after death.")]
        if abs(x - self.x) + abs(y - self.y) > 1:
            return [Event("Move beside the object first.")]
        _, objects = self.world.at(x, y)
        obj = next((o for o in objects if action in WORLD["objects"][o["type"]]["actions"]), None)
        if not obj:
            return [Event("That action is unavailable.")]
        definition = WORLD["objects"][obj["type"]]
        if action in ("open", "close"):
            if action == "close" and (x, y) == (self.x, self.y):
                return [Event("Step off the doorway before closing it.")]
            obj["opened"] = action == "open"
            event = Event(f"You {action} the {definition['name']}.", action, x=x, y=y)
        elif action in ("search", "gather", "dismantle"):
            if obj["searched"]:
                return [Event("Already searched. Nothing remains.")]
            obj["searched"] = True
            for item in definition["loot"]:
                self.inventory[item] = self.inventory.get(item, 0) + 1
            event = Event(
                "You find "
                + ", ".join(ITEMS[i]["name"] for i in definition["loot"])
                + ". Added to inventory.",
                definition.get("sound", "search"),
                x=x,
                y=y,
            )
        elif action == "inspect":
            return [Event(definition["description"])]
        else:
            event = Event(definition["dialogue"], "talk", x=x, y=y)
        return [event] + self.advance(2)

    def wait(self):
        if self.health <= 0:
            return [Event("You cannot rest after death.")]
        self.stamina = min(100, self.stamina + 8)
        return [Event(f"You rest. Stamina {self.stamina}.", "rest")] + self.advance(2)

    def jump(self):
        if self.health <= 0 or self.stamina < 5:
            return [Event("You cannot jump. Check your health and stamina.")]
        dx, dy = DIRECTIONS[self.facing]
        for step in (1, 2):
            if self.world.blocked(self.x + dx * step, self.y + dy * step):
                return [Event("Jump blocked. You need two clear tiles ahead.", "blocked")]
        self.x += dx * 2
        self.y += dy * 2
        self.stamina -= 5
        tile, _ = self.world.at(self.x, self.y)
        return [
            Event(
                "You jump two tiles " + self.facing + ". " + self.describe(),
                "land",
                tile["surface"],
            )
        ] + self.advance(2)

    def attack(self, heavy=False):
        if self.health <= 0:
            return [Event("You cannot attack after death.")]
        threats = self.threats()
        target = next(
            (t for t in threats if self.target and (t[1], t[2]) == tuple(self.target)),
            threats[0] if threats else None,
        )
        if not target:
            return [Event("No nearby target.")]
        c, x, y, distance = target
        if self.aiming:
            if not self.ammo:
                return [Event("Pistol empty. Press R to reload.", "blocked")]
            # Cover blocks shooting; accuracy increases through deliberate aiming.
            count = max(abs(x - self.x), abs(y - self.y))
            if any(
                self.world.blocked(
                    round(self.x + (x - self.x) * s / count),
                    round(self.y + (y - self.y) * s / count),
                    False,
                )
                for s in range(1, count)
            ):
                return [Event("Your line of fire is blocked by cover.")]
            self.ammo -= 1
            rng = random.Random(f"{self.seed}:{self.turn}:{self.ammo}")
            damage = (
                ITEMS["pistol"]["damage"]
                if rng.random() < min(0.95, 0.9 - distance * 0.06 + self.aim * 0.1)
                else 0
            )
            sound = "fire"
        else:
            weapon = self.melee()
            if distance > weapon["reach"]:
                return [Event(f"Target is beyond your {weapon['name']}'s reach.")]
            count = max(abs(x - self.x), abs(y - self.y))
            if any(
                self.world.blocked(
                    round(self.x + (x - self.x) * s / count),
                    round(self.y + (y - self.y) * s / count),
                    False,
                )
                for s in range(1, count)
            ):
                return [Event("Your melee attack is blocked by an obstacle.")]
            cost = 10 if heavy else 3
            if self.stamina < cost:
                return [Event("Not enough stamina to attack.")]
            self.stamina -= cost
            damage = weapon["damage"] * (2 if heavy else 1)
            sound = "attack"
        c["health"] = max(0, c["health"] - damage)
        message = (
            f"You hit {c['name']} for {damage} damage. Health {c['health']}."
            if damage
            else f"Your shot misses {c['name']}."
        )
        if c["health"] == 0:
            message += " It falls dead."
            self.target = None
        self.aim = 0
        return [Event(message, sound, x=x, y=y)] + self.advance(2 if heavy else 1)

    def block(self):
        if self.health <= 0:
            return [Event("You cannot block after death.")]
        self.blocking = True
        return [Event("You brace to block incoming attacks.", "block")] + self.advance(1)

    def aim_action(self):
        if self.health <= 0:
            return [Event("You cannot aim after death.")]
        if not self.aiming:
            if not self.inventory.get("pistol"):
                return [Event("You do not have a pistol.")]
            self.aiming = True
            return [
                Event(
                    "Aiming pistol. Tab selects a target; A steadies aim; F fires; R reloads; V readies your knife."
                )
            ]
        self.aim = min(3, self.aim + 1)
        return [Event(f"You steady your aim. Aim level {self.aim}.")] + self.advance(1)

    def reload(self):
        if self.health <= 0:
            return [Event("You cannot reload after death.")]
        if not self.inventory.get("pistol"):
            return [Event("You do not have a pistol.")]
        available = self.inventory.get("ammo", 0)
        count = min(6 - self.ammo, available)
        if count == 0:
            return [Event("Magazine full or no spare cartridges.")]
        self.inventory["ammo"] -= count
        self.ammo += count
        return [Event(f"Reloaded {count} rounds. {self.ammo} loaded.", "reload")] + self.advance(2)

    def use_item(self, item):
        if self.health <= 0 or not self.inventory.get(item):
            return [Event("Item cannot be used.")]
        definition = ITEMS[item]
        if not definition["action"]:
            return [Event("This item has no usable action yet.")]
        self.inventory[item] -= 1
        self.health = min(100, self.health + definition.get("health", 0))
        self.stamina = min(100, self.stamina + definition.get("stamina", 0))
        return [
            Event(f"You {definition['action']} the {definition['name']}. " + self.status(), "use")
        ] + self.advance(2)

    def save(self, directory):
        slot = Path(directory) / self.slot
        slot.mkdir(parents=True, exist_ok=True)
        references = self.world.checkpoint(slot / "chunks")
        state = {k: v for k, v in self.__dict__.items() if k != "world"}
        state.update(version=2, chunks=references)
        temporary = slot / "manifest.tmp"
        temporary.write_text(json.dumps(state, indent=2), encoding="utf-8")
        temporary.replace(slot / "manifest.json")
        # Old chunk revisions are retained so failed writes cannot destroy a save.
        return slot / "manifest.json"

    @classmethod
    def load(cls, manifest):
        path = Path(manifest)
        state = json.loads(path.read_text(encoding="utf-8"))
        if state.pop("version") not in (1, 2):
            raise ValueError("Unsupported save version")
        references = {k: str(path.parent / "chunks" / v) for k, v in state.pop("chunks").items()}
        world = World(state["seed"], references)
        game = cls(state["seed"], world)
        game.__dict__.update(state)
        if game.target:
            game.target = tuple(game.target)
        world.at(game.x, game.y)  # Verify current chunk before replacing a live game.
        return game
