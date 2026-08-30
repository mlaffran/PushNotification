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
# * ## PushNotification FreeCAD WorkBench 2026.04.09-V01 ##                    *
# *     ##########################################################               *
# *                                                                              *
# *                   Authors of this workbench:                                 *
# *           Marco Laffranchi <Laffranchi.Marco@gmail.com>                      *
# *                                                                              *
# *          Please refer to the Documentation and README for                    *
# *      more information regarding this WorkBench and its usage                 *
# *                                                                              *
# ********************************************************************************
"""Core notification engine plus automatic FreeCAD save/error hooks."""

from __future__ import annotations

import json
import secrets
import threading
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

import FreeCAD

try:
    import keyring
    import keyring.errors
    _KEYRING_IMPORT_ERROR = None
except Exception as _err:  # pragma: no cover - depends on host environment
    keyring = None
    _KEYRING_IMPORT_ERROR = _err

_KEYRING_SERVICE = "FreeCAD-PushNotification"
_KEYRING_USERNAME = "ntfy-token"
_KEYRING_WARNED = False

PREF_GROUP = "User parameter:BaseApp/Preferences/FreeCADPNS"

TRIGGER_DOCUMENT_SAVED = "when document is saved"
TRIGGER_FREECAD_ERROR = "when FreeCAD error occurs"
TRIGGER_SIMULATION_FINISHED = "when simulation finishes"
SUPPORTED_TRIGGERS = (
    TRIGGER_DOCUMENT_SAVED,
    TRIGGER_FREECAD_ERROR,
    TRIGGER_SIMULATION_FINISHED,
)

_HOOKS_INSTALLED = False
_SAVE_OBSERVER = None
_KNOWN_ERROR_OBJECTS: Dict[str, Set[str]] = {}


def _prefs():
    return FreeCAD.ParamGet(PREF_GROUP)


def get_server_url() -> str:
    return _prefs().GetString("ServerURL", "https://ntfy.sh")


def set_server_url(url: str):
    _prefs().SetString("ServerURL", url.rstrip("/"))


def _generate_default_topic() -> str:
    return f"freecad-pns-{secrets.token_hex(6)}"


def get_topic() -> str:
    prefs = _prefs()
    topic = prefs.GetString("Topic", "")
    if not topic:
        # ntfy topics are unauthenticated-by-obscurity: a shared hardcoded
        # default would let anyone subscribe to every install using it.
        # Generate a random one on first use and persist it.
        topic = _generate_default_topic()
        prefs.SetString("Topic", topic)
    return topic


def set_topic(topic: str):
    _prefs().SetString("Topic", topic.strip())


def _warn_keyring_fallback(reason: str):
    global _KEYRING_WARNED
    if _KEYRING_WARNED:
        return
    _KEYRING_WARNED = True
    FreeCAD.Console.PrintWarning(
        f"[PushNotification] Secure token storage unavailable ({reason}); "
        "falling back to plaintext storage in FreeCAD preferences.\n"
    )


def get_token() -> str:
    if keyring is not None:
        try:
            token = keyring.get_password(_KEYRING_SERVICE, _KEYRING_USERNAME)
            if token:
                return token
        except Exception as err:
            _warn_keyring_fallback(str(err))
    # Fall back to (or migrate from) the plaintext preference value.
    return _prefs().GetString("Token", "")


def set_token(token: str):
    token = token.strip()
    if keyring is not None:
        try:
            if token:
                keyring.set_password(_KEYRING_SERVICE, _KEYRING_USERNAME, token)
            else:
                try:
                    keyring.delete_password(_KEYRING_SERVICE, _KEYRING_USERNAME)
                except keyring.errors.PasswordDeleteError:
                    pass
            # Clear any legacy plaintext copy now that keyring holds the token.
            _prefs().SetString("Token", "")
            return
        except Exception as err:
            _warn_keyring_fallback(str(err))
    _prefs().SetString("Token", token)


