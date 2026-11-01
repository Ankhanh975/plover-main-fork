# Plover

Plover brings stenography to everyone. It is a free, open-source desktop
application for writing on your computer with a stenography keyboard, at
speeds of 200 words per minute and beyond.

## Contents

- [About Plover](#about-plover)
- [Installation](#installation)
- [Getting help](#getting-help)
- [Contributing](#contributing)
  - [Donations](#donations)
  - [Ways to contribute](#ways-to-contribute)
- [Development and building](#development-and-building)
- [Changes in this fork](#changes-in-this-fork)

## About Plover

Plover (rhymes with “lover”) is part of the Open Steno Project. The project
aims to make machine shorthand accessible to everyone with free software,
affordable hardware, and learning resources.

Plover has been licensed under GPL-2.0-or-later since version 3.1.0. See
[LICENSE.txt](LICENSE.txt) for the license terms.

## Changes in this fork

This section records the changes from the complete history authored with
`ankhanh1566@gmail.com` (under the names `GoldenApple` and `GoldAppleVn`).
The history contains 84 commits: 38 with changes documented below, 19 merge
commits with no unique direct changes, and 46 commits that only changed
user-specific dictionary data.

### Functional and UI changes

- Added modal dictionary state management through `ModalDictionaryTrayIcon`,
  including active/inactive tray icons, resource registration, main-window
  integration, and tray-icon tests.
- Added the custom `-N` and `-X` keys to the English steno system. The Plover
  HID layout now exposes `X1` through `X26`, while `-N` and `-X` remain
  unbound by default and configurable through **Configure**.
- Added early chord/stroke sending for Plover HID and computer-keyboard
  machines, including configuration controls, timing behavior, correction of
  growing chords, undo-stroke protection, and tests.
- Added `retro_case` capitalization behavior, translator-state reset handling,
  resume-state preservation, external-key handling, and related engine,
  translation, formatting, and black-box tests.
- Improved keyboard event handling, logging, key-down timing, modifier
  behavior, and Windows keyboard emulation. Added passthrough scan codes for
  number and punctuation keys and corresponding tests.
- Added Caps Lock handling as an output toggle: pressing Caps Lock emits a
  toggle command instead of becoming a steno stroke, and Caps Lock is kept
  suppressed from normal keyboard input.
- Added automatic output suspension and restoration for modifier keystrokes.
  Holding Ctrl, Alt, Shift, or Windows temporarily disables steno output so
  those shortcuts can be used normally; releasing the modifiers automatically
  restores output when it was enabled before.
- Optimized output key sending on Windows by batching keyboard and Unicode
  press/release events into a single `SendInput` call when no output delay is
  configured. Backspace output uses the same batching path, while configured
  delays continue to be preserved.
- Added and refined Lapwing movement modal mappings, including caret notation,
  undo behavior, H-related mappings, and supporting distribution metadata.
- Removed the duplicate `Ctrl+N` shortcut from the Dictionaries toolbar and
  scoped the Dictionary Editor shortcut; added a bug-fix note.
- Updated main-window minimize behavior and added feature/bug-fix release notes.

### Commit-by-commit record

The following is the complete non-`user.json` commit record:

- `34629286` — Add modal state icons and update tray icon functionality.
- `195aa028` — Add custom `-N` and `-X` keys to English steno system with
  initial unbinding in Plover HID keymap.
- `b01acc36` — Add `ModalDictionaryTrayIcon` for managing modal dictionary
  state in the system tray.
- `ef30bfff` — Add exit configuration and update modal functionality.
- `3559d6a8` — Implement early chord send for Plover HID with UI adjustments
  and tests.
- `dd7720f3` — Add the `retro_case` operator and capitalization tests.
- `d4246bab` — Fix resume command behavior in `StenoEngine`.
- `844fd2d3` — Add engine behavior and related tests alongside dictionary
  updates.
- `cdb50d05` — Remove the duplicate `Ctrl+N` shortcut and scope the editor
  shortcut.
- `f7e7c339` — Add early stroke sending for the keyboard machine with a UI
  option and tests.
- `e9893970` — Enhance resume command handling and capitalization tests.
- `d1226442` — Prevent early sending of undo strokes and test chord growth.
- `7647635d` — Adjust keyboard key-down timing and its test.
- `84e0584d` — Enhance logging and keyboard handling.
- `83e4663e` — Preserve translator state during resume and add tests.
- `ab419eaa` — Update resume engine behavior and tests.
- `68f7e53f` — Implement resume behavior and output-state tests.
- `5d4af8c3` — Add passthrough scan codes for number and punctuation keys.
- `2cfb4627` — Optimize Windows output-key sending by batching keyboard,
  Unicode, and backspace events when no delay is configured; preserve delayed
  sending and add emulation tests.
- `289e1903` — Reverse selected engine changes and update tests.
- `9a9111b3` — Update Lapwing movement modal mappings.
- `fc78e403` — Implement resume behavior and update modal/test coverage.
- `7ff7222b` — Refactor Lapwing movement mappings and add H-related mappings.
- `15973354` — Update Lapwing movement modal mappings.
- `87fe10f3` — Refactor Lapwing movement modal mappings.
- `cce3cc31` — Add caret notation and undo behavior to modal entries.
- `a3874a11` — Add caret notation to modal entries and dictionary values.
- `a1ba8904` — Update modal mappings and distribution dependencies.
- `9ecc153d` — Update minimize behavior and modal definitions.
- `f47dbe05` — Add a temporary dictionary data file used by the changes.
- `30f37cb1` — Refine punctuation meta handling and tests.
- `5f6cf81b` — Improve capitalization and punctuation meta handling.
- `a259f300` — Implement external key handling and translator-state management.
- `f23d39a4` — Reset translator state on the next stroke.
- `4c416e6e` — Reset translator state in `StenoEngine`.
- `7ad5fecc` — Update keyboard behavior and tests.
- `654ff6ad` — Add machine command callbacks and Caps Lock output toggling;
  improve keyboard, engine, registry, and platform input handling.
- `68291439` — Add modifier-aware output suspension and automatic restoration
  after Ctrl, Alt, Shift, or Windows keys are released.

All changes to `plover/user.json` and `plover/assets/user.json`, including
commits whose only purpose was adding or correcting dictionary entries, are
intentionally excluded.

## Installation

Plover is available for Windows, Linux, and macOS. Follow the [installation
guide](https://plover.wiki/index.php/Installation_Guide) to download and
install Plover, then complete the initial configuration.

## Getting help

For help getting started, setup instructions, and supported hardware, visit
the [Plover Wiki](https://plover.wiki). If you run into a problem or have an
idea for an improvement, [search existing issues or open a new one](https://github.com/opensteno/plover/issues).

For general questions and community discussion, join the Plover community on
[Discord](https://discord.com/invite/H5HnRE6) or the
[Google Group](https://groups.google.com/forum/#!forum/ploversteno).

## Contributing

Plover is developed by volunteers, and contributions of all kinds help the
Open Steno Project grow.

### Donations

Donations help fund new projects and cover the costs of maintaining and
publishing Plover. Contributions of any size are welcome through the
[Open Steno donation page](http://www.opensteno.org/donate).

### Ways to contribute

- **Code:** Plover is a cross-platform desktop application written in Python.
  Read the [contribution guide](CONTRIBUTING.md) to get started. Other
  stenography projects, including [StenoJig](https://github.com/JoshuaGrams/steno-jig)
  and [StenoTray](https://github.com/SmackleFunky/StenoTray), also welcome
  contributors.
- **Documentation and design:** Improve the [Plover Wiki](https://plover.wiki),
  suggest usability improvements, or contribute artwork and icons.
- **Community and web:** Help with community resources and websites maintained
  by the Open Steno Project.

## Development and building

Plover is a cross-platform Python application. Platform-specific setup and
build instructions are available in the repository:

- [Windows](windows/README.md)
- [Linux](linux/README.md)
- [macOS](osx/README.md)
