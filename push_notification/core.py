# ********************************************************************************
# *                                                                              *
# *   This program is free software; you can redistribute it and/or modify       *
# *   it under the terms of the GNU General Public License (GPL)                 *
# *   as published by the Free Software Foundation; version 3 of the License.    *
# *   for detail see the LICENSE text file.                                      *
# *                                                                              *
# *   This program is distributed in the hope that it will be useful,            *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of             *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                       *
# *   See the GNU General Public License for more details.                       *
# *                                                                              *
# *   You should have received a copy of the GNU General Public License          *
# *   License along with this program; if not, write to the Free Software        *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston,                      *
# *   MA 02111-1307, USA                                                         *
# *_____________________________________________________________________________ *
# *                                                                              *
# *     ##########################################################               *
# * ## Push Notification FreeCAD WorkBench 2026.04.07-V01 ##                     *
# *     ##########################################################               *
# *                                                                              *
# *                   Authors of this workbench:                                 *
# *           Marco Laffranchi <Laffranchi.Marco@gmail.com>                      *
# *                                                                              *
# *          Please refer to the Documentation and README for                    *
# *      more information regarding this WorkBench and its usage                 *
# *                                                                              *
# ********************************************************************************
"""
push_notification/core.py
Core notification engine — sends HTTP POST to ntfy endpoint.
"""

from __future__ import annotations
import json
import threading
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from typing import List, Optional

import FreeCAD


# ──────────────────────────────────────────────────
# Preferences helpers
# ──────────────────────────────────────────────────
PREF_GROUP = "User parameter:BaseApp/Preferences/FreeCADPNS"


def _prefs():
    return FreeCAD.ParamGet(PREF_GROUP)


def get_server_url() -> str:
    return _prefs().GetString("ServerURL", "https://ntfy.sh")


def set_server_url(url: str):
    _prefs().SetString("ServerURL", url.rstrip("/"))


def get_topic() -> str:
    return _prefs().GetString("Topic", "push-notification")


def set_topic(topic: str):
    _prefs().SetString("Topic", topic.strip())


def get_token() -> str:
    """Optional Bearer token for private ntfy topics."""
    return _prefs().GetString("Token", "")


def set_token(token: str):
    _prefs().SetString("Token", token.strip())


def get_default_priority() -> int:
    return _prefs().GetInt("DefaultPriority", 3)


def set_default_priority(p: int):
    _prefs().SetInt("DefaultPriority", p)


def get_notify_on_error() -> bool:
    return _prefs().GetBool("NotifyOnError", True)


def set_notify_on_error(v: bool):
    _prefs().SetBool("NotifyOnError", v)


def get_notify_on_save() -> bool:
    return _prefs().GetBool("NotifyOnSave", False)


def set_notify_on_save(v: bool):
    _prefs().SetBool("NotifyOnSave", v)


# ──────────────────────────────────────────────────
# Notification payload
# ──────────────────────────────────────────────────
@dataclass
class Notification:
    message: str
    title: str = "FreeCAD"
    priority: int = 3           # 1=min … 5=max
    tags: List[str] = field(default_factory=list)
    click_url: Optional[str] = None

    PRIORITY_LABELS = {1: "min", 2: "low", 3: "default", 4: "high", 5: "max"}

    def to_json_payload(self, topic: str, token: str = "") -> tuple:
        """Return (body_bytes, headers) using ntfy's JSON API (supports Unicode)."""
        payload = {
            "topic":    topic,
            "message":  self.message,
            "title":    self.title,
            "priority": self.priority,
        }
        if self.tags:
            payload["tags"] = self.tags
        if self.click_url:
            payload["click"] = self.click_url
        body = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return body, headers


# ──────────────────────────────────────────────────
# Send function (non-blocking)
# ──────────────────────────────────────────────────
def send(notification: Notification,
         server: Optional[str] = None,
         topic: Optional[str] = None,
         token: Optional[str] = None,
         blocking: bool = False) -> None:
    """
    Send *notification* to the ntfy endpoint.

    Runs in a background thread by default so FreeCAD UI never blocks.
    Set *blocking=True* only for tests.
    """
    server = (server or get_server_url()).rstrip("/")
    topic  = topic  or get_topic()
    token  = token  or get_token()

    url = server

    def _send():
        try:
            body, headers = notification.to_json_payload(topic, token)
            req = urllib.request.Request(url, data=body, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    FreeCAD.Console.PrintMessage(
                        f"[Push Notification] Notification sent: {notification.title}\n"
                    )
                else:
                    FreeCAD.Console.PrintWarning(
                        f"[Push Notification] Server returned HTTP {resp.status}\n"
                    )
        except urllib.error.URLError as e:
            FreeCAD.Console.PrintError(
                f"[Push Notification] Failed to send notification: {e}\n"
            )
        except Exception as e:
            FreeCAD.Console.PrintError(f"[Push Notification] Unexpected error: {e}\n")

    if blocking:
        _send()
    else:
        t = threading.Thread(target=_send, daemon=True)
        t.start()


# ──────────────────────────────────────────────────
# Convenience helpers
# ──────────────────────────────────────────────────
def notify(message: str,
           title: str = "FreeCAD",
           priority: int = 3,
           tags: Optional[List[str]] = None) -> None:
    """Quick send — callable from macros."""
    n = Notification(
        message=message,
        title=title,
        priority=priority,
        tags=tags or [],
    )
    send(n)


def notify_success(message: str, title: str = "✅ FreeCAD") -> None:
    send(Notification(message=message, title=title, priority=3,
                      tags=["white_check_mark"]))


def notify_error(message: str, title: str = "❌ FreeCAD Error") -> None:
    send(Notification(message=message, title=title, priority=5,
                      tags=["rotating_light", "error"]))


def notify_warning(message: str, title: str = "⚠️ FreeCAD Warning") -> None:
    send(Notification(message=message, title=title, priority=4,
                      tags=["warning"]))


def notify_render_done(filename: str = "") -> None:
    msg = f"Render finished: {filename}" if filename else "Render finished."
    send(Notification(message=msg, title="🖼️ Render Done", priority=3,
                      tags=["photo", "white_check_mark"]))


def notify_export_done(filename: str = "") -> None:
    msg = f"Export complete: {filename}" if filename else "Export complete."
    send(Notification(message=msg, title="📤 Export Done", priority=3,
                      tags=["outbox_tray"]))


def notify_fem_done(analysis: str = "") -> None:
    msg = f"FEM analysis finished: {analysis}" if analysis else "FEM analysis finished."
    send(Notification(message=msg, title="🔬 FEM Complete", priority=3,
                      tags=["microscope", "white_check_mark"]))
