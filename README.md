# Darkness Lies Ahead

A Windows desktop, turn-based exploration game set decades after civilization's collapse. Explore individual tiles in abandoned suburbs, search buildings, and survive encounters. The design document calls this world **After the Collapse**; this repository and executable use **Darkness Lies Ahead**.

## Play

Download the Windows ZIP from [Releases](https://github.com/cha0t1cnu3tral/darkness-lies-ahead/releases), extract the entire folder, then open `DarknessLiesAhead.exe`. Python is not required for the packaged build. Windows 10/11, 64-bit is the initial target.

The main menu contains **New game**, **Saved games**, **Settings**, and **Exit**. Start a new survivor and walk east along the path to the house. Walking into its door opens it; the next step enters. Search the kitchen cabinet and bedroom wardrobe, talk to Mara, and watch for the feral dog.

## Keyboard and accessibility

| Key | Action |
| --- | --- |
| Arrows | Walk one tile |
| Shift / Control / Alt + Arrow | Run / crouch / dodge |
| Space | Jump two clear tiles in the facing direction |
| Enter or G | Nearby interaction menu |
| I | Inventory and usable items |
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

Requires 64-bit Python 3.14 on Windows for the pinned dependencies.

```powershell
python -m pip install -r requirements.txt
python main.py
python -m unittest discover -s tests -v
python tools/smoke_ui.py
```

Double-click `Start Game.bat` to run the source version after installing dependencies. Audio is included in Git; `python tools/fetch_assets.py` re-downloads it from the original publishers. Development tools and packaging:

```powershell
python -m pip install -r requirements-dev.txt
python -m ruff check .
python -m ruff format --check .
powershell -ExecutionPolicy Bypass -File tools/build.ps1
```

`game/engine.py` contains UI-independent mechanics and a nine-chunk LRU cache. Evicted chunks persist to session files; saves independently checkpoint chunks and atomically replace the manifest. Content-addressed chunk revisions avoid rewriting unchanged content and preserve the previous save if a write fails. Only nearby creatures receive detailed AI; distant chunks remain inactive. `game/ui.py`, `game/accessibility.py`, and `game/audio.py` consume the same state. JSON definitions live in `data/`; tests cover movement, interactions, combat, chunk eviction, persistence, and audio decoding.

Saves, settings, and logs are stored under `%LOCALAPPDATA%\DarknessLiesAhead`. Each survivor has a separate save slot. Autosave runs every 30 seconds of game time and when returning to the menu or exiting; real time does not advance the world.

## Development scope

This first prototype implements the exploration and accessibility foundation, not the full design catalog in the existing `agents.md`. The next milestones are broader building generation and real flooring audio, creature migration and richer combat timing, crafting and cooking, agriculture, reclamation and settlements, and distant-world simulation. Existing save format is versioned; future changes will need migration handling.
