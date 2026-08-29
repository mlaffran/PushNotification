# PushNotification

A FreeCAD workbench that sends push notifications — to your phone or desktop —
when something happens in FreeCAD: a document is saved, an error occurs, a
render or export finishes, or a FEM/simulation solve completes.

Notifications are delivered via [ntfy](https://ntfy.sh), a free, open-source
pub/sub notification service. Install the ntfy app on your phone, subscribe to
a topic, and FreeCAD will push messages to it. Look for the app with a teal
speech-bubble icon containing a terminal prompt (`>_`), subtitled
"Push notifications via REST" in the app store.

## Features

- **Toolbar/menu commands** to send a custom notification, or a quick
  success/error/render-done notification, and to test your connection.
- **Automatic notifications** on document save and on FreeCAD errors
  (opt-in, configured in Settings).
- **Notification Definitions** — document objects you can create per-file to
  declare "when X happens in this document, send this message," with
  `{doc}`, `{document}`, `{filename}`, and `{error}` placeholders in the
  message/title.
- **Macro API** — call `notify()`, `notify_success()`, `notify_error()`, etc.
  directly from your own macros. See [MACRO_EXAMPLES.md](MACRO_EXAMPLES.md).

## Installation

### Via the Addon Manager (recommended)

Once listed in the FreeCAD Addon catalog: `Tools → Addon Manager`, search for
"PushNotification", install, then restart FreeCAD.

### Manual installation

Clone this repository into your FreeCAD `Mod` directory:

```bash
git clone https://github.com/mlaffran/PushNotification.git \
  "$(python3 -c 'import FreeCAD; print(FreeCAD.getUserAppDataDir())')Mod/PushNotification"
```

Or on macOS, directly:

```bash
git clone https://github.com/mlaffran/PushNotification.git \
  "$HOME/Library/Application Support/FreeCAD/v1-1/Mod/PushNotification"
```

Restart FreeCAD; the **PushNotification** workbench will appear in the
workbench selector.

## Setup

1. Install the [ntfy app](https://ntfy.sh/#subscribe) on your phone (or any
   ntfy-compatible client).
2. In the app, subscribe to a topic name of your choosing (topic names act as
   the "address" notifications are sent to).
3. In FreeCAD, open the **PushNotification** workbench and go to
   **PNS Settings…**. Enter the same topic name (and server URL, if you're
   self-hosting ntfy instead of using the public `ntfy.sh`).
4. Click **Test Connection** to confirm you receive a test push.

### ⚠️ Security note

By default this workbench uses the public `ntfy.sh` server. Topics on
`ntfy.sh` are **not private** — anyone who knows or guesses your topic name
can subscribe and read your notifications (which may include document names
and error text). For anything sensitive:

- Choose a long, hard-to-guess topic name, and/or
- Set an auth token in **PNS Settings…** for a
  [protected topic](https://docs.ntfy.sh/publish/#authentication), or
- Point **Server URL** at a self-hosted ntfy instance.

By default the auth token is stored in FreeCAD's own preferences
(`user.cfg`) as **plain text**. If the optional
[`keyring`](https://pypi.org/project/keyring/) Python package is installed
in FreeCAD's Python environment, the workbench will store and retrieve the
token through your OS credential store instead — macOS Keychain, Windows
Credential Locker, or the Linux Secret Service (GNOME Keyring/KWallet) —
and automatically fall back to plaintext storage (with a console warning)
if `keyring` is missing or its backend is unavailable. To enable it, install
`keyring` into FreeCAD's Python (e.g. via the Addon Manager's dependency
prompt, or `pip install keyring` targeting FreeCAD's interpreter).

## Usage

| Command | What it does |
|---|---|
| Send Notification | Opens a dialog to send a custom message, title, priority, and tags. |
| Notify: Success | Sends a quick success notification for the active document. |
| Notify: Error | Prompts for a message and sends it as an error/alert notification. |
| Notify: Render Done | Prompts for an (optional) rendered file and sends a "render finished" notification. |
| Test Connection | Sends a test notification and shows your configured topic URL. |
| Create Notification Definition | Adds a `NotificationDefinition` object to the document's Notifications folder. |
| Create Simulation Notification | Adds a `NotificationDefinition` pre-configured for the "simulation finished" trigger. |
| PNS Settings… | Configure server URL, topic, auth token, default click URL, and automatic notifications. |

### Notification Definitions

A `NotificationDefinition` is a document object with editable properties:

- **Trigger** — `when document is saved`, `when FreeCAD error occurs`, or
  `when simulation finishes`.
- **Message** / **Title** — support `{doc}`, `{document}`, `{filename}`,
  `{error}` placeholders.
- **Priority** (1–5), **Tags** (ntfy emoji tags), **ClickURL**.

Any number of definitions can live in a document; all matching ones fire when
their trigger condition occurs.

## Macro API

```python
from push_notification import notify, notify_success, notify_error, notify_render_done

notify("Part export started…", title="FreeCAD Job", priority=3)
notify_render_done("/path/to/output.png")
```

See [MACRO_EXAMPLES.md](MACRO_EXAMPLES.md) for more.

## License

GPL-3.0-or-later. See [LICENSE](LICENSE).

## Author

Marco Laffranchi

## Contributing

Issues and pull requests welcome at
[github.com/mlaffran/PushNotification](https://github.com/mlaffran/PushNotification).
