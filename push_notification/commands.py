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
push_notification/commands.py
FreeCAD GUI commands registered in the toolbar / menu.
"""

import FreeCAD
import FreeCADGui
try:
    from PySide6 import QtWidgets, QtCore, QtGui
except ImportError:
    from PySide2 import QtWidgets, QtCore, QtGui

from push_notification import core
from push_notification import objects


# ──────────────────────────────────────────────────────────────
# Helper: resource path for icons
# ──────────────────────────────────────────────────────────────
import os
_RES = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources")

def icon(name):
    return os.path.join(_RES, name)


# ──────────────────────────────────────────────────────────────
# Command: Custom notification dialog
# ──────────────────────────────────────────────────────────────
class PNS_Notify:
    """Send a custom push notification."""

    def GetResources(self):
        return {
            "Pixmap":   icon("notify.svg"),
            "MenuText": "Send Notification",
            "ToolTip":  "Send a custom push notification to Push Notification",
            "Accel":    "Shift+N",
        }

    def IsActive(self):
        return True

    def Activated(self):
        dialog = NotifyDialog(FreeCADGui.getMainWindow())
        dialog.exec()


class NotifyDialog(QtWidgets.QDialog):
    PRIORITY_MAP = {"Min (1)": 1, "Low (2)": 2, "Normal (3)": 3,
                    "High (4)": 4, "Urgent (5)": 5}

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Send Notification – Push Notification")
        self.setMinimumWidth(440)
        self._build_ui()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # Title
        form = QtWidgets.QFormLayout()
        self.title_edit = QtWidgets.QLineEdit("FreeCAD")
        self.title_edit.setPlaceholderText("Notification title")
        form.addRow("Title:", self.title_edit)

        # Message
        self.msg_edit = QtWidgets.QPlainTextEdit()
        self.msg_edit.setPlaceholderText("Enter your notification message…")
        self.msg_edit.setFixedHeight(80)
        form.addRow("Message:", self.msg_edit)

        # Priority
        self.priority_combo = QtWidgets.QComboBox()
        self.priority_combo.addItems(list(self.PRIORITY_MAP.keys()))
        self.priority_combo.setCurrentIndex(2)  # Normal
        form.addRow("Priority:", self.priority_combo)

        # Tags
        self.tags_edit = QtWidgets.QLineEdit()
        self.tags_edit.setPlaceholderText("wrench,white_check_mark  (ntfy emoji tags, comma-separated)")
        form.addRow("Tags:", self.tags_edit)

        layout.addLayout(form)

        # Buttons
        btn_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setText("Send")
        btn_box.accepted.connect(self._send)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def _send(self):
        message = self.msg_edit.toPlainText().strip()
        if not message:
            QtWidgets.QMessageBox.warning(self, "Push Notification", "Please enter a message.")
            return
        title    = self.title_edit.text().strip() or "FreeCAD"
        priority = self.PRIORITY_MAP[self.priority_combo.currentText()]
        tags_raw = self.tags_edit.text().strip()
        tags     = [t.strip() for t in tags_raw.split(",") if t.strip()]
        core.send(core.Notification(
            message=message, title=title, priority=priority, tags=tags
        ))
        self.accept()


# ──────────────────────────────────────────────────────────────
# Command: Quick "Success" notification
# ──────────────────────────────────────────────────────────────
class PNS_NotifySuccess:
    def GetResources(self):
        return {
            "Pixmap":   icon("success.svg"),
            "MenuText": "Notify: Success",
            "ToolTip":  "Send a success push notification",
        }

    def IsActive(self):
        return True

    def Activated(self):
        doc_name = ""
        if FreeCAD.ActiveDocument:
            doc_name = FreeCAD.ActiveDocument.Name
        msg = f"Task completed successfully.{(' – ' + doc_name) if doc_name else ''}"
        core.notify_success(msg)
        FreeCAD.Console.PrintMessage("[Push Notification] Success notification sent.\n")


# ──────────────────────────────────────────────────────────────
# Command: Quick "Error" notification
# ──────────────────────────────────────────────────────────────
class PNS_NotifyError:
    def GetResources(self):
        return {
            "Pixmap":   icon("error.svg"),
            "MenuText": "Notify: Error",
            "ToolTip":  "Send an error/alert push notification",
        }

    def IsActive(self):
        return True

    def Activated(self):
        msg, ok = QtWidgets.QInputDialog.getText(
            FreeCADGui.getMainWindow(),
            "Push Notification – Error Notification",
            "Error message to send:"
        )
        if ok and msg:
            core.notify_error(msg)


# ──────────────────────────────────────────────────────────────
# Command: Notify render done
# ──────────────────────────────────────────────────────────────
class PNS_NotifyRenderDone:
    def GetResources(self):
        return {
            "Pixmap":   icon("render.svg"),
            "MenuText": "Notify: Render Done",
            "ToolTip":  "Send 'Render Done' push notification",
        }

    def IsActive(self):
        return True

    def Activated(self):
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(
            FreeCADGui.getMainWindow(),
            "Select rendered file (optional)",
            "",
            "Images (*.png *.jpg *.exr *.hdr);;All Files (*)"
        )
        core.notify_render_done(fname)


# ──────────────────────────────────────────────────────────────
# Command: Test connection
# ──────────────────────────────────────────────────────────────
class PNS_TestConnection:
    def GetResources(self):
        return {
            "Pixmap":   icon("test.svg"),
            "MenuText": "Test Connection",
            "ToolTip":  "Send a test notification to verify configuration",
        }

    def IsActive(self):
        return True

    def Activated(self):
        core.send(
            core.Notification(
                message="Push Notification workbench is connected and working! ✅",
                title="🔧 Push Notification Test",
                priority=3,
                tags=["wrench", "white_check_mark"],
            ),
            blocking=False,
        )
        QtWidgets.QMessageBox.information(
            FreeCADGui.getMainWindow(),
            "Push Notification",
            f"Test notification sent to:\n{core.get_server_url()}/{core.get_topic()}\n\n"
            f"Check your iPhone app!"
        )


# ──────────────────────────────────────────────────────────────
# Command: Create Notification Definition
# ──────────────────────────────────────────────────────────────
class PNS_CreateNotificationDefinition:
    def GetResources(self):
        return {
            "Pixmap":   icon("push_notification_icon.svg"),
            "MenuText": "Create Notification Definition",
            "ToolTip":  "Create a notification definition object in the Notifications folder",
        }

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

    def Activated(self):
        # Ask for notification name
        name, ok = QtWidgets.QInputDialog.getText(
            FreeCADGui.getMainWindow(),
            "Create Notification Definition",
            "Enter name for notification definition:",
            text="Notification"
        )
        if not ok or not name.strip():
            return
        
        # Create notification in folder
        notification = objects.create_notification_in_folder(name.strip())
        if notification:
            QtWidgets.QMessageBox.information(
                FreeCADGui.getMainWindow(),
                "Push Notification",
                f"Created notification definition '{name}' in Notifications folder."
            )
        else:
            QtWidgets.QMessageBox.critical(
                FreeCADGui.getMainWindow(),
                "Push Notification",
                f"Failed to create notification definition."
            )


# ──────────────────────────────────────────────────────────────
# Command: Settings dialog
# ──────────────────────────────────────────────────────────────
class PNS_Settings:
    def GetResources(self):
        return {
            "Pixmap":   icon("settings.svg"),
            "MenuText": "PNS Settings…",
            "ToolTip":  "Configure the Push Notification server and topic",
        }

    def IsActive(self):
        return True

    def Activated(self):
        dlg = SettingsDialog(FreeCADGui.getMainWindow())
        dlg.exec()


class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Push Notification Settings")
        self.setMinimumWidth(460)
        self._build_ui()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # ── Server section ──────────────────────────
        server_group = QtWidgets.QGroupBox("ntfy Server")
        server_form  = QtWidgets.QFormLayout(server_group)

        self.server_edit = QtWidgets.QLineEdit(core.get_server_url())
        self.server_edit.setPlaceholderText("https://ntfy.sh")
        server_form.addRow("Server URL:", self.server_edit)

        self.topic_edit = QtWidgets.QLineEdit(core.get_topic())
        self.topic_edit.setPlaceholderText("push-notification")
        server_form.addRow("Topic:", self.topic_edit)

        self.token_edit = QtWidgets.QLineEdit(core.get_token())
        self.token_edit.setPlaceholderText("(optional – for private topics)")
        self.token_edit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        server_form.addRow("Auth Token:", self.token_edit)

        layout.addWidget(server_group)

        # ── Notification behaviour ──────────────────
        behav_group = QtWidgets.QGroupBox("Automatic Notifications")
        behav_layout = QtWidgets.QVBoxLayout(behav_group)

        self.chk_error = QtWidgets.QCheckBox("Notify on FreeCAD error")
        self.chk_error.setChecked(core.get_notify_on_error())
        behav_layout.addWidget(self.chk_error)

        self.chk_save = QtWidgets.QCheckBox("Notify on document save")
        self.chk_save.setChecked(core.get_notify_on_save())
        behav_layout.addWidget(self.chk_save)

        layout.addWidget(behav_group)

        # ── Topic URL preview ───────────────────────
        self.preview_label = QtWidgets.QLabel()
        self.preview_label.setWordWrap(True)
        self.preview_label.setStyleSheet("color: grey; font-size: 11px;")
        self._update_preview()
        self.server_edit.textChanged.connect(self._update_preview)
        self.topic_edit.textChanged.connect(self._update_preview)
        layout.addWidget(self.preview_label)

        # ── Buttons ─────────────────────────────────
        btn_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Save | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.accepted.connect(self._save)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def _update_preview(self):
        url = self.server_edit.text().rstrip("/")
        topic = self.topic_edit.text().strip()
        self.preview_label.setText(f"📲 iPhone subscribes to: {url}/{topic}/json")

    def _save(self):
        core.set_server_url(self.server_edit.text().strip())
        core.set_topic(self.topic_edit.text().strip())
        core.set_token(self.token_edit.text().strip())
        core.set_notify_on_error(self.chk_error.isChecked())
        core.set_notify_on_save(self.chk_save.isChecked())
        FreeCAD.Console.PrintMessage("[Push Notification] Settings saved.\n")
        self.accept()


# ──────────────────────────────────────────────────────────────
# Register all commands
# ──────────────────────────────────────────────────────────────
for _cmd_class in [
    PNS_Notify, PNS_NotifySuccess, PNS_NotifyError,
    PNS_NotifyRenderDone, PNS_TestConnection, PNS_Settings,
    PNS_CreateNotificationDefinition,
]:
    FreeCADGui.addCommand(_cmd_class.__name__, _cmd_class())
