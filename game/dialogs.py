"""Reusable native choice list with screen-reader-readable details."""

import wx


class NewGameDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="New game", size=(560, 320))
        layout = wx.BoxSizer(wx.VERTICAL)
        layout.Add(wx.StaticText(self, label="Survivor name"), 0, wx.ALL, 12)
        self.name = wx.TextCtrl(self, value="Survivor")
        self.name.SetName("Survivor name")
        layout.Add(self.name, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        layout.Add(
            wx.StaticText(
                self, label="World seed (optional). Use the same number to recreate a world."
            ),
            0,
            wx.ALL,
            12,
        )
        self.seed = wx.TextCtrl(self)
        self.seed.SetName("World seed. Leave blank for a new random world.")
        layout.Add(self.seed, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        layout.Add(self.CreateButtonSizer(wx.OK | wx.CANCEL), 0, wx.ALL | wx.ALIGN_CENTER, 16)
        self.SetSizer(layout)
        self.Bind(wx.EVT_BUTTON, self.accept, id=wx.ID_OK)
        self.name.SetFocus()
        self.name.SelectAll()

    def accept(self, event):
        raw = self.seed.GetValue().strip()
        if raw and (
            not raw.isascii() or not raw.isdigit() or len(raw) > 10 or int(raw) > 2147483647
        ):
            wx.MessageBox(
                "Enter a whole number from 0 to 2147483647, or leave the seed blank.",
                "World seed",
                parent=self,
            )
            self.seed.SetFocus()
            return
        self.EndModal(wx.ID_OK)


class DetailChoiceDialog(wx.Dialog):
    def __init__(self, parent, title, prompt, choices, details, action="Select"):
        super().__init__(parent, title=title, size=(700, 550))
        self.SetMinSize((550, 420))
        layout = wx.BoxSizer(wx.VERTICAL)
        layout.Add(wx.StaticText(self, label=prompt), 0, wx.ALL, 12)
        self.choices = wx.ListBox(self, choices=choices)
        self.choices.SetName(title + " choices")
        self.details = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.details.SetName("Selected choice details. Tab to read requirements and description.")
        self.describe = details
        self.choices.Bind(wx.EVT_LISTBOX, self.update_details)
        self.choices.Bind(wx.EVT_LISTBOX_DCLICK, lambda event: self.EndModal(wx.ID_OK))
        layout.Add(self.choices, 1, wx.EXPAND | wx.ALL, 12)
        layout.Add(self.details, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        buttons = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        self.FindWindowById(wx.ID_OK).SetLabel(action)
        layout.Add(buttons, 0, wx.ALL | wx.ALIGN_CENTER, 12)
        self.SetSizer(layout)
        if choices:
            self.choices.SetSelection(0)
            self.update_details()
        else:
            self.FindWindowById(wx.ID_OK).Disable()
        self.choices.SetFocus()

    def update_details(self, event=None):
        index = self.choices.GetSelection()
        if index != wx.NOT_FOUND:
            self.details.ChangeValue(self.describe(index))

    def GetSelection(self):
        return self.choices.GetSelection()
