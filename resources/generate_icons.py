#!/usr/bin/env python3
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
"""Generate simple SVG icons for the Push Notification toolbar."""

import os

ICONS = {
    "notify.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="10" fill="#1565C0"/>
  <path d="M32 8a14 14 0 0 0-14 14v12l-4 6h36l-4-6V22A14 14 0 0 0 32 8z" fill="#FFF9C4"/>
  <path d="M26 40a6 6 0 0 0 12 0" fill="#FFF9C4"/>
  <circle cx="32" cy="14" r="3" fill="#FF8F00"/>
</svg>""",

    "success.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="10" fill="#2E7D32"/>
  <path d="M32 8a14 14 0 0 0-14 14v12l-4 6h36l-4-6V22A14 14 0 0 0 32 8z" fill="#C8E6C9"/>
  <path d="M26 40a6 6 0 0 0 12 0" fill="#C8E6C9"/>
  <path d="M20 34l8 8 16-16" stroke="#fff" stroke-width="4" stroke-linecap="round" fill="none"/>
</svg>""",

    "error.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="10" fill="#B71C1C"/>
  <path d="M32 8a14 14 0 0 0-14 14v12l-4 6h36l-4-6V22A14 14 0 0 0 32 8z" fill="#FFCDD2"/>
  <path d="M26 40a6 6 0 0 0 12 0" fill="#FFCDD2"/>
  <text x="32" y="38" text-anchor="middle" font-size="22" font-weight="bold" fill="#fff">!</text>
</svg>""",

    "render.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="10" fill="#4527A0"/>
  <rect x="8" y="14" width="48" height="36" rx="4" fill="#D1C4E9"/>
  <circle cx="20" cy="25" r="5" fill="#FFD54F"/>
  <path d="M8 36l14-12 10 10 8-8 14 14H8z" fill="#7E57C2"/>
  <rect x="24" y="46" width="16" height="4" rx="2" fill="#9575CD"/>
</svg>""",

    "settings.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="10" fill="#37474F"/>
  <circle cx="32" cy="32" r="8" fill="#B0BEC5"/>
  <path d="M32 10v8M32 46v8M10 32h8M46 32h8
           M17.5 17.5l5.6 5.6M40.9 40.9l5.6 5.6
           M17.5 46.5l5.6-5.6M40.9 23.1l5.6-5.6"
        stroke="#CFD8DC" stroke-width="4" stroke-linecap="round"/>
</svg>""",

    "test.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="10" fill="#00695C"/>
  <path d="M20 10h24v6l8 28H16L24 16z" fill="#B2DFDB" opacity=".9"/>
  <circle cx="24" cy="46" r="4" fill="#4DB6AC"/>
  <circle cx="32" cy="50" r="4" fill="#4DB6AC"/>
  <circle cx="40" cy="46" r="4" fill="#4DB6AC"/>
  <text x="32" y="28" text-anchor="middle" font-size="14" font-weight="bold" fill="#004D40">TEST</text>
</svg>""",
}

out_dir = os.path.dirname(os.path.abspath(__file__))
for name, svg in ICONS.items():
    path = os.path.join(out_dir, name)
    with open(path, "w") as f:
        f.write(svg)
    print(f"  Created {path}")

print("Icons generated.")
