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
# * ## PushNotification FreeCAD WorkBench 2026.04.09-V01 ##                     *
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
PushNotification Workbench
Sends push notifications to the iPhone app via ntfy.
"""

import os
import FreeCAD
import FreeCADGui

class PushNotificationWorkbench(FreeCADGui.Workbench):
    """PushNotification Workbench"""

    MenuText = "PushNotification"
    ToolTip  = "Send push notifications via the PushNotification workbench"

    def __init__(self):
        wb_dir = os.path.join(FreeCAD.getUserAppDataDir(), "Mod", "PushNotification")
        self.Icon = os.path.join(wb_dir, "resources", "push_notification_icon.svg")
        FreeCADGui.addIconPath(os.path.join(wb_dir, "resources"))

    def Initialize(self):
        from push_notification import commands

        command_list = [
            "PNS_Notify",
            "PNS_NotifySuccess",
            "PNS_NotifyError",
            "PNS_NotifyRenderDone",
            "PNS_Settings",
            "PNS_TestConnection",
            "PNS_CreateNotificationDefinition",
        ]

        self.appendToolbar("PushNotification", command_list)
        self.appendMenu("&PushNotifications", command_list)

        FreeCAD.Console.PrintMessage("PushNotification Workbench loaded.\n")

    def Activated(self):
        FreeCAD.Console.PrintMessage("PushNotification Workbench activated.\n")

    def Deactivated(self):
        pass

    def GetClassName(self):
        return "Gui::PythonWorkbench"


FreeCADGui.addWorkbench(PushNotificationWorkbench)
