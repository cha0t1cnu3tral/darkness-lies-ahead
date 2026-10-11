"""Bounded object survey and tile-by-tile routing through the shared engine."""

import heapq

from .engine import DIRECTIONS, Event, ITEMS, SIZE, WORLD


class ObjectTracker:
    def __init__(self, game):
        self.game = game

    def targets(self):
        game = self.game
        targets = []
        cx, cy = game.x // SIZE, game.y // SIZE
        # Survey at most nine chunks; never search or simulate the entire world.
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                chunk = game.world.chunk(cx + dx, cy + dy)
                for obj in chunk["objects"]:
                    x, y = (cx + dx) * SIZE + obj["x"], (cy + dy) * SIZE + obj["y"]
                    targets.append({"kind": "object", "type": obj["type"], "x": x, "y": y})
                for pile in chunk["ground"]:
                    if pile["count"] > 0:
                        x, y = (cx + dx) * SIZE + pile["x"], (cy + dy) * SIZE + pile["y"]
                        targets.append({"kind": "item", "type": pile["item"], "x": x, "y": y})
        return sorted(targets, key=lambda t: (self.distance(t), self.name(t), t["y"], t["x"]))

    def name(self, target):
        definitions = WORLD["objects"] if target["kind"] == "object" else ITEMS
        return definitions[target["type"]]["name"]

    def category(self, target):
        definitions = WORLD["objects"] if target["kind"] == "object" else ITEMS
        return definitions[target["type"]].get("category", "Other objects")

    def grouped_targets(self):
        groups = {}
        for target in self.targets():
            groups.setdefault(self.category(target), []).append(target)
        order = WORLD["tracker_categories"]
        names = [name for name in order if name in groups]
        names.extend(sorted(set(groups) - set(names)))
        return {name: groups[name] for name in names}

    def cycle_object(self, offset):
        groups = self.grouped_targets()
        if not groups:
            return [Event("No nearby objects to track.")]
        category = self.game.tracker_category
        if category not in groups:
            category = next(iter(groups))
        targets = groups[category]
        current = self.game.tracked_object
        index = (
            (targets.index(current) + offset) % len(targets)
            if current in targets
            else (0 if offset > 0 else len(targets) - 1)
        )
        return self.browse_select(targets[index], index, len(targets))

    def cycle_category(self, offset):
        groups = self.grouped_targets()
        if not groups:
            return [Event("No nearby object categories.")]
        names = list(groups)
        current = self.game.tracker_category
        index = (
            (names.index(current) + offset) % len(names)
            if current in names
            else (0 if offset > 0 else len(names) - 1)
        )
        targets = groups[names[index]]
        return self.browse_select(targets[0], 0, len(targets))

    def browse_select(self, target, index, total):
        self.select(target)
        return [
            Event(
                f"{self.category(target)}. Object {index + 1} of {total}. "
                + self.description(target, include_help=False),
                "target",
                x=target["x"],
                y=target["y"],
            )
        ]

    def distance(self, target):
        return abs(target["x"] - self.game.x) + abs(target["y"] - self.game.y)

    def exists(self, target):
        if target["kind"] == "object":
            return any(
                obj["type"] == target["type"]
                for obj in self.game.world.at(target["x"], target["y"])[1]
            )
        return any(
            pile["item"] == target["type"] for pile in self.game.ground_at(target["x"], target["y"])
        )

    def description(self, target, include_help=True):
        text = f"{self.name(target)}. {self.distance(target)} tiles away, {self.game.relative(target['x'], target['y'])}."
        if target["kind"] == "object":
            obj = next(
                (
                    obj
                    for obj in self.game.world.at(target["x"], target["y"])[1]
                    if obj["type"] == target["type"]
                ),
                None,
            )
            if obj:
                if obj["type"] == "door":
                    text += " Open." if obj["opened"] else " Closed."
                elif obj.get("searched"):
                    text += " Already searched or gathered."
        if not include_help:
            return text
        return (
            text
            + " Automatic walking stops within interaction reach. It opens doors using normal turns and stops when enemies are nearby."
        )

    def select(self, target):
        if not self.exists(target):
            return [Event("That object is no longer there.")]
        self.game.tracked_object = dict(target)
        self.game.tracker_category = self.category(target)
        return [
            Event("Tracking " + self.description(target), "target", x=target["x"], y=target["y"])
        ]

    def clear(self):
        self.game.tracked_object = None
        return [Event("Object tracking cleared.")]

    def status(self):
        target = self.game.tracked_object
        if not target:
            return [Event("No object tracked. Press O to select one.")]
        if not self.exists(target):
            return [Event("Tracked object is no longer there. Press O to choose another.")]
        return [Event("Tracked: " + self.description(target))]

    def route(self):
        game = self.game
        target = game.tracked_object
        if not target or not self.exists(target):
            return None
        start = (game.x, game.y)
        if self.distance(target) <= 1:
            return []
        cx, cy = game.x // SIZE, game.y // SIZE
        xmin, xmax = (cx - 1) * SIZE, (cx + 2) * SIZE - 1
        ymin, ymax = (cy - 1) * SIZE, (cy + 2) * SIZE - 1
        if not (xmin <= target["x"] <= xmax and ymin <= target["y"] <= ymax):
            return None
        goals = {(target["x"] + dx, target["y"] + dy) for dx, dy in DIRECTIONS.values()}
        queue = [(0, start)]
        costs = {start: 0}
        previous = {}
        while queue:
            cost, point = heapq.heappop(queue)
            if cost != costs[point]:
                continue
            if point in goals:
                result = []
                while point != start:
                    point, direction = previous[point]
                    result.append(direction)
                return result[::-1]
            for direction, (dx, dy) in DIRECTIONS.items():
                nx, ny = point[0] + dx, point[1] + dy
                if not (xmin <= nx <= xmax and ymin <= ny <= ymax):
                    continue
                tile, objects = game.world.at(nx, ny)
                if not tile["passable"]:
                    continue
                blockers = [
                    obj
                    for obj in objects
                    if WORLD["objects"][obj["type"]]["blocking"] and not obj.get("opened")
                ]
                if any(obj["type"] != "door" for obj in blockers):
                    continue
                if any(
                    c["health"] > 0 and (c["x"], c["y"]) == (nx % SIZE, ny % SIZE)
                    for c in game.world.chunk(nx // SIZE, ny // SIZE)["creatures"]
                ):
                    continue
                next_cost = cost + (2 if blockers else 1)
                if next_cost < costs.get((nx, ny), float("inf")):
                    costs[nx, ny] = next_cost
                    previous[nx, ny] = (point, direction)
                    heapq.heappush(queue, (next_cost, (nx, ny)))
        return None

    def step(self):
        game = self.game
        target = game.tracked_object
        if game.health <= 0:
            return [Event("Automatic walking stopped. You cannot move.")], False
        if not target or not self.exists(target):
            return [Event("Automatic walking stopped. No tracked object remains.")], False
        if self.distance(target) <= 1:
            return [
                Event(
                    f"Arrived at {self.name(target)}. Enter interacts; G picks up loose items.",
                    "target",
                )
            ], False
        if game.threats():
            return [
                Event("Automatic walking stopped: enemies nearby. Press T to inspect threats.")
            ], False
        route = self.route()
        if not route:
            return [
                Event(
                    "Automatic walking stopped. No route within the nearby chunks. Move closer or choose another object."
                )
            ], False
        before = (game.x, game.y, game.turn)
        events = game.move(route[0])
        if game.health <= 0 or game.threats():
            events.append(Event("Automatic walking stopped: danger nearby."))
            return events, False
        if self.distance(target) <= 1:
            events.append(
                Event(
                    f"Arrived at {self.name(target)}. Enter interacts; G picks up loose items.",
                    "target",
                )
            )
            return events, False
        if (game.x, game.y, game.turn) == before:
            events.append(Event("Automatic walking stopped: path blocked."))
            return events, False
        return events, True
