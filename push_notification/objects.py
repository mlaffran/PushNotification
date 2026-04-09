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
# * ## Push Notification FreeCAD WorkBench 2026.04.09-V01 ##                    *
# *     ##########################################################               *
# *                                                                              *
# *                   Authors of this workbench:                                 *
# *           Marco Laffranchi <Laffranchi.Marco@gmail.com>                      *
# *                                                                              *
# *          Please refer to the Documentation and README for                    *
# *      more information regarding this WorkBench and its usage                 *
# *                                                                              *
# ********************************************************************************
"""FreeCAD document objects for the Push Notification workbench."""

from typing import Optional

import FreeCAD as App
import FreeCADGui as Gui

from push_notification import core


def _ensure_property(obj, prop_name: str, prop_type: str, group: str, doc: str):
    if prop_name in obj.PropertiesList:
        return False
    obj.addProperty(prop_type, prop_name, group, doc)
    return True


def _ensure_trigger_property(obj):
    current_value = core.TRIGGER_DOCUMENT_SAVED
    if "Trigger" in obj.PropertiesList:
        try:
            current_value = str(getattr(obj, "Trigger", core.TRIGGER_DOCUMENT_SAVED) or core.TRIGGER_DOCUMENT_SAVED)
        except Exception:
            current_value = core.TRIGGER_DOCUMENT_SAVED
        try:
            if obj.getTypeIdOfProperty("Trigger") != "App::PropertyEnumeration":
                obj.removeProperty("Trigger")
        except Exception:
            pass
    if "Trigger" not in obj.PropertiesList:
        obj.addProperty(
            "App::PropertyEnumeration",
            "Trigger",
            "Notification",
            "When to send the notification",
        )
    try:
        obj.Trigger = list(core.SUPPORTED_TRIGGERS)
    except Exception:
        pass
    try:
        obj.Trigger = current_value if current_value in core.SUPPORTED_TRIGGERS else core.TRIGGER_DOCUMENT_SAVED
    except Exception:
        obj.Trigger = core.TRIGGER_DOCUMENT_SAVED


class NotificationDefinition:
    """FeaturePython object representing a notification definition."""

    def __init__(self, obj):
        self.Type = "NotificationDefinition"
        self.Object = obj
        self.initProperties(obj)
        obj.Proxy = self

    def initProperties(self, obj):
        added_name = _ensure_property(obj, "Name", "App::PropertyString", "Notification", "Name of this notification definition")
        _ensure_trigger_property(obj)
        added_message = _ensure_property(obj, "Message", "App::PropertyString", "Notification", "Message to send")
        added_title = _ensure_property(obj, "Title", "App::PropertyString", "Notification", "Notification title")
        added_priority = _ensure_property(obj, "Priority", "App::PropertyInteger", "Notification", "Priority (1-5)")
        added_tags = _ensure_property(obj, "Tags", "App::PropertyStringList", "Notification", "Tags for the notification")

        if added_name or not str(getattr(obj, "Name", "") or "").strip():
            obj.Name = "New Notification"
        if added_message or not str(getattr(obj, "Message", "") or "").strip():
            obj.Message = "Document event completed for {doc}"
        if added_title or not str(getattr(obj, "Title", "") or "").strip():
            obj.Title = "FreeCAD Notification"
        if added_priority:
            obj.Priority = 3
        if added_tags or not list(getattr(obj, "Tags", []) or []):
            obj.Tags = ["white_check_mark"]

    def execute(self, obj):
        return

    def onChanged(self, obj, prop):
        if prop == "Priority":
            try:
                obj.Priority = max(1, min(5, int(getattr(obj, "Priority", 3) or 3)))
            except Exception:
                obj.Priority = 3

    def onDocumentRestored(self, obj):
        self.Object = obj
        self.initProperties(obj)
        obj.Proxy = self


class ViewProviderNotificationDefinition:
    """View provider for NotificationDefinition objects."""

    def __init__(self, vobj):
        vobj.Proxy = self

    def getIcon(self):
        return ":/icons/push_notification_icon.svg"

    def attach(self, vobj):
        self.Object = vobj.Object

    def claimChildren(self):
        return []

    def setEdit(self, vobj, mode):
        return False

    def unsetEdit(self, vobj, mode):
        return

    def doubleClicked(self, vobj):
        return False

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


def create_notification_definition(name: str = "Notification") -> Optional[App.DocumentObject]:
    if not App.ActiveDocument:
        App.Console.PrintError("No active document to create notification in\n")
        return None

    try:
        obj = App.ActiveDocument.addObject("App::FeaturePython", name)
        NotificationDefinition(obj)
        if Gui.ActiveDocument:
            ViewProviderNotificationDefinition(obj.ViewObject)
        obj.Label = name
        App.Console.PrintMessage(f"Created notification definition '{name}'\n")
        return obj
    except Exception as e:
        App.Console.PrintError(f"Failed to create notification definition: {e}\n")
        return None


def ensure_notification_folder() -> Optional[App.DocumentObject]:
    if not App.ActiveDocument:
        return None

    doc = App.ActiveDocument
    for obj in doc.Objects:
        if getattr(obj, "TypeId", "") == "App::DocumentObjectGroup" and getattr(obj, "Label", "") == "Notifications":
            return obj

    try:
        folder = doc.addObject("App::DocumentObjectGroup", "Notifications")
        folder.Label = "Notifications"
        App.Console.PrintMessage("Created Notifications folder\n")
        return folder
    except Exception as e:
        App.Console.PrintError(f"Failed to create Notifications folder: {e}\n")
        return None


def create_notification_in_folder(name: str = "Notification") -> Optional[App.DocumentObject]:
    folder = ensure_notification_folder()
    if not folder:
        return None

    notification = create_notification_definition(name)
    if not notification:
        return None

    try:
        folder.addObject(notification)
        return notification
    except Exception as e:
        App.Console.PrintError(f"Failed to add notification to folder: {e}\n")
        return notification
