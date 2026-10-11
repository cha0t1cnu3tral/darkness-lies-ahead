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
        details = ui.DetailChoiceDialog(
            frame,
            "Crafting test",
            "Select a recipe",
            ["First", "Second"],
            lambda index: f"Recipe {index} details",
        )
        assert details.details.GetValue() == "Recipe 0 details"
        details.choices.SetSelection(1)
        details.update_details()
        assert details.details.GetValue() == "Recipe 1 details"
        details.Destroy()
        new_game = ui.NewGameDialog(frame)
        assert new_game.name.GetName() == "Survivor name"
        assert "World seed" in new_game.seed.GetName()
        new_game.Destroy()
        frame.game.inventory["fiber"] = 3
        with patch.object(ui.DetailChoiceDialog, "ShowModal", return_value=wx.ID_OK):
            frame.crafting_menu()
            assert frame.game.crafting["recipe"] == "cordage"
            frame.crafting_menu()
            assert frame.game.crafting["progress"] == 3
        with patch.object(ui.DetailChoiceDialog, "ShowModal", return_value=wx.ID_CANCEL):
            frame.inventory_menu()
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
    return "Native UI smoke check passed: audio, menu, seed dialog, map rendering, crafting dialogs, inventory, event history, save, resume, exit."
