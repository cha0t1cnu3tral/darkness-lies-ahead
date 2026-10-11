# Darkness Lies Ahead

A Windows desktop, turn-based exploration game set decades after civilization's collapse. Explore individual tiles in abandoned suburbs, search buildings, and survive encounters. The design document calls this world **After the Collapse**; this repository and executable use **Darkness Lies Ahead**.

## Play

Download the Windows ZIP from [Releases](https://github.com/cha0t1cnu3tral/darkness-lies-ahead/releases), extract the entire folder, then open `DarknessLiesAhead.exe`. Python is not required for the packaged build. Windows 10/11, 64-bit is the initial target.

The main menu contains **New game**, **Saved games**, **Settings**, and **Exit**. New game accepts an optional world seed; leaving it blank creates a random world. Start a new survivor and walk east along the path to the house. Walking into its door opens it; the next step enters. Search the kitchen cabinet and bedroom wardrobe, talk to Mara, and watch for the feral dog.

## Procedural world and crafting

The world generates **16 × 16 tile chunks on demand**, using the saved seed and chunk coordinates. Beyond the starting area, houses, cabins, workshops, brush, woodland, and encounters vary by seed. Building layouts rotate and mirror, and clear borders form continuous streets between chunks. Only nine chunks stay cached; evicted changes persist on disk. Opened doors, gathered resources, dropped supplies, enemies, and searched containers survive leaving an area and reloading a save. Enemies can follow you across chunk boundaries.

Gather branches and plant fibers from brush piles south of the starting path. Press **C** to weave cordage, then carve a wooden spear with your knife. Search wardrobes and crates for clean cloth to make bandages. Dismantle broken chairs for wood and scrap. The workshop one block east contains a workbench for crafting padded splints; a cabin lies one block north.

Recipes display required materials, tools, workstation, and work time through native lists and a readable details field. Materials can come from inventory or loose supplies on your tile or adjacent accessible tiles. Crafting reserves ingredients and proceeds in three-second work steps. Projects can be paused, saved, resumed, or cancelled to recover their materials. Enemies respond to the time you spend working. Press **I** to equip your finished spear, which reaches two tiles. Dropping a pistol returns its loaded cartridges to inventory so ammunition cannot duplicate.

## Keyboard and accessibility

| Key | Action |
| --- | --- |
| Arrows | Walk one tile |
| Shift / Control / Alt + Arrow | Run / crouch / dodge |
| Space | Jump two clear tiles in the facing direction |
| Enter | Nearby object interactions |
| G / D | Pick up loose items / put an item down |
| I | Inventory, inspect, use, equip, and drop actions |
| C | Crafting recipes and current project |
| L / S / T | Surroundings / status / threats, without advancing time |
| Tab on the map | Cycle enemy targets |
| F / Shift + F / E | Attack / heavy attack / block |
| A / R / V | Aim or steady aim / reload / ready knife |
| Period | Rest |
| F1 / F5 / F6 | Help / save / switch map and event history focus |
| Escape | Save and return to the main menu |

Menus, dialogs, lists, sliders, and event history use native wxWidgets Windows controls. NVDA receives action descriptions through the bundled NVDA Controller Client, including braille messages. The map exposes an application accessibility role. If NVDA intercepts movement keys, use **NVDA + Space** to enter focus mode. Use Tab and Shift + Tab for native menu navigation; Shift + Tab leaves the map for other controls.

Sound never carries exclusive gameplay information. Movement, obstacles, enemies, attacks, and interactions also produce readable text. Settings independently control master, music, ambience, and effect volumes, NVDA announcements, speech ducking, and graphical contrast. The NVDA connection and native control flow have been checked locally; a full manual NVDA playthrough is still required before claiming complete accessibility certification.

## Recorded audio

The build includes Anton Revin's melancholy piano/synth track **Midnight**, Luke.RUSTLTD's wind ambience, Kenney's recorded surface footsteps and interaction packs, and recorded firearm effects. Footsteps choose among five variants per implemented surface without immediate repetition. Outdoors, wind layers beneath the score; indoors it recedes and positional building creaks appear. Music and ambience duck during spoken game events. Effects use a separate channel pool, distance attenuation, and stereo positioning.

Credits and licensing are in [CREDITS.md](CREDITS.md); downloads and checksums are recorded in `assets/audio/provenance.json`. Kitchen tile temporarily shares the concrete recordings. More specific flooring recordings, environmental layers, and a larger adaptive soundtrack remain planned.

## Develop

With [uv](https://docs.astral.sh/uv/), run this command from the repository on 64-bit Windows:

```powershell
uv run main.py
```

uv manages Python 3.14, creates `.venv`, and installs the locked runtime dependencies automatically. `uv.lock` is committed for reproducible setup. Double-click `Start Game.bat` to use the same launcher. Audio is included in Git; `uv run tools/fetch_assets.py` re-downloads it from the original publishers. Tests, development tools, and packaging:

```powershell
uv run python -m unittest discover -s tests -v
uv run tools/smoke_ui.py
uv run --group dev ruff check .
uv run --group dev ruff format --check .
powershell -ExecutionPolicy Bypass -File tools/build.ps1
```

`game/engine.py` contains UI-independent mechanics and a nine-chunk LRU cache. Evicted chunks persist to session files; saves independently checkpoint chunks and atomically replace the manifest. Content-addressed chunk revisions avoid rewriting unchanged content and preserve the previous save if a write fails. Only nearby creatures receive detailed AI; distant chunks remain inactive. `game/ui.py`, `game/accessibility.py`, and `game/audio.py` consume the same state. JSON definitions live in `data/`; tests cover movement, interactions, combat, chunk eviction, persistence, and audio decoding.

Saves, settings, and logs are stored under `%LOCALAPPDATA%\DarknessLiesAhead`. Each survivor has a separate save slot. Autosave runs every 30 seconds of game time and when returning to the menu or exiting; real time does not advance the world. Version 1 saves remain loadable; visited areas retain their original tiles and changes, while newly explored chunks use the expanded generator.

## Development scope

This prototype implements exploration, basic crafting, inventory handling, combat, and the accessibility foundation, rather than the full design catalog in the existing `agents.md`. The next milestones are a broader building catalog and flooring audio, advanced crafting and cooking, agriculture, reclamation and settlements, richer NPC behavior, and distant-world simulation. Existing save format is versioned; future changes will need migration handling.
