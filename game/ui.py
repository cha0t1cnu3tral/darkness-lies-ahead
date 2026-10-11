"""Windows-native accessible menus and a graphical view of the shared engine."""

import json
import logging
import random
import wx

from .accessibility import Narrator
from .audio import Audio
from .engine import Game, Event, ITEMS, RECIPES, SIZE
from .dialogs import DetailChoiceDialog, NewGameDialog
from .paths import USER
from . import settings as preferences

HELP = """Darkness Lies Ahead — early playable prototype

Civilization collapsed decades ago. You begin west of an abandoned house.
Move east along the concrete path. Walking into a closed door opens it;
press the arrow again to enter. Search the kitchen cabinet and bedroom wardrobe.
Mara stands northwest of your starting position. A feral dog prowls the yard.

Arrow keys: walk one tile. Shift + Arrow: run up to two tiles.
Control + Arrow: crouch quietly. Alt + Arrow: dodge one tile.
Space: jump two clear tiles in your facing direction.
Enter: nearby object interactions. G: pick up nearby ground items.
I: inventory, inspect, use, equip, and drop actions. D: put an item down.
C: crafting recipes, project progress, continue work, or cancel a project.
L: describe your tile and adjacent tiles.
S: read health, stamina, time, and weapon status.
T: inspect nearby threats without advancing time.
Tab on the map: cycle enemy targets. F: melee attack. Shift + F: heavy attack.
E: block. A: ready pistol, then A again to improve aim. F while aiming: fire.
R: reload. V: ready knife. Period: rest and recover stamina.
F5: save. F1: this help. Escape: save and return to the main menu.
F6: switch focus between the map and the readable event history.

Menus use native Windows buttons, lists, and sliders. Tab and Shift + Tab move
between controls. Arrow keys select list entries. Enter activates a choice.
NVDA receives game action descriptions and braille through its controller API.
On the map, NVDA must pass keys through to the game; use NVDA + Space to switch
to focus mode if needed. Every sound cue also has text feedback.

Gather branches and plant fibers from brush piles. Weave cordage, then carve a
wooden spear. Scavenge clean cloth for bandages. Crafting reserves materials;
each work step advances time, and unfinished projects persist through saves.
The workshop one block east has a workbench for crafting padded splints.
Cabins, workshops, woodland and houses generate as you explore beyond the start.

The prototype includes exploration, scavenging, basic crafting, basic combat,
inventory, saves, and audio settings. Farming, cooking, advanced crafting, settlement
management, the full building catalog, and broader NPC simulation are future work.
"""


class MapAccessibility(wx.Accessible):
    def __init__(self, window):
        super().__init__(window)
        self.window = window

    def GetName(self, child):
        return (
            wx.ACC_OK,
            "World exploration. Arrow keys move. F1 for controls. F6 for event history.",
        )

    def GetRole(self, child):
        return wx.ACC_OK, wx.ROLE_SYSTEM_APPLICATION

    def GetValue(self, child):
        game = self.window.frame.game
        return wx.ACC_OK, game.describe() if game else "No active game"

    def GetState(self, child):
        state = wx.ACC_STATE_SYSTEM_FOCUSABLE
        if self.window.HasFocus():
            state |= wx.ACC_STATE_SYSTEM_FOCUSED
        return wx.ACC_OK, state


