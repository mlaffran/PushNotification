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
push_notification/objects.py
FreeCAD document objects for Push Notification workbench.
"""

import FreeCAD as App
import FreeCADGui as Gui
from typing import Optional, List


class NotificationDefinition:
    """FeaturePython object representing a notification definition."""
    
    def __init__(self, obj):
        """Initialize the object with default properties."""
        self.Type = "NotificationDefinition"
        self.Object = obj
        
        # Add properties
        obj.addProperty("App::PropertyString", "Name", "Notification", "Name of this notification definition")
        obj.addProperty("App::PropertyString", "Trigger", "Notification", "When to send the notification")
        obj.addProperty("App::PropertyString", "Message", "Notification", "Message to send")
        obj.addProperty("App::PropertyString", "Title", "Notification", "Notification title")
        obj.addProperty("App::PropertyInteger", "Priority", "Notification", "Priority (1-5)")
        obj.addProperty("App::PropertyStringList", "Tags", "Notification", "Tags for the notification")
        
        # Set default values
        obj.Name = "New Notification"
        obj.Trigger = "when Solve is complete"  # Currently only option
        obj.Message = "Task completed successfully"
        obj.Title = "FreeCAD Notification"
        obj.Priority = 3
        obj.Tags = ["white_check_mark"]
        
        obj.Proxy = self
    
    def execute(self, obj):
        """Called on document recompute (not used for notifications)."""
        pass
    
    def onChanged(self, obj, prop):
        """Called when a property changes."""
        pass
    
    def onDocumentRestored(self, obj):
        """Called when document is restored."""
        self.Object = obj
        obj.Proxy = self


class ViewProviderNotificationDefinition:
    """View provider for NotificationDefinition objects."""
    
    def __init__(self, vobj):
        vobj.Proxy = self
    
    def getIcon(self):
        """Return the icon for this object."""
        return ":/icons/push_notification_icon.svg"
    
    def attach(self, vobj):
        """Attach the view provider to the object."""
        self.Object = vobj.Object
    
    def claimChildren(self):
        """Return children (none)."""
        return []
    
    def setEdit(self, vobj, mode):
        """Start editing the object."""
        return False
    
    def unsetEdit(self, vobj, mode):
        """Stop editing the object."""
        pass
    
    def doubleClicked(self, vobj):
        """Handle double-click."""
        return False
    
    def __getstate__(self):
        """Return state for serialization."""
        return None
    
    def __setstate__(self, state):
        """Restore state from serialization."""
        pass


def create_notification_definition(name: str = "Notification") -> Optional[App.DocumentObject]:
    """Create a new NotificationDefinition object in the active document."""
    if not App.ActiveDocument:
        App.Console.PrintError("No active document to create notification in\n")
        return None
    
    try:
        # Create the FeaturePython object
        obj = App.ActiveDocument.addObject("App::FeaturePython", name)
        NotificationDefinition(obj)
        
        if Gui.ActiveDocument:
            ViewProviderNotificationDefinition(obj.ViewObject)
        
        # Set label (user-visible name)
        obj.Label = name
        
        App.Console.PrintMessage(f"Created notification definition '{name}'\n")
        return obj
    
    except Exception as e:
        App.Console.PrintError(f"Failed to create notification definition: {e}\n")
        return None


def ensure_notification_folder() -> Optional[App.DocumentObject]:
    """Ensure the document has a 'Notifications' folder/group.
    Returns the folder object or None if no active document."""
    if not App.ActiveDocument:
        return None
    
    doc = App.ActiveDocument
    
    # Look for existing "Notifications" group
    for obj in doc.Objects:
        if hasattr(obj, 'TypeId') and obj.TypeId == "App::DocumentObjectGroup":
            if obj.Label == "Notifications":
                return obj
    
    # Create new group
    try:
        folder = doc.addObject("App::DocumentObjectGroup", "Notifications")
        folder.Label = "Notifications"
        App.Console.PrintMessage("Created Notifications folder\n")
        return folder
    except Exception as e:
        App.Console.PrintError(f"Failed to create Notifications folder: {e}\n")
        return None


def create_notification_in_folder(name: str = "Notification") -> Optional[App.DocumentObject]:
    """Create a notification definition and add it to the Notifications folder."""
    # Ensure folder exists
    folder = ensure_notification_folder()
    if not folder:
        return None
    
    # Create notification definition
    notification = create_notification_definition(name)
    if not notification:
        return None
    
    # Add to folder
    try:
        folder.addObject(notification)
        return notification
    except Exception as e:
        App.Console.PrintError(f"Failed to add notification to folder: {e}\n")
        return notification  # Return notification even if folder addition fails