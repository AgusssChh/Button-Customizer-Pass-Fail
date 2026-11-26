from __future__ import annotations

from aqt.qt import *

from . import config

COLORS = [
    ("Again", "again"),
    ("Hard", "hard"),
    ("Good", "good"),
    ("Easy", "easy"),
]


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pass/Fail + KING Button Customizer")
        self.setMinimumSize(760, 720)
        self.c = config.all()
        self.fields = {}
        self._build()
        self._load()

    def _build(self):
        root = QVBoxLayout(self)
        tabs = QTabWidget(self)
        root.addWidget(tabs)

        general = QWidget()
        gl = QFormLayout(general)
        self.button_count = QComboBox()
        self.button_count.addItem("2 — Fail / Pass", 2)
        self.button_count.addItem("3 — Again / Hard / Good", 3)
        self.button_count.addItem("4 — Again / Hard / Good / Easy", 4)
        gl.addRow("Number of answer buttons", self.button_count)
        self.enable_names = QCheckBox("Use custom answer-button names")
        gl.addRow(self.enable_names)
        for key, label, placeholder in [
            ("again_name", "Again / Fail name", "Fail"),
            ("hard_name", "Hard name", "Hard"),
            ("good_name", "Good / Pass name", "Pass"),
            ("easy_name", "Easy name", "Easy"),
        ]:
            e = QLineEdit(); e.setPlaceholderText(placeholder)
            self.fields[key] = e
            gl.addRow(label, e)

        self.color_mode = QComboBox()
        for text, value in [
            ("Default — no custom button colors", "default"),
            ("Text only", "text"),
            ("Text + background", "colors"),
            ("Text + background on hover", "hover"),
        ]:
            self.color_mode.addItem(text, value)
        gl.addRow("Color mode", self.color_mode)

        layout_tab = QWidget()
        ll = QFormLayout(layout_tab)
        self.fields["border_radius"] = QSpinBox(); self.fields["border_radius"].setRange(0, 50)
        self.fields["button_height"] = QComboBox(); self.fields["button_height"].addItems(["S", "M", "L"])
        self.fields["button_width"] = QComboBox(); self.fields["button_width"].addItems(["S", "M", "L"])
        self.fields["button_font_size"] = QComboBox(); self.fields["button_font_size"].addItems(["S", "M", "L"])
        self.fields["answer_button_width"] = QComboBox(); self.fields["answer_button_width"].addItem("Full", "full"); self.fields["answer_button_width"].addItem("Normal", "normal")
        ll.addRow("Border radius", self.fields["border_radius"])
        ll.addRow("Button height", self.fields["button_height"])
        ll.addRow("Button width", self.fields["button_width"])
        ll.addRow("Font size", self.fields["button_font_size"])
        ll.addRow("Show-answer button width", self.fields["answer_button_width"])
        self.style_main = QCheckBox("Style the entire reviewer bottom bar")
        ll.addRow(self.style_main)

        colors_tab = QWidget(); cl = QVBoxLayout(colors_tab)
        cl.addWidget(QLabel("Background and text colors are independent for light and dark mode."))
        color_grid = QGridLayout(); cl.addLayout(color_grid)
        color_grid.addWidget(QLabel("Button"), 0, 0)
        color_grid.addWidget(QLabel("Light background"), 0, 1)
        color_grid.addWidget(QLabel("Light text"), 0, 2)
        color_grid.addWidget(QLabel("Dark background"), 0, 3)
        color_grid.addWidget(QLabel("Dark text"), 0, 4)
        for row, (label, suffix) in enumerate(COLORS, start=1):
            color_grid.addWidget(QLabel(label), row, 0)
            for col, prefix in enumerate(["light_background", "light_text", "dark_background", "dark_text"], start=1):
                key = f"{prefix}_{suffix}"
                button = QPushButton(); button.setMinimumWidth(120)
                button.clicked.connect(lambda _, k=key, b=button: self._pick_color(k, b))
                self.fields[key] = button
                color_grid.addWidget(button, row, col)
        cl.addStretch(1)

        outline_tab = QWidget(); ol = QFormLayout(outline_tab)
        self.outline = QCheckBox("Show a focus/selection outline around the selected answer button")
        self.outline_width = QSpinBox(); self.outline_width.setRange(1, 8)
        self.outline_offset = QSpinBox(); self.outline_offset.setRange(0, 8)
        ol.addRow(self.outline)
        ol.addRow("Outline width", self.outline_width)
        ol.addRow("Outline offset", self.outline_offset)
        ol.addRow(QLabel("On Anki 2.1.55+ the original KING selector no longer controls this. This version uses :focus/:focus-visible on the current answer-button markup, plus :active as a fallback."))

        confirm_tab = QWidget(); fl = QFormLayout(confirm_tab)
        self.confirmation = QCheckBox("Show answer confirmation tooltip")
        self.confirmation_time = QSpinBox(); self.confirmation_time.setRange(50, 5000); self.confirmation_time.setSuffix(" ms")
        self.confirmation_x = QSpinBox(); self.confirmation_x.setRange(-500, 500)
        self.confirmation_y = QSpinBox(); self.confirmation_y.setRange(-500, 500)
        fl.addRow(self.confirmation)
        fl.addRow("Tooltip time", self.confirmation_time)
        fl.addRow("X offset", self.confirmation_x)
        fl.addRow("Y offset", self.confirmation_y)

        tabs.addTab(general, "Buttons")
        tabs.addTab(layout_tab, "Layout")
        tabs.addTab(colors_tab, "Colors")
        tabs.addTab(outline_tab, "Outline")
        tabs.addTab(confirm_tab, "Confirmation")

        preview_box = QGroupBox("Preview")
        pv = QHBoxLayout(preview_box)
        self.preview_buttons = []
        for _ in range(4):
            b = QPushButton()
            b.setMinimumHeight(34)
            pv.addWidget(b)
            self.preview_buttons.append(b)
        root.addWidget(preview_box)
        self.button_count.currentIndexChanged.connect(self._refresh_preview)
        self.enable_names.stateChanged.connect(self._refresh_preview)
        self.color_mode.currentIndexChanged.connect(self._refresh_preview)

        row = QHBoxLayout()
        save = QPushButton("Save")
        cancel = QPushButton("Cancel")
        apply = QPushButton("Apply")
        save.clicked.connect(self._save_and_close)
        apply.clicked.connect(self._save)
        cancel.clicked.connect(self.reject)
        row.addStretch(1); row.addWidget(apply); row.addWidget(cancel); row.addWidget(save)
        root.addLayout(row)

    def _load(self):
        c = self.c
        self.button_count.setCurrentIndex({2: 0, 3: 1, 4: 2}.get(int(c.get("button_count", 2)), 0))
        self.enable_names.setChecked(bool(c.get("enable_names", True)))
        for key in ["again_name", "hard_name", "good_name", "easy_name"]:
            self.fields[key].setText(str(c.get(key, "")))
        mode = str(c.get("color_mode", "colors"))
        idx = self.color_mode.findData(mode); self.color_mode.setCurrentIndex(max(0, idx))
        for key in ["border_radius"]:
            self.fields[key].setValue(int(c.get(key, 15)))
        for key in ["button_height", "button_width", "button_font_size"]:
            idx = self.fields[key].findText(str(c.get(key, "S")).upper())
            self.fields[key].setCurrentIndex(max(0, idx))
        idx = self.fields["answer_button_width"].findData(str(c.get("answer_button_width", "full")).lower()); self.fields["answer_button_width"].setCurrentIndex(max(0, idx))
        self.style_main.setChecked(bool(c.get("style_main_screen_buttons", True)))
        for key, _ in [(k, s) for _, s in COLORS for k in [f"light_background_{s}", f"light_text_{s}", f"dark_background_{s}", f"dark_text_{s}"]]:
            self._set_color_button(key)
        self.outline.setChecked(bool(c.get("outline", True)))
        self.outline_width.setValue(int(c.get("outline_width", 2)))
        self.outline_offset.setValue(int(c.get("outline_offset", 2)))
        self.confirmation.setChecked(bool(c.get("confirmation", True)))
        self.confirmation_time.setValue(int(c.get("confirmation_time", 450)))
        self.confirmation_x.setValue(int(c.get("confirmation_x_offset", 0)))
        self.confirmation_y.setValue(int(c.get("confirmation_y_offset", 0)))
        self._refresh_preview()

    def _set_color_button(self, key: str):
        b = self.fields[key]
        value = str(self.c.get(key, "#000000"))
        b.setText(value)
        b.setStyleSheet(f"background:{value}; color:{'#000' if _luma(value) > 0.55 else '#fff'};")

    def _pick_color(self, key, button):
        initial = QColor(str(self.c.get(key, "#000000")))
        color = QColorDialog.getColor(initial, self, f"Choose {key}")
        if not color.isValid():
            return
        self.c[key] = color.name()
        button.setText(self.c[key])
        button.setStyleSheet(f"background:{self.c[key]}; color:{'#000' if _luma(self.c[key]) > 0.55 else '#fff'};")
        self._refresh_preview()

    def _collect(self):
        self.c["button_count"] = int(self.button_count.currentData())
        self.c["enable_names"] = self.enable_names.isChecked()
        for key in ["again_name", "hard_name", "good_name", "easy_name"]:
            self.c[key] = self.fields[key].text().strip() or config.DEFAULTS[key]
        self.c["color_mode"] = self.color_mode.currentData()
        self.c["border_radius"] = self.fields["border_radius"].value()
        for key in ["button_height", "button_width", "button_font_size"]:
            self.c[key] = self.fields[key].currentText()
        self.c["answer_button_width"] = self.fields["answer_button_width"].currentData()
        self.c["style_main_screen_buttons"] = self.style_main.isChecked()
        self.c["outline"] = self.outline.isChecked()
        self.c["outline_width"] = self.outline_width.value()
        self.c["outline_offset"] = self.outline_offset.value()
        self.c["confirmation"] = self.confirmation.isChecked()
        self.c["confirmation_time"] = self.confirmation_time.value()
        self.c["confirmation_x_offset"] = self.confirmation_x.value()
        self.c["confirmation_y_offset"] = self.confirmation_y.value()
        for _, suffix in COLORS:
            for prefix in ["light_background", "light_text", "dark_background", "dark_text"]:
                key = f"{prefix}_{suffix}"
                self.c[key] = self.fields[key].text()
        return self.c

    def _save(self):
        config.update(self._collect())
        from .main import apply_settings_now
        apply_settings_now()

    def _save_and_close(self):
        self._save()
        self.accept()

    def _refresh_preview(self, *_):
        self._collect()
        count = int(self.c.get("button_count", 2))
        names = {
            1: self.c.get("again_name", "Fail"),
            2: self.c.get("hard_name", "Hard"),
            3: self.c.get("good_name", "Pass"),
            4: self.c.get("easy_name", "Easy"),
        }
        eases = (1, 3) if count == 2 else (1, 2, 3) if count == 3 else (1, 2, 3, 4)
        shown = set(eases)
        for i, b in enumerate(self.preview_buttons, start=1):
            b.setVisible(i <= count)
            if i <= count:
                ease = eases[i - 1]
                key = {1: "again", 2: "hard", 3: "good", 4: "easy"}[ease]
                b.setText(names[ease] if self.c.get("enable_names", True) else ["", "Again", "Hard", "Good", "Easy"][ease])
                bg = self.c.get(f"light_background_{key}", "#ddd")
                fg = self.c.get(f"light_text_{key}", "#000")
                mode = self.c.get("color_mode", "colors")
                b.setStyleSheet((f"color:{fg};" + (f"background:{bg};" if mode == "colors" else "")))
        for i in range(1, 5):
            self.fields[f"light_background_{['again','hard','good','easy'][i-1]}"].setEnabled(i in shown)
            self.fields[f"light_text_{['again','hard','good','easy'][i-1]}"].setEnabled(i in shown)
            self.fields[f"dark_background_{['again','hard','good','easy'][i-1]}"].setEnabled(i in shown)
            self.fields[f"dark_text_{['again','hard','good','easy'][i-1]}"].setEnabled(i in shown)


def _luma(value: str) -> float:
    try:
        value = value.lstrip('#')
        if len(value) != 6:
            return 0.5
        r, g, b = [int(value[i:i+2], 16) / 255 for i in (0, 2, 4)]
        return 0.2126*r + 0.7152*g + 0.0722*b
    except Exception:
        return 0.5
