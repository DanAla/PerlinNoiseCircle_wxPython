# PerlinNoiseCircle_wx.py
# https://raw.githubusercontent.com/DanAla/PerlinNoiseCircle_wxPython/refs/heads/main/PerlinNoiseCircle_wx.py
import wx
import random
import math
import svgwrite
import json
import os
from noise import pnoise2

# All files live in the same folder as this script
APP_DIR   = os.path.abspath(os.path.dirname(__file__))
CONFIG_FILE = os.path.join(APP_DIR, 'noise_circles_state.json')
DEFAULT_PARAMS_FILE = os.path.join(APP_DIR, 'default_params.json')

CANVAS_SIZE = 2000          # logical bitmap
VIEWPORT_SIZE = 700         # visible viewport

BUILTIN_DEFAULTS = {
    'startRadius': 25.0,
    'maxCircles': 310,
    'resolution': 1,
    'dRadius': 0.5,
    'rdn': 10.0,
    'xOffset': 0.0,
    'yOffset': 0.0,
    'nSeed': 0,
    'penWidth': 0.25,
    'lineDistance': 1.0,
}

if os.path.isfile(DEFAULT_PARAMS_FILE):
    with open(DEFAULT_PARAMS_FILE) as f:
        DEFAULTS = json.load(f)
else:
    DEFAULTS = BUILTIN_DEFAULTS.copy()


class ParamPanel(wx.Panel):
    def __init__(self, parent, on_changed, initial):
        super().__init__(parent)
        self.on_changed = on_changed
        self.values = dict(initial)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer)

        grid = wx.FlexGridSizer(cols=2, vgap=4, hgap=8)
        self.ctrls = {}

        for key, default in DEFAULTS.items():
            label = wx.StaticText(self, label=key)
            label.SetMinSize((140, -1))
            label.SetWindowStyle(wx.ALIGN_RIGHT)

            if isinstance(default, float):
                sc = wx.SpinCtrlDouble(self, value=str(self.values[key]),
                                       min=0.01, max=1000, inc=0.01)
                sc.SetDigits(2)
            else:
                sc = wx.SpinCtrl(self, value=str(int(self.values[key])),
                                 min=0, max=10000)

            sc.Bind(wx.EVT_SPINCTRLDOUBLE if isinstance(default, float)
                    else wx.EVT_SPINCTRL,
                    self.make_handler(key, sc))
            self.ctrls[key] = sc
            grid.Add(label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.RIGHT, 4)
            grid.Add(sc, 1, wx.EXPAND)

        grid.AddGrowableCol(1, 1)
        self.SetSizer(grid)

    def make_handler(self, key, ctrl):
        def _handler(evt):
            val = ctrl.GetValue()
            self.values[key] = val
            self.start_regen_timer()
        return _handler

    def start_regen_timer(self):
        self.timer.Stop()
        self.timer.StartOnce(300)

    def on_timer(self, evt):
        self.on_changed(self.values.copy())

    def set_all(self, d):
        self.values.update(d)
        for k, c in self.ctrls.items():
            c.SetValue(self.values[k])
        self.on_changed(self.values.copy())


