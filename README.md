<p align="center">
    <img width="300" alt="Plover logo" src="https://raw.githubusercontent.com/opensteno/plover/main/doc/_static/dolores.svg" />
</p>

<h1 align="center">Plover</h1>

<p align="center"><i>Bringing stenography to everyone.</i></p>

<p align="center">
    <a href="https://github.com/opensteno/plover/releases">
        <img alt="Latest release" src="https://img.shields.io/github/v/release/opensteno/plover?filter=v*" />
    </a>
    <img alt="License" src="https://img.shields.io/github/license/opensteno/plover" />
    <a href="https://github.com/opensteno/plover/actions/workflows/ci.yml?query=branch%3Amain">
        <img alt="CI status" src="https://github.com/opensteno/plover/actions/workflows/ci.yml/badge.svg?branch=main" />
    </a>
    <a href="https://plover.readthedocs.io/">
        <img alt="ReadTheDocs" src="https://img.shields.io/readthedocs/plover?logo=readthedocs&logoColor=white" />
    </a>
    <a href="https://discord.gg/0lQde43a6dGmAMp2">
        <img alt="Plover Discord" src="https://img.shields.io/discord/136953735426473984?logo=discord&logoColor=white" />
    </a>
</p>

| [Homepage][] | [Wiki][] | [Blog][] | [Google Group][] | [Discord](https://discord.com/invite/H5HnRE6) |
| ------------ | -------- | -------- | ---------------- | --------------------------------------------- |

-   [About](#about)
-   [Installation](#installation)
-   [Getting help](#getting-help)
-   [Contributing](#contributing)
-   [Donations](#donations)
-   [Programming](#programming)
-   [Writing, Art, UX, and Web Design](#writing-art-ux-and-web-design)
-   [Development Environment and Building](#development-environment-and-building)

## About

Plover (rhymes with "lover") is a desktop application that allows anyone
to use stenography to write on their computer, up to speeds of 200WPM
and beyond.

Plover is part of the [Open Steno Project][]. The Open Steno Project's
goal is to provide everything you need to learn machine shorthand on
your own, from free software, to cheap hardware, to learning resources.

Plover is GPLv2+ as of version 3.1.0. See the [license][] for details.

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

Plover runs on Windows, Linux, and Mac.

View the [installation guide][] which covers downloading, installation,
and initial configuration.

## Getting help

Having trouble with Plover?

The Wiki has several pages to help you:

-   [Installation Guide][]
-   [Beginner's Guide][]
-   [Supported Hardware][]
-   [Troubleshooting Common Issues][]

If you are still having trouble, have found a bug, or would like to
request a new feature, please [search for or create an issue][issues].
When making a new issue, fill out the form as best you can so that we
can help you quickly.

If you are looking for more general support (i.e. you don't have a
specific issue), consider joining the community. We are active on
[Discord](https://discord.gg/0lQde43a6dGmAMp2), a live chatroom service; and on the [Google Group][],
a more traditional mailing list.

## Contributing

The Open Steno Project is always growing, and could use your help!

### Donations

Plover is developed by volunteers. Donations to Open Steno help fund new
projects as well as any maintenance costs with publishing Plover.

[Donate here][Donate], donations of any size are very appreciated!

### Programming

Plover is a cross-platform desktop application written in Python. To
contribute to Plover, see [contributing][].

If Python isn't your thing, there are other steno-related projects,
including [StenoJig][] (JavaScript) and [StenoTray][] (Java).

### Writing, Art, UX, and Web Design

-   The [Plover Wiki][Wiki] discusses Plover and Open Steno in
    general. Edits to the Wiki and new page ideas are welcome.
-   Graphic art for Plover and stenography in general is always
    appreciated. The app's icons are worked on at [panathea/plover\_icons][].
    You may consider reimagining or reposing [Plover's mascot, Dolores][Mascot].
-   UX improvement suggestions are welcome. Plover runs on Windows, Mac,
    and Linux, and should be powerful but out of the way, which poses
    some interesting challenges. Please drop in to the Discord server to
    brainstorm with users and the developers.
-   Open Steno has websites that accept contributions, including the
    [Open Steno Project Homepage][Open Steno Project] ([source][Open Steno Project Homepage Source]) and [Plover's Homepage][Homepage]
    ([source][Homepage Source]).

## Development Environment and Building

Plover is cross-platform and has separate build instructions for each
platform.

Please follow through for your system:

-   [Windows][Windows README]
-   [Linux][Linux README]
-   [Mac][macOS README]

[Beginner's Guide]: https://plover.wiki/index.php/Beginner%27s_Guide
[Blog]: http://plover.stenoknight.com
[Contributing]: https://github.com/opensteno/plover/blob/main/CONTRIBUTING.md
[Donate]: http://www.opensteno.org/donate
[Google Group]: https://groups.google.com/forum/#!forum/ploversteno
[Homepage Source]: https://github.com/opensteno/plover/tree/gh-pages
[Homepage]: http://opensteno.org/plover
[Issues]: https://github.com/opensteno/plover/issues?q=is:issue
[License]: https://github.com/opensteno/plover/blob/main/LICENSE.txt
[Open Steno Project Homepage Source]: https://github.com/opensteno/opensteno.github.io
[Open Steno Project]: http://opensteno.org
[Mascot]: http://plover.stenoknight.com/2010/10/new-logo.html
[StenoJig]: https://github.com/JoshuaGrams/steno-jig
[StenoTray]: https://github.com/SmackleFunky/StenoTray
[Supported Hardware]: https://plover.wiki/index.php/Supported_hardware
[Troubleshooting Common Issues]: https://plover.wiki/index.php/Troubleshooting_issues
[Wiki]: https://plover.wiki
[installation guide]: https://plover.wiki/index.php/Installation_Guide
[panathea/plover\_icons]: https://github.com/panathea/plover_icons
[Windows README]: https://github.com/opensteno/plover/blob/main/windows/README.md
[Linux README]: https://github.com/opensteno/plover/blob/main/linux/README.md
[macOS README]: https://github.com/opensteno/plover/blob/main/osx/README.md
