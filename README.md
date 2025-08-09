# PerlinNoiseCircle_wxPython  
*Create hypnotic, ever-expanding circle art from Perlin noise — right on your desktop.*
### This app is an adaptation in Python, based on the work of Stoli123 who has written it in Processing5's Java
https://editor.p5js.org/Stoli123/sketches/ifMMJBDca
---

![preview](PerlinNoiseCircles_wx(1024x768).png)  
*(example output, 1024 × 768 window)*

---

## ✨ What it does

PerlinNoiseCircle_wxPython turns a simple mathematical seed into mesmerizing, organic ring patterns.  
Each ring is placed using 2-D Perlin noise, giving every run a unique, flowing appearance that looks hand-drawn yet is 100 % deterministic.

- **Real-time parameter control** – sliders update the drawing instantly  
- **Export to SVG** – vector-perfect for posters, stickers, or laser-cutting  
- **Export to G-code** – drop the generated `.nc` file straight onto many CNC mills or plotters  
- **Save / load presets** – keep your favourite styles as JSON snippets  
- **Cross-platform** – pure Python + wxPython; runs on Windows, macOS, Linux  

---
## 🚀 Windows Quick start
simply run PerlinNoiseCircle_wx.exe

## 🚀 Quick start

```bash
git clone https://github.com/DanAla/PerlinNoiseCircle_wxPython.git
cd PerlinNoiseCircle_wxPython
python -m venv venv
source venv/bin/activate      # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python PerlinNoiseCircle_wx.py
```

---

## 🎛️ Controls

| Parameter        | Effect |
|------------------|--------|
| startRadius      | radius of the very first circle |
| maxCircles       | how many rings to draw |
| resolution       | degrees between line segments (1 = 1°) |
| dRadius          | growth step per segment |
| rdn              | randomness damping (higher = smoother) |
| x / y Offset     | translate the entire drawing |
| nSeed            | noise seed (0 → random) |
| penWidth         | stroke thickness in SVG / G-code |
| lineDistance     | distance multiplier between rings |

---

## 📁 Files

- `PerlinNoiseCircle_wx.py` – the application (single-file)  
- `default_params.json` – fallback parameters (auto-created if missing)  
- `noise_circles_state.json` – remembers window geometry & last settings (created on exit)

---

## 🛠️ Requirements

- Python ≥ 3.8  
- `wxPython`  
- `noise` (Perlin-noise bindings)  
- `svgwrite`

```text
wxPython>=4.2
noise>=1.2
svgwrite>=1.4
```

---

## 📦 Export formats

| Format | Contents | Typical use |
|--------|----------|-------------|
| `.svg` | one `<polyline>` per ring, blue stroke, no fill | Inkscape, Illustrator, web |
| `.nc`  | G-code snippet for GRBL / FluidNC / Marlin / Mach3 | Pen-plotter, CNC engraver |

---

## 🧪 Tips & tricks

- **Smooth gradients** – lower *resolution* and raise *rdn*  
- **Jagged chaos** – raise *resolution* and decrease *rdn*  
- **Perfect loops** – duplicate seeds create identical pieces; share a preset JSON with friends  
- **Large wall art** – set *maxCircles* to 2000, *startRadius* to 5, export SVG and scale freely

---

## 📜 License

BSD3 – do what you like, attribution appreciated.

---

Made with ❤️ and Perlin noise.
