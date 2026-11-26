Patch 1.0.1: fixed Anki 26.x typed-hook startup failure and hardened dark-mode/outline selectors.

# Pass/Fail + KING Button Customizer

A single GPL-3.0 Anki add-on combining the core reviewer behavior of lambdadog's **Pass/Fail 2** with the reviewer-button customization features of AnKing-VIP's **The KING of Button Add-ons**.

## Added functionality

- Choose 2, 3, or 4 reviewer answer buttons.
  - 2: Again/Fail + Good/Pass (ease 1 + ease 3)
  - 3: Again + Hard + Good (ease 1 + 2 + 3)
  - 4: Again + Hard + Good + Easy (ease 1 + 2 + 3 + 4)
- Independent background and text colors for each button in light and dark mode.
- Settings UI under **Tools → Pass/Fail + KING Button Customizer…**.
- Live application of most settings without restarting Anki.
- Confirmation tooltip, sizing, border radius, hover mode, and reviewer-bottom styling retained from KING.
- Pass/Fail shortcut behavior retained: in 2-button mode, any non-Again answer key is normalized to Good/ease 3; in 3-button mode ease 4 is normalized to Good/ease 3.
- Current reviewer hooks are used instead of the old legacy wrapping path on modern Anki.

## 26.09.4+fsrs7 compatibility

The target fork's reviewer still provides `reviewer_will_init_answer_buttons` and `reviewer_will_answer_card`. Its current answer-button HTML uses `data-ease="1..4"`, which this add-on targets directly. The add-on does not replace `_answerButtonList()` or `_answerCard()` and therefore leaves the fork's FSRS-7/RWKV scheduling implementation in control of grading.

## Outline repair

The original KING add-on exposes an `outline` option, but its implementation only changes the CSS `outline` property on the base button rule. On newer Anki builds this does not reproduce the old selected/focus ring reliably. This fork replaces that with explicit `:focus`, `:focus-visible`, and `:active` rules against the current answer buttons, with configurable width and offset.

## Conflict handling

The manifest declares conflicts with the original PassFail2 package and KING package ID. Do not run the original add-ons alongside this merged version; their reviewer hooks would otherwise be duplicated.

## Source projects

- https://github.com/lambdadog/passfail2
- https://github.com/AnKing-VIP/The-KING-of-Button-Add-ons
- Compatibility target: https://github.com/JSchoreels/anki/tree/7259f40e
