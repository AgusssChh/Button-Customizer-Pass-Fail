# Button Customizer + Pass/Fail — Configuration

## Buttons

**Number of answer buttons** chooses which real Anki ease values remain visible:

- **2:** Fail → ease 1 (Again), Pass → ease 3 (Good)
- **3:** Again → 1, Hard → 2, Good → 3
- **4:** Again → 1, Hard → 2, Good → 3, Easy → 4

The add-on does not replace Anki's scheduler. In 2-button mode, the visible Pass action is submitted as ease 3 / Good. Hidden keyboard answers are normalized to the same available actions.

**Use custom answer-button names** controls the four label fields. Names are stored independently of the selected button count so switching between 2, 3, and 4 buttons does not erase them.

## Colors

Light and dark mode have independent background and text colors for each ease. The add-on reads the current Anki theme and selects the corresponding set.

**Color mode**:

- **Default:** leave Anki/theme colors unchanged.
- **Custom text only:** custom text colors, normal Anki/theme backgrounds.
- **Custom text + background:** custom text and background colors all the time.
- **Custom colors on hover:** custom text color normally, custom background on hover.

## Layout

All dimensions are direct pixel values. They are not restricted to S/M/L presets.

**Answer-button height / width / font size** control the reviewer buttons. The configured height is treated as a minimum height so Anki's next-review estimate can remain visible instead of being clipped.

**Show-answer button width** controls Anki's button shown before the answer is revealed.

**Bottom bar minimum height** controls the minimum height of the reviewer bottom bar. `Automatic` leaves the height to Anki. Increase it when the next-review information above/inside the answer area is clipped; values around 55–70 px are a useful starting point.

**Border radius** changes button corner rounding.

**Style the reviewer buttons and bottom-bar controls** enables the KING-derived visual styling. The bottom-bar minimum-height setting remains independent.

## Outline

The outline uses the current reviewer button markup and `:focus`, `:focus-visible`, and `:active`. It does not depend on the legacy KING selector that stopped working reliably on newer Anki versions.

## Confirmation

The confirmation popup appears over the selected answer. Its colors follow the corresponding light/dark button colors, and X/Y offsets adjust its position.

The popup is implemented directly with Qt for compatibility with current Anki versions; it no longer depends on the removed `aqt.utils.tooltipWithColour` helper.

## Preview

The preview is local to the settings window and is not saved by itself. It shows each currently enabled answer button, its label, its colors, and an example next-review interval above that button. The intervals are illustrative only.

Use **Refresh Preview** to redraw the preview explicitly; controls also update it automatically.

## Documentation pane

**Show configuration documentation** toggles the side-by-side `config.md` pane. Hiding it reduces the required window width, while showing it gives the documentation more horizontal space.

Long explanatory text in the settings window and documentation pane wraps at the available width.

## Configuration synchronization

The Tools window reloads the persisted add-on configuration every time it opens. It reads Anki's stored add-on configuration directly from `meta.json`, so changes made through **Tools → Add-ons → Button Customizer + Pass/Fail → Config** are reflected in the custom settings window.

The add-on also registers Anki's configuration-updated callback, so a change made in the built-in JSON editor updates the active reviewer without requiring a restart.

The bundled `config.json` contains the add-on's defaults; user overrides are stored by Anki in `meta.json`.

## Source

https://github.com/AgusssChh/Button-Customizer-Pass-Fail
