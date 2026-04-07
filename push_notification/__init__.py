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
push_notification — public API
Import this module in macros:

    from push_notification import notify, notify_success, notify_error
    notify("My custom message", title="Step 3 done", priority=3)
"""

from push_notification.core import (
    notify,
    notify_success,
    notify_error,
    notify_warning,
    notify_render_done,
    notify_export_done,
    notify_fem_done,
    send,
    Notification,
)

__all__ = [
    "notify",
    "notify_success",
    "notify_error",
    "notify_warning",
    "notify_render_done",
    "notify_export_done",
    "notify_fem_done",
    "send",
    "Notification",
]

__version__ = "1.0.0"