class Canvas(wx.ScrolledWindow):
    def __init__(self, parent):
        super().__init__(parent, size=(VIEWPORT_SIZE, VIEWPORT_SIZE),
                         style=wx.BORDER_NONE)
        self.SetScrollbars(1, 1,
                           CANVAS_SIZE, CANVAS_SIZE,
                           0, 0)  # will be centred later
        self.SetScrollRate(1, 1)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self.on_paint)

        self.buffer = wx.Bitmap(CANVAS_SIZE, CANVAS_SIZE)
        self.values = dict(DEFAULTS)
        self.redraw()

    def set_values(self, d):
        self.values.update(d)
        if abs(self.values['nSeed']) < 1e-6:
            self.values['nSeed'] = random.randint(1, 10000)
        self.redraw()

    def redraw(self):
        dc = wx.MemoryDC(self.buffer)
        dc.SetBackground(wx.Brush(wx.Colour(255, 255, 255)))
        dc.Clear()

        gc = wx.GraphicsContext.Create(dc)
        if not gc:
            return
        gc.SetPen(wx.GraphicsRenderer.GetDefaultRenderer().CreatePen(
            wx.GraphicsPenInfo(wx.Colour(0, 0, 200))
            .Width(self.values['penWidth'])))

        v = self.values
        radius = v['startRadius']
        seed = int(v['nSeed'])
        random.seed(seed)

        def noise(x, y):
            return (pnoise2(x, y, octaves=4, persistence=0.35) + 1) / 2

        x1 = v['startRadius']
        y1 = 0
        lines = []
        scale = CANVAS_SIZE / 2 / 350
        step = max(1, int(round(1 / v['resolution'])))
        ld = v['lineDistance']

        for i in range(int(v['maxCircles']) + 1):
            for j in range(1, 360, step):
                x = (radius - v['rdn']) * math.cos(math.radians(j))
                y = (radius - v['rdn']) * math.sin(math.radians(j))

                n1 = noise((radius - v['rdn']) / 25.0, j / 25.0)
                nf1 = noise(x / 250.0 + n1, (y * j) / 15500.0)
                vval = (((radius - v['rdn']) * 1.5 + 55) ** 2) / 40000.0
                nf2 = noise(x / 30.0, y / 30.0) * ((radius - v['rdn']) ** 1.75) / 3500.0

                # Ensure nf2 is real before using in radians
                nf2_real = float(abs(nf2))
                x2 = v['startRadius'] * math.cos(math.radians(j + nf2_real * 40)) \
                     + radius * math.cos(math.radians(j + nf2_real * 40)) * nf1 * vval
                y2 = v['startRadius'] * math.sin(math.radians(j + nf2_real * 50)) \
                     + radius * math.sin(math.radians(j + nf2_real * 50)) * nf1 * vval
                     
                sx1 = CANVAS_SIZE // 2 + v['xOffset'] * scale + x1 * scale
                sy1 = CANVAS_SIZE // 2 + v['yOffset'] * scale + y1 * scale
                sx2 = CANVAS_SIZE // 2 + v['xOffset'] * scale + x2 * scale
                sy2 = CANVAS_SIZE // 2 + v['yOffset'] * scale + y2 * scale
                lines.append((sx1, sy1, sx2, sy2))

                x1, y1 = x2, y2
                radius += ld * v['dRadius'] / (360.0 * v['resolution'])

        path = gc.CreatePath()
        for sx1, sy1, sx2, sy2 in lines:
            path.MoveToPoint(sx1, sy1)
            path.AddLineToPoint(sx2, sy2)
        gc.StrokePath(path)
        self.Refresh()

    def on_paint(self, evt):
        wx.BufferedPaintDC(self, self.buffer, wx.BUFFER_VIRTUAL_AREA)

    def get_paths(self):
        v = self.values
        radius = v['startRadius']
        seed = int(v['nSeed'])
        random.seed(seed)

        def noise(x, y):
            return (pnoise2(x, y, octaves=4, persistence=0.35) + 1) / 2

        points = [(v['startRadius'], 0)]
        step = max(1, int(round(1 / v['resolution'])))
        ld = v['lineDistance']
        for i in range(int(v['maxCircles']) + 1):
            for j in range(1, 360, step):
                a = math.radians(j)
                cx = (radius - v['rdn']) * math.cos(a)
                cy = (radius - v['rdn']) * math.sin(a)

                n1 = noise((radius - v['rdn']) / 25.0, j / 25.0)
                nf1 = noise(cx / 250.0 + n1, (cy * j) / 15500.0)
                vval = (((radius - v['rdn']) * 1.5 + 55) ** 2) / 40000.0
                nf2 = noise(cx / 30.0, cy / 30.0) * ((radius - v['rdn']) ** 1.75) / 3500.0

                # Ensure nf2 is real before using in radians
                nf2_real = float(abs(nf2))
                x2 = v['startRadius'] * math.cos(a + nf2_real * 40) \
                     + radius * math.cos(a + nf2_real * 40) * nf1 * vval
                y2 = v['startRadius'] * math.sin(a + nf2_real * 50) \
                     + radius * math.sin(a + nf2_real * 50) * nf1 * vval
                
                points.append((x2, y2))
                radius += ld * v['dRadius'] / (360.0 * v['resolution'])
        return points


