"""Hidden native UI/asset check for source and packaged Windows builds."""

import os
from pathlib import Path
import tempfile
from unittest.mock import patch


def smoke():
    os.environ["SDL_AUDIODRIVER"] = "dummy"
    import wx
    from . import ui
    from .engine import Game

    with tempfile.TemporaryDirectory() as directory, patch.object(ui, "USER", Path(directory)):
        app = wx.App(False)
        frame = ui.Frame()
        frame.settings["speech"] = False
        if not frame.audio.enabled:
            raise RuntimeError(frame.audio.error)
        assert [b.GetLabel() for b in frame.menu_buttons] == [
            "New game",
            "Saved games",
            "Settings",
            "Exit",
        ]
        frame.game = Game(42)
        frame.play_screen()
        frame.deliver(frame.game.move("east"))
        app.Yield()
        assert frame.game.x == 4
        assert "Walk east" in frame.log.GetValue()
        assert frame.map.accessible.GetRole(0)[1] == wx.ROLE_SYSTEM_APPLICATION
        bitmap = wx.Bitmap(1000, 700)
        dc = wx.MemoryDC(bitmap)
        frame.map.draw(dc)
        dc.SelectObject(wx.NullBitmap)
        assert frame.save_game(silent=True)
        frame.return_menu()
        assert frame.mode == "menu"
        assert frame.menu_buttons[-1].GetLabel() == "Resume current game"
        frame.Close()
        app.Yield()
    return "Native UI smoke check passed: audio, menu, map rendering, event history, save, resume, exit."
