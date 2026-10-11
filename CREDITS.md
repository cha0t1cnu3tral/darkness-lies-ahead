# Audio and accessibility credits

All bundled audio below is published under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/). Original recordings are included except where edits are explicitly described. No generated tones are used.

| Asset | Creator | Source | Changes |
| --- | --- | --- | --- |
| Midnight (normal quality MP3) | Anton Revin (AR) | https://opengameart.org/content/midnight | None |
| Wind1 | Luke.RUSTLTD | https://opengameart.org/content/wind1 | None |
| Impact Sounds | Kenney | https://kenney.nl/assets/impact-sounds | None; selects footsteps and impacts |
| RPG Audio | Kenney | https://kenney.nl/assets/rpg-audio | None; selects doors, creaks, cloth, and knife sounds |
| Interface Sounds | Kenney | https://kenney.nl/assets/interface-sounds | None |
| CZ pistol from Gunshot Sounds | Tabasco | https://opengameart.org/content/gunshot-sounds | Four individual shots extracted, with 80ms tail fades |
| Gunreload1 | SpringySpringo | https://opengameart.org/content/gun-reload-sounds | None |

Pack licenses are retained alongside Kenney recordings. `assets/audio/provenance.json` lists publisher download URLs and checksums. Recordings remain covered by their original CC0 dedication independently of the game's source code.

## NVDA Controller Client

The unmodified x64 `nvdaControllerClient.dll` from NV Access's **NVDA 2026.2** Controller Client package is dynamically loaded. It is licensed under **LGPL 2.1**; its complete license and documentation are included in `vendor/nvda`. Users may replace this DLL with a compatible build.

- Publisher archive: https://download.nvaccess.org/releases/2026.2/nvda_2026.2_controllerClient.zip
- Source repository: https://github.com/nvaccess/nvda
- Controller source: https://github.com/nvaccess/nvda/tree/master/extras/controllerClient

Python, wxPython/wxWidgets, pygame-ce/SDL, and PyInstaller retain their respective licenses. The release's `licenses` folder contains the license texts distributed with the installed dependencies. pygame-ce and NVDA are dynamically linked and can be replaced by compatible builds; no dependency source has been modified.
