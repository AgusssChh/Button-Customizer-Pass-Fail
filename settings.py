from __future__ import annotations

from pathlib import Path

from aqt.qt import *

from . import config

COLORS = [
    ("Again / Fail", "again"),
    ("Hard", "hard"),
    ("Good / Pass", "good"),
    ("Easy", "easy"),
]
COLOR_PREFIXES = ["light_background", "light_text", "dark_background", "dark_text"]
EASE_NAMES = {1: "Again", 2: "Hard", 3: "Good", 4: "Easy"}
EASE_KEYS = {1: "again", 2: "hard", 3: "good", 4: "easy"}
PREVIEW_TIMES = {
    2: ["10m", "8h"],
    3: ["10m", "8h", "2d"],
    4: ["10m", "1h", "2d", "5d"],
}


def _wrap_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setWordWrap(True)
    label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    return label


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Button Customizer + Pass/Fail")
        self.resize(1100, 800)
        self.setMinimumSize(980, 700)
        self.c = config.reload()
        self.fields = {}
        self.preview_buttons: list[QPushButton] = []
        self.preview_times: list[QLabel] = []
        self._building = True
        self._build()
        self._load()
        self._building = False
        self._update_docs_visibility()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(6)

        top = QHBoxLayout()
        self.docs_toggle = QCheckBox("Show configuration documentation")
        self.docs_toggle.setChecked(True)
        self.docs_toggle.toggled.connect(self._update_docs_visibility)
        top.addWidget(self.docs_toggle)
        top.addStretch(1)
        root.addLayout(top)

        splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.splitter = splitter
        root.addWidget(splitter, 1)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        tabs = QTabWidget(left)
        left_layout.addWidget(tabs, 1)

        buttons_tab = QWidget()
        bl = QVBoxLayout(buttons_tab)
        form = QFormLayout()
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.button_count = QComboBox()
        self.button_count.addItem("2 — Fail / Pass", 2)
        self.button_count.addItem("3 — Again / Hard / Good", 3)
        self.button_count.addItem("4 — Again / Hard / Good / Easy", 4)
        form.addRow("Number of answer buttons", self.button_count)
        self.enable_names = QCheckBox("Use custom answer-button names")
        form.addRow(self.enable_names)
        for key, label, placeholder in [
            ("again_name", "Again / Fail name", "Fail"),
            ("hard_name", "Hard name", "Hard"),
            ("good_name", "Good / Pass name", "Pass"),
            ("easy_name", "Easy name", "Easy"),
        ]:
            edit = QLineEdit()
            edit.setPlaceholderText(placeholder)
            self.fields[key] = edit
            form.addRow(label, edit)
        self.color_mode = QComboBox()
        for text, value in [
            ("Default — Anki/theme colors", "default"),
            ("Custom text only", "text"),
            ("Custom text + background", "colors"),
            ("Custom colors on hover", "hover"),
        ]:
            self.color_mode.addItem(text, value)
        form.addRow("Color mode", self.color_mode)
        bl.addLayout(form)

        color_group = QGroupBox("Independent light/dark colors")
        cg = QGridLayout(color_group)
        headers = ["Button", "Light background", "Light text", "Dark background", "Dark text"]
        for col, header in enumerate(headers):
            header_label = QLabel(header)
            header_label.setWordWrap(True)
            cg.addWidget(header_label, 0, col)
        for row, (label, suffix) in enumerate(COLORS, start=1):
            cg.addWidget(QLabel(label), row, 0)
            for col, prefix in enumerate(COLOR_PREFIXES, start=1):
                key = f"{prefix}_{suffix}"
                button = QPushButton()
                button.setMinimumWidth(94)
                button.clicked.connect(lambda _, k=key, b=button: self._pick_color(k, b))
                self.fields[key] = button
                cg.addWidget(button, row, col)
        bl.addWidget(color_group)
        bl.addStretch(1)
        tabs.addTab(buttons_tab, "Buttons")

        layout_tab = QWidget()
        ll = QFormLayout(layout_tab)
        ll.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        for key, label, lo, hi, suffix in [
            ("button_height_px", "Answer-button height", 1, 240, " px"),
            ("button_width_px", "Answer-button width", 1, 500, " px"),
            ("button_font_size_px", "Answer-button font size", 1, 96, " px"),
            ("answer_button_width_px", "Show-answer button width", 1, 1600, " px"),
            ("bottom_bar_height_px", "Bottom bar minimum height", 0, 500, " px"),
            ("border_radius", "Border radius", 0, 100, " px"),
        ]:
            spin = QSpinBox()
            spin.setRange(lo, hi)
            spin.setSuffix(suffix)
            if key == "bottom_bar_height_px":
                spin.setSpecialValueText("Automatic")
            self.fields[key] = spin
            ll.addRow(label, spin)
        ll.addRow(
            _wrap_label(
                "The bottom-bar value controls the minimum height of the current Anki reviewer bottom bar. "
                "Use it together with the automatic button-height behavior so the next-review estimates are not clipped."
            )
        )
        self.style_main = QCheckBox("Style the reviewer buttons and bottom-bar controls")
        ll.addRow(self.style_main)
        tabs.addTab(layout_tab, "Layout")

        outline_tab = QWidget()
        ol = QFormLayout(outline_tab)
        self.outline = QCheckBox("Show a focus/selection outline around the selected answer button")
        self.outline_width = QSpinBox(); self.outline_width.setRange(1, 12); self.outline_width.setSuffix(" px")
        self.outline_offset = QSpinBox(); self.outline_offset.setRange(0, 12); self.outline_offset.setSuffix(" px")
        ol.addRow(self.outline)
        ol.addRow("Outline width", self.outline_width)
        ol.addRow("Outline offset", self.outline_offset)
        ol.addRow(
            _wrap_label(
                "The original KING focus selector stopped working reliably after Anki 2.1.55. "
                "This version targets the current reviewer answer buttons with :focus, :focus-visible, and :active."
            )
        )
        tabs.addTab(outline_tab, "Outline")

        confirmation_tab = QWidget()
        fl = QFormLayout(confirmation_tab)
        self.confirmation = QCheckBox("Show answer confirmation popup")
        self.confirmation_time = QSpinBox(); self.confirmation_time.setRange(50, 5000); self.confirmation_time.setSuffix(" ms")
        self.confirmation_x = QSpinBox(); self.confirmation_x.setRange(-500, 500); self.confirmation_x.setSuffix(" px")
        self.confirmation_y = QSpinBox(); self.confirmation_y.setRange(-500, 500); self.confirmation_y.setSuffix(" px")
        fl.addRow(self.confirmation)
        fl.addRow("Popup time", self.confirmation_time)
        fl.addRow("X offset", self.confirmation_x)
        fl.addRow("Y offset", self.confirmation_y)
        fl.addRow(
            _wrap_label(
                "The popup is implemented with Qt directly because aqt.utils.tooltipWithColour was removed from newer Anki versions."
            )
        )
        tabs.addTab(confirmation_tab, "Confirmation")

        splitter.addWidget(left)

        self.docs = QTextBrowser()
        self.docs.setOpenExternalLinks(True)
        self.docs.setReadOnly(True)
        self.docs.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.docs.setWordWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
        self.docs.setMinimumWidth(380)
        self._load_docs(self.docs)
        splitter.addWidget(self.docs)
        splitter.setChildrenCollapsible(True)
        splitter.setCollapsible(1, True)
        splitter.setSizes([620, 450])
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        preview = QGroupBox("Preview")
        pv = QVBoxLayout(preview)
        top = QHBoxLayout()
        top.addWidget(QLabel("Preview theme"))
        self.preview_theme = QComboBox()
        self.preview_theme.addItem("Light", False)
        self.preview_theme.addItem("Dark", True)
        top.addWidget(self.preview_theme)
        top.addStretch(1)
        refresh = QPushButton("Refresh Preview")
        refresh.clicked.connect(self._refresh_preview)
        top.addWidget(refresh)
        pv.addLayout(top)

        self.preview_bar = QFrame()
        self.preview_bar.setFrameShape(QFrame.Shape.StyledPanel)
        bar_layout = QVBoxLayout(self.preview_bar)
        bar_layout.setContentsMargins(10, 8, 10, 8)
        preview_row = QHBoxLayout()
        preview_row.setSpacing(8)
        preview_row.addStretch(1)
        for _ in range(4):
            column_widget = QWidget()
            column = QVBoxLayout(column_widget)
            column.setContentsMargins(0, 0, 0, 0)
            column.setSpacing(3)
            t = QLabel()
            t.setAlignment(Qt.AlignmentFlag.AlignCenter)
            t.setMinimumHeight(18)
            b = QPushButton()
            b.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.preview_times.append(t)
            self.preview_buttons.append(b)
            column.addWidget(t)
            column.addWidget(b)
            preview_row.addWidget(column_widget)
        preview_row.addStretch(1)
        bar_layout.addLayout(preview_row)
        pv.addWidget(self.preview_bar)
        root.addWidget(preview, 0)

        actions = QHBoxLayout()
        actions.addWidget(_wrap_label("Changes are previewed locally. Apply/Save writes them to Anki's add-on configuration."), 1)
        reload_button = QPushButton("Reload Stored Settings")
        reload_button.clicked.connect(self._reload_stored)
        actions.addWidget(reload_button)
        apply_button = QPushButton("Apply")
        cancel = QPushButton("Cancel")
        save = QPushButton("Save")
        apply_button.clicked.connect(self._save)
        cancel.clicked.connect(self.reject)
        save.clicked.connect(self._save_and_close)
        actions.addWidget(apply_button)
        actions.addWidget(cancel)
        actions.addWidget(save)
        root.addLayout(actions)

        self._wire_preview_signals()

    def _update_docs_visibility(self, checked: bool | None = None):
        if checked is None:
            checked = self.docs_toggle.isChecked()
        self.docs.setVisible(bool(checked))
        if checked:
            self.setMinimumWidth(980)
            if not self._building and self.width() < 1050:
                self.resize(1100, self.height())
            self.splitter.setSizes([620, 450])
        else:
            self.setMinimumWidth(760)
            if not self._building and self.width() > 880:
                self.resize(840, self.height())
            self.splitter.setSizes([900, 0])

    def _wire_preview_signals(self):
        for key in ["again_name", "hard_name", "good_name", "easy_name"]:
            self.fields[key].textChanged.connect(self._preview_changed)
        self.button_count.currentIndexChanged.connect(self._preview_changed)
        self.enable_names.stateChanged.connect(self._preview_changed)
        self.color_mode.currentIndexChanged.connect(self._preview_changed)
        for key in [
            "button_height_px", "button_width_px", "button_font_size_px",
            "answer_button_width_px", "bottom_bar_height_px", "border_radius",
        ]:
            self.fields[key].valueChanged.connect(self._preview_changed)
        self.style_main.stateChanged.connect(self._preview_changed)
        self.outline.stateChanged.connect(self._preview_changed)
        self.outline_width.valueChanged.connect(self._preview_changed)
        self.outline_offset.valueChanged.connect(self._preview_changed)
        self.confirmation.stateChanged.connect(self._preview_changed)
        self.confirmation_time.valueChanged.connect(self._preview_changed)
        self.preview_theme.currentIndexChanged.connect(self._preview_changed)

    def _preview_changed(self, *_):
        if not self._building:
            self._refresh_preview()

    def _load_docs(self, browser: QTextBrowser):
        path = Path(__file__).with_name("config.md")
        try:
            markdown = path.read_text(encoding="utf-8")
            browser.document().setMarkdown(markdown)
        except Exception:
            browser.setPlainText("Configuration documentation could not be loaded.")

    def _load(self):
        c = self.c
        self.button_count.setCurrentIndex({2: 0, 3: 1, 4: 2}.get(int(c.get("button_count", 2)), 0))
        self.enable_names.setChecked(bool(c.get("enable_names", True)))
        for key in ["again_name", "hard_name", "good_name", "easy_name"]:
            self.fields[key].setText(str(c.get(key, config.DEFAULTS[key])))

        mode = str(c.get("color_mode", "colors"))
        idx = self.color_mode.findData(mode)
        self.color_mode.setCurrentIndex(idx if idx >= 0 else 0)
        for key in [
            "button_height_px", "button_width_px", "button_font_size_px",
            "answer_button_width_px", "bottom_bar_height_px", "border_radius",
        ]:
            self.fields[key].setValue(int(c.get(key, config.DEFAULTS[key])))
        self.style_main.setChecked(bool(c.get("style_main_screen_buttons", True)))

        for _, suffix in COLORS:
            for prefix in COLOR_PREFIXES:
                self._set_color_button(f"{prefix}_{suffix}")

        self.outline.setChecked(bool(c.get("outline", True)))
        self.outline_width.setValue(int(c.get("outline_width", 2)))
        self.outline_offset.setValue(int(c.get("outline_offset", 2)))
        self.confirmation.setChecked(bool(c.get("confirmation", True)))
        self.confirmation_time.setValue(int(c.get("confirmation_time", 450)))
        self.confirmation_x.setValue(int(c.get("confirmation_x_offset", 0)))
        self.confirmation_y.setValue(int(c.get("confirmation_y_offset", 0)))
        self._refresh_preview()

    def _reload_stored(self):
        self.c = config.reload()
        self._load()

    def _set_color_button(self, key: str):
        value = str(self.c.get(key, config.DEFAULTS[key])) or config.DEFAULTS[key]
        button = self.fields[key]
        button.setText(value)
        button.setStyleSheet(f"background:{value}; color:{'#000' if _luma(value) > 0.55 else '#fff'};")

    def _pick_color(self, key, button):
        initial = QColor(str(self.c.get(key, config.DEFAULTS[key])))
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
        for key in [
            "button_height_px", "button_width_px", "button_font_size_px",
            "answer_button_width_px", "bottom_bar_height_px", "border_radius",
        ]:
            self.c[key] = self.fields[key].value()
        self.c["style_main_screen_buttons"] = self.style_main.isChecked()
        self.c["outline"] = self.outline.isChecked()
        self.c["outline_width"] = self.outline_width.value()
        self.c["outline_offset"] = self.outline_offset.value()
        self.c["confirmation"] = self.confirmation.isChecked()
        self.c["confirmation_time"] = self.confirmation_time.value()
        self.c["confirmation_x_offset"] = self.confirmation_x.value()
        self.c["confirmation_y_offset"] = self.confirmation_y.value()
        for _, suffix in COLORS:
            for prefix in COLOR_PREFIXES:
                key = f"{prefix}_{suffix}"
                self.c[key] = self.fields[key].text() or config.DEFAULTS[key]
        return self.c

    def _save(self):
        config.update(self._collect())
        from .main import apply_settings_now
        apply_settings_now()
        self.c = config.reload()
        self._load()

    def _save_and_close(self):
        self._save()
        self.accept()

    def _refresh_preview(self, *_):
        self._collect()
        count = int(self.c.get("button_count", 2))
        eases = (1, 3) if count == 2 else (1, 2, 3) if count == 3 else (1, 2, 3, 4)
        dark = bool(self.preview_theme.currentData())
        mode = str(self.c.get("color_mode", "colors")).lower()
        height = max(1, int(self.c.get("button_height_px", 25)))
        width = max(1, int(self.c.get("button_width_px", 42)))
        font = max(1, int(self.c.get("button_font_size_px", 14)))
        radius = max(0, int(self.c.get("border_radius", 15)))
        min_bar = max(0, int(self.c.get("bottom_bar_height_px", 0)))
        self.preview_bar.setMinimumHeight(max(96, min_bar) if min_bar else 96)
        self.preview_bar.setStyleSheet("background:#202124; color:#f1f3f4;" if dark else "")

        names = {
            1: self.c.get("again_name", "Fail"),
            2: self.c.get("hard_name", "Hard"),
            3: self.c.get("good_name", "Pass"),
            4: self.c.get("easy_name", "Easy"),
        }
        palette = "dark" if dark else "light"
        times = PREVIEW_TIMES[count]
        for i, (button, time_label) in enumerate(zip(self.preview_buttons, self.preview_times), start=1):
            visible = i <= count
            button.setVisible(visible)
            time_label.setVisible(visible)
            if not visible:
                continue
            ease = eases[i - 1]
            key = EASE_KEYS[ease]
            bg = self.c.get(f"{palette}_background_{key}", "#ddd")
            fg = self.c.get(f"{palette}_text_{key}", "#000")
            button.setText(names[ease] if self.c.get("enable_names", True) else EASE_NAMES[ease])
            button.setFixedSize(width, max(height, 22))
            time_label.setText(times[i - 1])
            time_label.setStyleSheet(f"color:{fg}; font-size:11px; background:transparent;")
            base = f"font-size:{font}px; border-radius:{radius}px; min-height:{height}px;"
            if mode == "default":
                button.setStyleSheet(base)
            elif mode == "text":
                button.setStyleSheet(base + f"color:{fg};")
            elif mode == "hover":
                button.setStyleSheet(base + f"color:{fg};")
            else:
                button.setStyleSheet(base + f"color:{fg}; background:{bg};")


def _luma(value: str) -> float:
    try:
        value = value.lstrip('#')
        if len(value) != 6:
            return 0.5
        r, g, b = [int(value[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    except Exception:
        return 0.5