class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Perlin Noise Circles wxGUI")

        self.SetSize((1024, 768))

        state = {}
        try:
            state = json.load(open(CONFIG_FILE))
        except Exception:
            pass
        if "size" in state:
            self.SetSize(state["size"])
        if "pos" in state:
            self.SetPosition(state["pos"])
        if state.get("max", False):
            self.Maximize(True)

        splitter = wx.SplitterWindow(self)
        self.canvas = Canvas(splitter)
        self.param = ParamPanel(splitter,
                                on_changed=self.canvas.set_values,
                                initial=state.get("params", DEFAULTS))
        splitter.SplitVertically(self.param, self.canvas, 220)

        # buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        for label, handler in (("Save SVG", self.on_save_svg),
                               ("Save G-code", self.on_save_gcode),
                               ("Save Params", self.on_save_params),
                               ("Load Params", self.on_load_params)):
            b = wx.Button(self, label=label)
            b.Bind(wx.EVT_BUTTON, handler)
            btn_sizer.Add(b, 0, wx.ALL, 5)

        main = wx.BoxSizer(wx.VERTICAL)
        main.Add(splitter, 1, wx.EXPAND)
        main.Add(btn_sizer, 0, wx.ALIGN_CENTER)
        self.SetSizer(main)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.Bind(wx.EVT_SHOW, self.on_show)

    def on_show(self, evt):
        evt.Skip()
        if evt.IsShown():
            self.canvas.Scroll(
                (CANVAS_SIZE - VIEWPORT_SIZE) // 2,
                (CANVAS_SIZE - VIEWPORT_SIZE) // 2)

    def on_save_params(self, evt):
        with wx.FileDialog(self, "Save parameters", wildcard="*.json",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                json.dump(self.param.values, open(dlg.GetPath(), "w"), indent=2)

    def on_load_params(self, evt):
        with wx.FileDialog(self, "Load parameters", wildcard="*.json",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                self.param.set_all(json.load(open(dlg.GetPath())))

    def on_save_svg(self, evt):
        pts = self.canvas.get_paths()
        if not pts:
            return
        with wx.FileDialog(self, "Save SVG", wildcard="*.svg",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
                v = self.canvas.values
                dwg = svgwrite.Drawing(path, size=(CANVAS_SIZE, CANVAS_SIZE))
                g = dwg.g(transform=f"translate({CANVAS_SIZE/2 + v['xOffset']}, "
                                     f"{CANVAS_SIZE/2 + v['yOffset']})")
                g.add(dwg.polyline(pts, stroke="blue",
                                   stroke_width=v['penWidth'], fill="none"))
                dwg.add(g)
                dwg.save()

    def on_save_gcode(self, evt):
        pts = self.canvas.get_paths()
        if not pts:
            return
        with wx.FileDialog(self, "Save G-code", wildcard="*.nc",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
                v = self.canvas.values
                header = (
                    f"( Noise circles )\n"
                    f"( startRadius {v['startRadius']}  maxCircles {v['maxCircles']}  "
                    f"resolution {v['resolution']}  dRadius {v['dRadius']}  "
                    f"rdn {v['rdn']}  xOffset {v['xOffset']}  yOffset {v['yOffset']}  "
                    f"nSeed {v['nSeed']}  penWidth {v['penWidth']}  "
                    f"lineDistance {v['lineDistance']} )\n"
                    "G54\nG90\nG00 Z5\nT01 M06\nG01 F1500\n"
                )
                first = f"G00 X{pts[0][0]:.3f} Y{pts[0][1]:.3f}\nG01 Z-3\n"
                body = "\n".join([f"G01 X{x:.3f} Y{y:.3f}" for x, y in pts[1:]])
                footer = "\nG00 Z2\nT00 M06\nM30\n"
                with open(path, "w") as f:
                    f.write(header + first + body + footer)

    def on_close(self, evt):
        json.dump({
            "size": list(self.GetSize()),
            "pos": list(self.GetPosition()),
            "max": self.IsMaximized(),
            "params": self.param.values,
        }, open(CONFIG_FILE, "w"), indent=2)
        evt.Skip()


if __name__ == "__main__":
    app = wx.App(False)
    MainFrame().Show()
    app.MainLoop()
