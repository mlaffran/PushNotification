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
# *    ##  PushNotification FreeCAD WorkBench 2026.04.16 1341 ##             *
# *     ##########################################################               *
# *                                                                              *
# *                   Authors of this workbench:                                 *
# *           Marco Laffranchi <Laffranchi.Marco@gmail.com>                      *
# *                                                                              *
# *          Please refer to the Documentation and README for                    *
# *      more information regarding this WorkBench and its usage                 *
# *                                                                              *
# ********************************************************************************
"""push_notification public API."""

from push_notification.core import (
    Notification,
    SUPPORTED_TRIGGERS,
    TRIGGER_DOCUMENT_SAVED,
    TRIGGER_FREECAD_ERROR,
    emit_trigger,
    install_hooks,
    notify,
    notify_error,
    notify_export_done,
    notify_fem_done,
    notify_render_done,
    notify_success,
    notify_warning,
    send,
)

from push_notification.objects import (
    NotificationDefinition,
    ViewProviderNotificationDefinition,
    create_notification_definition,
    create_notification_in_folder,
    ensure_notification_folder,
)

__all__ = [
    "Notification",
    "SUPPORTED_TRIGGERS",
    "TRIGGER_DOCUMENT_SAVED",
    "TRIGGER_FREECAD_ERROR",
    "emit_trigger",
    "install_hooks",
    "notify",
    "notify_error",
    "notify_export_done",
    "notify_fem_done",
    "notify_render_done",
    "notify_success",
    "notify_warning",
    "send",
    "NotificationDefinition",
    "ViewProviderNotificationDefinition",
    "create_notification_definition",
    "create_notification_in_folder",
    "ensure_notification_folder",
]

__version__ = "1.1.0"
