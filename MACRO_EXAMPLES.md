# Push Notification – Macro Examples

Once the workbench is installed you can import the public API from any FreeCAD
macro:

```python
from push_notification import notify, notify_success, notify_error, notify_render_done

# ── Basic notification ──────────────────────────────────────
notify("Part export started…", title="FreeCAD Job", priority=3)

# ── After a long render ────────────────────────────────────
notify_render_done("/path/to/output.png")

# ── After a FEM simulation ─────────────────────────────────
from push_notification import notify_fem_done
notify_fem_done("Beam stress analysis")

# ── Custom priority + tags ─────────────────────────────────
from push_notification.core import send, Notification
send(Notification(
    message="Batch export of 24 parts finished.",
    title="✅ Batch Done",
    priority=4,                          # High
    tags=["outbox_tray", "white_check_mark"],
))
```

## Wrapping a long operation

```python
import FreeCAD
from push_notification import notify_success, notify_error

try:
    # … your heavy operation here …
    doc = FreeCAD.ActiveDocument
    doc.recompute()
    notify_success(f"Recompute of '{doc.Name}' finished.")
except Exception as e:
    notify_error(str(e))
    raise
```

## Hooking into FreeCAD's document signals (put in user macro)

```python
import FreeCAD
from push_notification import notify

def _on_save(doc):
    notify(f"'{doc.Name}' saved.", title="💾 Saved", priority=2)

FreeCAD.connect("saveDocument", _on_save)
```