class MapView(wx.Panel):
    def __init__(self, parent, frame):
        super().__init__(parent, style=wx.WANTS_CHARS | wx.BORDER_SIMPLE)
        self.frame = frame
        self.SetMinSize((640, 540))
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetName("World exploration")
        self.accessible = MapAccessibility(self)
        self.SetAccessible(self.accessible)
        self.Bind(wx.EVT_PAINT, self.paint)
        self.Bind(wx.EVT_LEFT_DOWN, lambda event: self.SetFocus())

    def paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        self.draw(dc)

    def draw(self, dc):
        dc.SetBackground(wx.Brush("#111b19"))
        dc.Clear()
        game = self.frame.game
        if not game:
            return
        width, height = self.GetClientSize()
        size = max(12, min(width // 19, height // 17))
        ox, oy = (width - 19 * size) // 2, (height - 17 * size) // 2
        dc.SetFont(
            wx.Font(
                max(8, int(size * 0.30)),
                wx.FONTFAMILY_SWISS,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_BOLD,
            )
        )
        for row in range(17):
            for col in range(19):
                x, y = game.x + col - 9, game.y + row - 8
                tile, objects = game.world.at(x, y)
                left, top = ox + col * size, oy + row * size
                color = tile["color"]
                if self.frame.settings["high_contrast"]:
                    color = "#eeeeee" if tile["passable"] else "#252525"
                dc.SetBrush(wx.Brush(color))
                dc.SetPen(wx.Pen("#222c26", 1))
                dc.DrawRectangle(left, top, size, size)
                # Surface texture marks retain the readable tile boundaries.
                if tile["surface"] == "wood":
                    dc.SetPen(wx.Pen("#a78055", 1))
                    dc.DrawLine(left + 2, top + size // 2, left + size - 2, top + size // 2)
                if tile["name"] == "old oak tree":
                    dc.SetBrush(wx.Brush("#71935a"))
                    dc.DrawCircle(left + size // 2, top + size // 2, size // 3)
                for obj in objects:
                    if obj["type"] == "door":
                        dc.SetBrush(wx.Brush("#bba77c" if obj["opened"] else "#bf925e"))
                        dc.DrawRectangle(left + size // 3, top + 3, size // 3, size - 6)
                        label = "/" if obj["opened"] else "+"
                    elif obj["type"] == "scavenger":
                        label = "M"
                    elif obj["type"] == "workbench":
                        label = "W"
                    elif obj["type"] == "brush":
                        label = "-" if obj["searched"] else "B"
                    else:
                        label = "-" if obj["searched"] else "?"
                    dc.SetTextForeground("#ffffff")
                    dc.DrawText(label, left + size // 3, top + size // 4)
                if game.ground_at(x, y):
                    dc.SetTextForeground("#edce79")
                    dc.DrawText("*", left + 2, top + 2)
                chunk = game.world.chunk(x // SIZE, y // SIZE)
                creature = next(
                    (c for c in chunk["creatures"] if (c["x"], c["y"]) == (x % SIZE, y % SIZE)),
                    None,
                )
                if creature:
                    dc.SetTextForeground(creature["color"] if creature["health"] > 0 else "#777777")
                    dc.DrawText(
                        "D" if creature["health"] > 0 else "x", left + size // 3, top + size // 4
                    )
                if game.target == (x, y):
                    dc.SetPen(wx.Pen("#e9bc71", 3))
                    dc.SetBrush(wx.TRANSPARENT_BRUSH)
                    dc.DrawRectangle(left + 2, top + 2, size - 4, size - 4)
                if (x, y) == (game.x, game.y):
                    dc.SetBrush(wx.Brush("#a8edd6"))
                    dc.SetPen(wx.Pen("#ffffff", 2))
                    dc.DrawCircle(left + size // 2, top + size // 2, size // 3)
                    dc.SetTextForeground("#10261e")
                    dc.DrawText("@", left + size // 3, top + size // 4)


class Frame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Darkness Lies Ahead", size=(1100, 820))
        self.SetMinSize((850, 680))
        self.settings = preferences.load()
        self.narrator = Narrator(self.settings)
        self.audio = Audio(self.settings)
        self.game = None
        self.panel = None
        self.mode = "menu"
        self.history = []
        self.saved_turn = None
        self.scheduled_sounds = []
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, lambda event: self.audio.update(), self.timer)
        self.timer.Start(100)
        self.main_menu()
        self.Centre()
        if self.audio.error:
            wx.CallAfter(
                wx.MessageBox,
                "Audio could not start: "
                + self.audio.error
                + "\nThe game remains usable. See the application log.",
                "Audio unavailable",
                wx.OK | wx.ICON_WARNING,
                self,
            )

    def replace_panel(self, mode):
        self.mode = mode
        for job in self.scheduled_sounds:
            job.Stop()
        self.scheduled_sounds.clear()
        if self.panel:
            self.panel.Destroy()
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour("#172320")
        self.panel.SetForegroundColour("#f0ede0")
        self.outer = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(self.outer)
        self.frame_sizer = wx.BoxSizer(wx.VERTICAL)
        self.frame_sizer.Add(self.panel, 1, wx.EXPAND)
        self.SetSizer(self.frame_sizer)

    def text(self, label, size=12):
        text = wx.StaticText(self.panel, label=label)
        text.SetForegroundColour("#f0ede0")
        text.SetFont(wx.Font(size, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.outer.Add(text, 0, wx.ALL, 14)
        return text

    def main_menu(self):
        self.replace_panel("menu")
        self.SetTitle("Darkness Lies Ahead — Main menu")
        self.text("DARKNESS LIES AHEAD", 30)
        self.text("AFTER THE COLLAPSE", 15)
        self.text(
            "The streets are silent. The houses remember.\nA new life begins with a single step.",
            14,
        )
        self.menu_buttons = []
        for label, callback in (
            ("New game", self.new_game),
            ("Saved games", self.saved_games),
            ("Settings", self.show_settings),
            ("Exit", lambda: self.Close()),
        ):
            button = wx.Button(self.panel, label=label, size=(300, 48))
            button.Bind(wx.EVT_BUTTON, lambda event, action=callback: self.menu_action(action))
            self.outer.Add(button, 0, wx.LEFT | wx.BOTTOM, 28)
            self.menu_buttons.append(button)
        if self.game:
            button = wx.Button(self.panel, label="Resume current game", size=(300, 48))
            button.Bind(wx.EVT_BUTTON, lambda event: self.play_screen())
            self.outer.Add(button, 0, wx.LEFT | wx.BOTTOM, 28)
            self.menu_buttons.append(button)
        self.text(
            "Early playable prototype • Keyboard and NVDA supported\nUse Tab or Up / Down to select. Enter activates a button. F1 opens controls."
        )
        self.Layout()
        wx.CallAfter(self.focus_current_screen)
        self.audio.environment(False)

    def menu_action(self, action):
        self.audio.play("menu")
        action()

    def announce(self, text):
        if self.narrator.say(text):
            self.audio.duck(text)

    def new_game(self):
        if self.game and not self.save_game():
            return
        dialog = NewGameDialog(self)
        if dialog.ShowModal() != wx.ID_OK:
            dialog.Destroy()
            return
        name = dialog.name.GetValue().strip()[:80] or "Survivor"
        raw_seed = dialog.seed.GetValue().strip()
        seed = int(raw_seed) if raw_seed else random.SystemRandom().randrange(1, 2**31)
        dialog.Destroy()
        if self.game:
            self.game.world.close()
        self.game = Game(seed)
        self.game.name = name
        self.saved_turn = None
        self.history = []
        self.play_screen()
        self.deliver(
            [
                Event(
                    "Welcome, "
                    + name
                    + ". You stand west of an abandoned house. Walk east to find the door. Enter opens nearby interactions. F1 reads the controls. "
                    + self.game.describe()
                )
            ]
        )
        self.save_game(silent=True)

    def saved_games(self):
        saves = []
        for manifest in (USER / "saves").glob("*/manifest.json"):
            try:
                state = json.loads(manifest.read_text(encoding="utf-8"))
                saves.append(
                    (
                        manifest,
                        f"{state['name']} — time {state['turn']} seconds, health {state['health']}, position {state['x']}, {state['y']}",
                    )
                )
            except ValueError, OSError, KeyError:
                logging.exception("Unreadable save %s", manifest)
        saves.sort(key=lambda entry: entry[0].stat().st_mtime, reverse=True)
        if not saves:
            wx.MessageBox(
                "No saved games yet. Choose New game to begin.", "Saved games", parent=self
            )
            return
        dialog = wx.SingleChoiceDialog(
            self, "Choose a survivor to continue:", "Saved games", [label for _, label in saves]
        )
        if dialog.ShowModal() == wx.ID_OK:
            try:
                candidate = Game.load(saves[dialog.GetSelection()][0])
                if self.game and not self.save_game():
                    candidate.world.close()
                    dialog.Destroy()
                    return
                if self.game:
                    self.game.world.close()
                self.game = candidate
                self.history = []
                self.saved_turn = candidate.turn
                self.play_screen()
                self.deliver(
                    [Event("Saved game loaded. " + self.game.describe() + " " + self.game.status())]
                )
            except OSError, ValueError, KeyError, TypeError:
                logging.exception("Save load failed")
                wx.MessageBox(
                    "This save could not be loaded. Your current game is unchanged.",
                    "Load failed",
                    parent=self,
                )
        dialog.Destroy()

    def show_settings(self):
        dialog = wx.Dialog(self, title="Settings", size=(570, 530))
        layout = wx.BoxSizer(wx.VERTICAL)
        volumes = {}
        for key in ("master", "music", "ambience", "effects"):
            label = wx.StaticText(dialog, label=key.capitalize() + " volume (0 to 100)")
            layout.Add(label, 0, wx.ALL, 8)
            slider = wx.Slider(
                dialog,
                value=self.settings[key],
                minValue=0,
                maxValue=100,
                style=wx.SL_HORIZONTAL | wx.SL_LABELS,
            )
            slider.SetName(key.capitalize() + " volume")
            slider.Bind(wx.EVT_SLIDER, lambda event, k=key: self.preview_volume(k, event.GetInt()))
            layout.Add(slider, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 16)
            volumes[key] = slider
        toggles = {}
        for key, label in (
            ("speech", "Announce game events through NVDA"),
            ("duck", "Lower music and ambience during speech"),
            ("high_contrast", "High contrast graphical map"),
        ):
            control = wx.CheckBox(dialog, label=label)
            control.SetValue(self.settings[key])
            layout.Add(control, 0, wx.ALL, 8)
            toggles[key] = control
        layout.Add(dialog.CreateButtonSizer(wx.OK | wx.CANCEL), 0, wx.ALL | wx.ALIGN_CENTER, 12)
        dialog.SetSizer(layout)
        original = dict(self.settings)
        if dialog.ShowModal() == wx.ID_OK:
            self.settings.update({k: c.GetValue() for k, c in volumes.items()})
            self.settings.update({k: c.GetValue() for k, c in toggles.items()})
            try:
                preferences.save(self.settings)
            except OSError:
                wx.MessageBox(
                    "Settings work for this session but could not be saved.",
                    "Settings",
                    parent=self,
                )
        else:
            self.settings.update(original)
        self.audio.update()
        if self.mode == "play":
            self.map.Refresh()
        dialog.Destroy()

    def preview_volume(self, key, value):
        self.settings[key] = value
        self.audio.update()
        if key == "effects":
            self.audio.play("menu")

    def play_screen(self):
        self.replace_panel("play")
        self.SetTitle("Darkness Lies Ahead — " + self.game.name)
        self.header = self.text("", 15)
        body = wx.BoxSizer(wx.HORIZONTAL)
        self.map = MapView(self.panel, self)
        body.Add(self.map, 3, wx.EXPAND | wx.ALL, 8)
        sidebar = wx.BoxSizer(wx.VERTICAL)
        legend = wx.StaticText(
            self.panel,
            label="THE OVERGROWN SUBURB\n\n@ You   M Mara   D Feral dog\n+ Closed door   / Open door\n? Container   B Brush\nW Workbench   * Ground items\n\nArrows: walk\nShift: run • Control: crouch\nEnter: interact • I: inventory\nG: pick up • D: drop • C: craft\nL: surroundings • S: status\nF1: controls • F5: save\nEscape: main menu",
        )
        legend.SetForegroundColour("#f0ede0")
        sidebar.Add(legend, 0, wx.ALL, 10)
        for label, callback in (
            ("Nearby interactions", self.interaction_menu),
            ("Inventory", self.inventory_menu),
            ("Crafting", self.crafting_menu),
            ("Settings", self.show_settings),
            ("Save game", self.save_game),
            ("Main menu", self.return_menu),
        ):
            button = wx.Button(self.panel, label=label)
            button.Bind(wx.EVT_BUTTON, lambda event, action=callback: self.menu_action(action))
            sidebar.Add(button, 0, wx.EXPAND | wx.ALL, 5)
        body.Add(sidebar, 1, wx.EXPAND | wx.ALL, 8)
        self.outer.Add(body, 1, wx.EXPAND)
        self.log = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(-1, 120))
        self.log.SetName("Game event history. F6 returns to the map.")
        self.log.SetValue("\n".join(self.history))
        self.outer.Add(self.log, 0, wx.EXPAND | wx.ALL, 10)
        self.update_view()
        self.Layout()
        wx.CallAfter(self.focus_current_screen)

    def focus_current_screen(self):
        if not self or not self.panel:
            return
        if self.mode == "menu":
            self.menu_buttons[0].SetFocus()
        elif self.mode == "play":
            self.map.SetFocus()

    def update_view(self):
        self.header.SetLabel(
            f"{self.game.name}  |  Health {self.game.health}  |  Stamina {self.game.stamina}  |  Time {self.game.turn}s  |  {'Pistol' if self.game.aiming else self.game.melee()['name']}"
        )
        tile, _ = self.game.world.at(self.game.x, self.game.y)
        self.audio.environment(bool(tile.get("indoors")))
        self.map.Refresh()

    def deliver(self, events):
        message = " ".join(e.text for e in events if e.text)
        delay = 0
        self.scheduled_sounds = [job for job in self.scheduled_sounds if job.IsRunning()]
        for event in events:
            if event.sound:
                dx = (event.x - self.game.x) if event.x is not None else 0
                dy = (event.y - self.game.y) if event.y is not None else 0
                gain = 0.7 if event.sound == "enemy_step" else 1
                job = wx.CallLater(delay, self.audio.play, event.sound, event.surface, dx, dy, gain)
                self.scheduled_sounds.append(job)
                delay += 140
        if message:
            self.history.append(message)
            self.history = self.history[-150:]
            self.log.SetValue("\n".join(self.history))
            self.log.SetInsertionPointEnd()
            self.announce(message)
        self.update_view()
        if self.saved_turn is not None and self.game.turn - self.saved_turn >= 30:
            self.save_game(silent=True)

    def interaction_menu(self):
        choices = self.game.interactions()
        if not choices:
            self.deliver([Event("Nothing to interact with on your tile or adjacent tiles.")])
            return
        dialog = wx.SingleChoiceDialog(
            self,
            "Choose an action. Inspection and menu navigation do not advance time.",
            "Nearby interactions",
            [c[0] for c in choices],
        )
        if dialog.ShowModal() == wx.ID_OK:
            _, x, y, action = choices[dialog.GetSelection()]
            self.deliver(self.game.interact(x, y, action))
        dialog.Destroy()
        self.map.SetFocus()

    def inventory_menu(self):
        items = [(key, count) for key, count in self.game.inventory.items() if count > 0]
        if not items:
            self.deliver([Event("Your inventory is empty.")])
            return
        dialog = DetailChoiceDialog(
            self,
            "Inventory",
            "Choose an item. Tab reads its details. Select opens its actions.",
            [f"{ITEMS[key]['name']}, quantity {count}" for key, count in items],
            lambda index: self.item_description(items[index][0]),
        )
        if dialog.ShowModal() == wx.ID_OK:
            item = items[dialog.GetSelection()][0]
            dialog.Destroy()
            self.item_actions(item)
        else:
            dialog.Destroy()
        self.map.SetFocus()

    def item_description(self, item):
        definition = ITEMS[item]
        text = definition["name"] + ". Quantity " + str(self.game.inventory.get(item, 0)) + "."
        if definition.get("weapon") == "melee":
            text += f" Melee damage {definition['damage']}. Reach {definition['reach']} tiles."
            if self.game.melee_weapon == item:
                text += " Equipped."
        if definition.get("tool"):
            text += " Crafting tool: " + definition["tool"] + "."
        if definition.get("action"):
            text += f" Use: {definition['action']}. Restores {definition.get('health', 0)} health and {definition.get('stamina', 0)} stamina."
        if item == "pistol":
            text += f" Press A on the map to aim. {self.game.ammo} rounds loaded."
        return text

    def item_actions(self, item):
        actions = [("Inspect", lambda: [Event(self.item_description(item))])]
        if ITEMS[item].get("action"):
            actions.append(("Use", lambda: self.game.use_item(item)))
        if ITEMS[item].get("weapon") == "melee":
            actions.append(("Equip", lambda: self.game.equip(item)))
        actions.append(("Put down one", lambda: self.game.drop_item(item)))
        if self.game.inventory.get(item, 0) > 1:
            actions.append(
                ("Put down all", lambda: self.game.drop_item(item, self.game.inventory[item]))
            )
        dialog = wx.SingleChoiceDialog(
            self, "Choose an action:", ITEMS[item]["name"], [name for name, action in actions]
        )
        if dialog.ShowModal() == wx.ID_OK:
            self.deliver(actions[dialog.GetSelection()][1]())
        dialog.Destroy()

    def drop_menu(self):
        items = [key for key, count in self.game.inventory.items() if count > 0]
        if not items:
            self.deliver([Event("Your inventory is empty.")])
            return
        dialog = wx.SingleChoiceDialog(
            self,
            "Choose an item to put down. One item is placed on your tile.",
            "Put down item",
            [f"{ITEMS[key]['name']}, quantity {self.game.inventory[key]}" for key in items],
        )
        if dialog.ShowModal() == wx.ID_OK:
            self.deliver(self.game.drop_item(items[dialog.GetSelection()]))
        dialog.Destroy()
        self.map.SetFocus()

    def pickup_menu(self):
        piles = self.game.nearby_ground()
        if not piles:
            self.deliver(
                [
                    Event(
                        "No loose items within reach. Press Enter to search or gather from nearby objects."
                    )
                ]
            )
            return
        dialog = wx.SingleChoiceDialog(
            self,
            "Choose supplies to pick up:",
            "Ground items",
            [
                f"{pile['count']} {ITEMS[pile['item']]['name']}, {self.game.relative(x, y)}"
                for pile, x, y in piles
            ],
        )
        if dialog.ShowModal() == wx.ID_OK:
            pile, x, y = piles[dialog.GetSelection()]
            self.deliver(self.game.pickup(x, y, pile["item"]))
        dialog.Destroy()
        self.map.SetFocus()

    def crafting_menu(self):
        project = self.game.crafting
        if project:
            recipe = RECIPES[project["recipe"]]
            dialog = DetailChoiceDialog(
                self,
                "Current crafting project",
                f"{recipe['name']}: {project['progress']} of {recipe['seconds']} seconds complete.",
                ["Continue work (up to three seconds)", "Cancel and recover materials"],
                lambda index: (
                    "Continuing consumes game time and allows enemies to act. You can leave and resume this project later."
                    if index == 0
                    else "Reserved materials return to your inventory. Work progress is discarded."
                ),
                action="Perform action",
            )
            if dialog.ShowModal() == wx.ID_OK:
                self.deliver(
                    self.game.continue_craft()
                    if dialog.GetSelection() == 0
                    else self.game.cancel_craft()
                )
        else:
            recipes = list(RECIPES)
            labels = []
            for key in recipes:
                missing = self.game.crafting_requirements(key)
                labels.append(
                    RECIPES[key]["name"]
                    + (" — missing " + ", ".join(missing) if missing else " — ready")
                )
            dialog = DetailChoiceDialog(
                self,
                "Crafting recipes",
                "Choose a recipe. Tab reads ingredients, tools, workstations, and time.",
                labels,
                lambda index: self.game.recipe_description(recipes[index]),
                action="Begin project",
            )
            if dialog.ShowModal() == wx.ID_OK:
                self.deliver(self.game.start_craft(recipes[dialog.GetSelection()]))
        dialog.Destroy()
        self.map.SetFocus()

    def save_game(self, silent=False):
        if not self.game:
            return True
        try:
            self.game.save(USER / "saves")
            self.saved_turn = self.game.turn
            if not silent:
                self.audio.play("save")
                self.announce("Game saved.")
            return True
        except OSError:
            logging.exception("Save failed")
            wx.MessageBox(
                "Could not save the game. Your current session is still open. Check disk space and permissions.",
                "Save failed",
                wx.OK | wx.ICON_ERROR,
                self,
            )
            return False

    def return_menu(self):
        if self.save_game():
            self.main_menu()

    def show_help(self):
        dialog = wx.Dialog(self, title="Controls and accessibility", size=(760, 650))
        layout = wx.BoxSizer(wx.VERTICAL)
        text = wx.TextCtrl(dialog, value=HELP, style=wx.TE_MULTILINE | wx.TE_READONLY)
        text.SetName("Controls and accessibility instructions")
        layout.Add(text, 1, wx.EXPAND | wx.ALL, 12)
        layout.Add(dialog.CreateButtonSizer(wx.OK), 0, wx.ALL | wx.ALIGN_CENTER, 12)
        dialog.SetSizer(layout)
        text.SetFocus()
        dialog.ShowModal()
        dialog.Destroy()

    def on_key(self, event):
        code = event.GetKeyCode()
        if code == wx.WXK_F1:
            self.show_help()
            return
        if self.mode == "menu":
            if code in (wx.WXK_UP, wx.WXK_DOWN):
                focused = wx.Window.FindFocus()
                index = self.menu_buttons.index(focused) if focused in self.menu_buttons else 0
                self.menu_buttons[
                    (index + (1 if code == wx.WXK_DOWN else -1)) % len(self.menu_buttons)
                ].SetFocus()
                self.audio.play("menu")
                return
            event.Skip()
            return
        if code == wx.WXK_F6:
            (self.log if self.map.HasFocus() else self.map).SetFocus()
            return
        if not self.map.HasFocus():
            event.Skip()
            return
        directions = {
            wx.WXK_UP: "north",
            wx.WXK_DOWN: "south",
            wx.WXK_LEFT: "west",
            wx.WXK_RIGHT: "east",
        }
        if code in directions:
            mode = (
                "dodge"
                if event.AltDown()
                else "run"
                if event.ShiftDown()
                else "crouch"
                if event.ControlDown()
                else "walk"
            )
            self.deliver(self.game.move(directions[code], mode))
        elif code == wx.WXK_SPACE:
            self.deliver(self.game.jump())
        elif code == wx.WXK_RETURN:
            self.interaction_menu()
        elif code == ord("G"):
            self.pickup_menu()
        elif code == ord("I"):
            self.inventory_menu()
        elif code == ord("D"):
            self.drop_menu()
        elif code == ord("C"):
            self.crafting_menu()
        elif code == ord("L"):
            self.deliver([Event(self.game.describe() + " " + self.game.nearby())])
        elif code == ord("S"):
            self.deliver([Event(self.game.status())])
        elif code == ord("T"):
            threats = self.game.threats()
            self.deliver(
                [
                    Event(
                        " ".join(
                            f"{c['name']}: {self.game.relative(x, y)}, health {c['health']}."
                            for c, x, y, d in threats
                        )
                        or "No nearby threats."
                    )
                ]
            )
        elif code == wx.WXK_TAB and not event.ShiftDown():
            self.deliver(self.game.cycle_target())
        elif code == ord("F"):
            self.deliver(self.game.attack(event.ShiftDown()))
        elif code == ord("E"):
            self.deliver(self.game.block())
        elif code == ord("A"):
            self.deliver(self.game.aim_action())
        elif code == ord("R"):
            self.deliver(self.game.reload())
        elif code == ord("V"):
            self.deliver(self.game.equip("knife"))
        elif code == ord("."):
            self.deliver(self.game.wait())
        elif code == wx.WXK_F5:
            self.save_game()
        elif code == wx.WXK_ESCAPE:
            self.return_menu()
        else:
            event.Skip()

    def on_close(self, event):
        if self.game and not self.save_game(silent=True):
            if event.CanVeto():
                event.Veto()
                return
        self.timer.Stop()
        for job in self.scheduled_sounds:
            job.Stop()
        if self.game:
            self.game.world.close()
        self.narrator.close()
        self.audio.close()
        self.Destroy()


def run():
    USER.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=USER / "game.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    app = wx.App(False)
    frame = Frame()
    frame.Show()
    app.MainLoop()