def get_default_priority() -> int:
    return _prefs().GetInt("DefaultPriority", 3)


def set_default_priority(p: int):
    _prefs().SetInt("DefaultPriority", p)


def get_notify_on_error() -> bool:
    return _prefs().GetBool("NotifyOnError", False)


def set_notify_on_error(v: bool):
    _prefs().SetBool("NotifyOnError", v)


def get_notify_on_save() -> bool:
    return _prefs().GetBool("NotifyOnSave", False)


def set_notify_on_save(v: bool):
    _prefs().SetBool("NotifyOnSave", v)


def get_notification_link() -> str:
    return _prefs().GetString("NotificationLink", "")


def set_notification_link(link: str):
    _prefs().SetString("NotificationLink", link.strip())


@dataclass
class Notification:
    message: str
    title: str = "FreeCAD"
    priority: int = 3
    tags: List[str] = field(default_factory=list)
    click_url: Optional[str] = None

    PRIORITY_LABELS = {1: "min", 2: "low", 3: "default", 4: "high", 5: "max"}

    def to_json_payload(self, topic: str, token: str = "") -> tuple:
        payload = {
            "topic": topic,
            "message": self.message,
            "title": self.title,
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


def send(notification: Notification,
         server: Optional[str] = None,
         topic: Optional[str] = None,
         token: Optional[str] = None,
         blocking: bool = False) -> None:
    server = (server or get_server_url()).rstrip("/")
    topic = topic or get_topic()
    token = token or get_token()
    url = server

    def _send():
        try:
            body, headers = notification.to_json_payload(topic, token)
            req = urllib.request.Request(url, data=body, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    FreeCAD.Console.PrintMessage(
                        f"[PushNotification] Notification sent: {notification.title}\n"
                    )
                else:
                    FreeCAD.Console.PrintWarning(
                        f"[PushNotification] Server returned HTTP {resp.status}\n"
                    )
        except urllib.error.URLError as e:
            FreeCAD.Console.PrintError(
                f"[PushNotification] Failed to send notification: {e}\n"
            )
        except Exception as e:
            FreeCAD.Console.PrintError(f"[PushNotification] Unexpected error: {e}\n")

    if blocking:
        _send()
    else:
        thread = threading.Thread(target=_send, daemon=True)
        thread.start()


def notify(message: str,
           title: str = "FreeCAD",
           priority: int = 3,
           tags: Optional[List[str]] = None) -> None:
    send(Notification(message=message, title=title, priority=priority, tags=tags or []))


def notify_success(message: str, title: str = "✅ FreeCAD") -> None:
    send(Notification(message=message, title=title, priority=3, tags=["white_check_mark"]))


def notify_error(message: str, title: str = "❌ FreeCAD Error") -> None:
    send(Notification(message=message, title=title, priority=5, tags=["rotating_light", "error"]))


def notify_warning(message: str, title: str = "⚠️ FreeCAD Warning") -> None:
    send(Notification(message=message, title=title, priority=4, tags=["warning"]))


def notify_render_done(filename: str = "") -> None:
    msg = f"Render finished: {filename}" if filename else "Render finished."
    send(Notification(message=msg, title="🖼️ Render Done", priority=3, tags=["photo", "white_check_mark"]))


def notify_export_done(filename: str = "") -> None:
    msg = f"Export complete: {filename}" if filename else "Export complete."
    send(Notification(message=msg, title="📤 Export Done", priority=3, tags=["outbox_tray"]))


def notify_fem_done(analysis: str = "") -> None:
    msg = f"FEM analysis finished: {analysis}" if analysis else "FEM analysis finished."
    send(Notification(message=msg, title="🔬 FEM Complete", priority=3, tags=["microscope", "white_check_mark"]))


def _doc_display_name(doc) -> str:
    if doc is None:
        return "Unnamed document"
    file_name = str(getattr(doc, "FileName", "") or "").strip()
    if file_name:
        return file_name
    label = str(getattr(doc, "Label", "") or "").strip()
    if label:
        return label
    name = str(getattr(doc, "Name", "") or "").strip()
    return name or "Unnamed document"


def _iter_documents(doc=None):
    documents = []
    if doc is not None:
        return [doc]
    active_doc = getattr(FreeCAD, "ActiveDocument", None)
    if active_doc is not None:
        documents.append(active_doc)
    try:
        all_docs = FreeCAD.listDocuments()
    except Exception:
        all_docs = {}
    for candidate in getattr(all_docs, "values", lambda: [])():
        if candidate is not None and candidate not in documents:
            documents.append(candidate)
    return documents


def _is_notification_definition(obj) -> bool:
    proxy = getattr(obj, "Proxy", None)
    return getattr(proxy, "Type", "") == "NotificationDefinition"


def iter_notification_definitions(doc=None):
    seen = set()
    for document in _iter_documents(doc):
        for obj in getattr(document, "Objects", []) or []:
            if not _is_notification_definition(obj):
                continue
            key = (str(getattr(document, "Name", "")), str(getattr(obj, "Name", "")))
            if key in seen:
                continue
            seen.add(key)
            yield document, obj


def _format_text(template: str, **context) -> str:
    text = str(template or "")
    if not text:
        return ""
    try:
        return text.format(**context)
    except Exception:
        return text


def _build_notification_from_definition(obj,
                                        doc=None,
                                        default_message: str = "",
                                        default_title: str = "FreeCAD",
                                        default_tags: Optional[List[str]] = None,
                                        error_text: str = "") -> Optional[Notification]:
    doc_name = _doc_display_name(doc)
    context = {
        "doc": doc_name,
        "document": doc_name,
        "error": str(error_text or "").strip(),
        "filename": str(getattr(doc, "FileName", "") or "") if doc is not None else "",
    }
    message = _format_text(getattr(obj, "Message", ""), **context).strip() or str(default_message or "").strip()
    if not message:
        return None
    title = _format_text(getattr(obj, "Title", ""), **context).strip() or str(default_title or "FreeCAD")
    try:
        priority = int(getattr(obj, "Priority", get_default_priority()) or get_default_priority())
    except Exception:
        priority = get_default_priority()
    priority = max(1, min(5, priority))
    tags = list(getattr(obj, "Tags", []) or list(default_tags or []))
    click_url = getattr(obj, "ClickURL", "")
    if click_url:
        click_url = str(click_url).strip()
    if not click_url:
        click_url = None
    return Notification(message=message, title=title, priority=priority, tags=tags, click_url=click_url)


def emit_trigger(trigger: str,
                 doc=None,
                 default_message: str = "",
                 default_title: str = "FreeCAD",
                 default_tags: Optional[List[str]] = None,
                 error_text: str = "") -> int:
    trigger = str(trigger or "").strip()
    sent = 0
    for document, obj in iter_notification_definitions(doc):
        obj_trigger = str(getattr(obj, "Trigger", "") or "").strip()
        if obj_trigger != trigger:
            continue
        notification = _build_notification_from_definition(
            obj,
            doc=document,
            default_message=default_message,
            default_title=default_title,
            default_tags=default_tags,
            error_text=error_text,
        )
        if notification is None:
            continue
        send(notification)
        sent += 1
    return sent


def _dispatch_save_notifications(doc) -> None:
    doc_name = _doc_display_name(doc)
    if get_notify_on_save():
        notify_success(f"Document saved: {doc_name}", title="💾 Document Saved")
    emit_trigger(
        TRIGGER_DOCUMENT_SAVED,
        doc=doc,
        default_message=f"Document saved: {doc_name}",
        default_title="💾 Document Saved",
        default_tags=["floppy_disk", "white_check_mark"],
    )


def _dispatch_error_notifications(doc, obj) -> None:
    doc_name = _doc_display_name(doc)
    obj_label = str(getattr(obj, "Label", "") or getattr(obj, "Name", "") or "Object")
    text = f"{obj_label} failed to recompute in {doc_name}"
    if get_notify_on_error():
        notify_error(text)
    emit_trigger(
        TRIGGER_FREECAD_ERROR,
        doc=doc,
        default_message=text,
        default_title="❌ FreeCAD Error",
        default_tags=["rotating_light", "error"],
        error_text=text,
    )


def _check_document_errors(doc) -> None:
    """Detect objects that just entered an error state after a recompute.

    We watch obj.State rather than hooking FreeCAD.Console.PrintError: the
    console is used for every error in the application (macros, unrelated
    workbenches, etc.), and monkey-patching it caused a runaway loop where a
    failed notification send logged its own error, which triggered another
    notification, which failed and logged again. Recompute state only
    reflects this document's objects and carries no such feedback path.
    """
    doc_name = str(getattr(doc, "Name", "") or "")
    if not doc_name:
        return
    current_errors = set()
    for obj in getattr(doc, "Objects", []) or []:
        if "Invalid" in (getattr(obj, "State", None) or []):
            current_errors.add(str(getattr(obj, "Name", "") or ""))
    previous_errors = _KNOWN_ERROR_OBJECTS.get(doc_name, set())
    for obj_name in current_errors - previous_errors:
        obj = doc.getObject(obj_name)
        if obj is not None:
            _dispatch_error_notifications(doc, obj)
    _KNOWN_ERROR_OBJECTS[doc_name] = current_errors


class _PushNotificationDocumentObserver:
    def slotFinishSaveDocument(self, doc, value=None):
        try:
            _dispatch_save_notifications(doc)
        except Exception as err:
            FreeCAD.Console.PrintWarning(f"[PushNotification] Save hook failed: {err}\n")

    def slotCreatedDocument(self, doc):
        return

    def slotDeletedDocument(self, doc):
        _KNOWN_ERROR_OBJECTS.pop(str(getattr(doc, "Name", "") or ""), None)

    def slotRelabelDocument(self, doc):
        return

    def slotActivateDocument(self, doc):
        return

    def slotUndoDocument(self, doc):
        return

    def slotRedoDocument(self, doc):
        return

    def slotBeforeChangeDocument(self, doc, prop):
        return

    def slotChangedDocument(self, doc, prop):
        return

    def slotBeforeRecomputeDocument(self, doc):
        return

    def slotRecomputedDocument(self, doc):
        try:
            _check_document_errors(doc)
        except Exception as err:
            FreeCAD.Console.PrintWarning(f"[PushNotification] Error-detection hook failed: {err}\n")

    def slotStartSaveDocument(self, doc, value=None):
        return


def install_hooks() -> bool:
    global _HOOKS_INSTALLED, _SAVE_OBSERVER
    if _HOOKS_INSTALLED:
        return True

    installed = True
    try:
        _SAVE_OBSERVER = _PushNotificationDocumentObserver()
        FreeCAD.addDocumentObserver(_SAVE_OBSERVER)
    except Exception as err:
        installed = False
        FreeCAD.Console.PrintWarning(
            f"[PushNotification] Failed to install document observer: {err}\n"
        )

    _HOOKS_INSTALLED = installed
    return installed


def uninstall_hooks() -> bool:
    global _HOOKS_INSTALLED, _SAVE_OBSERVER
    if not _HOOKS_INSTALLED:
        return True

    success = True

    if _SAVE_OBSERVER is not None:
        try:
            FreeCAD.removeDocumentObserver(_SAVE_OBSERVER)
            _SAVE_OBSERVER = None
        except Exception as err:
            FreeCAD.Console.PrintWarning(
                f"[PushNotification] Failed to remove document observer: {err}\n"
            )
            success = False

    _KNOWN_ERROR_OBJECTS.clear()
    _HOOKS_INSTALLED = False
    return success
