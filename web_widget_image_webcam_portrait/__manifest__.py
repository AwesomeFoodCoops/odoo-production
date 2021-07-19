##############################################################################
#
#    Copyright since 2009 Trobz (<https://trobz.com/>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "Web Widget - Image WebCam - Portrait",
    "summary": "Allows to take image with WebCam in Portrait",
    "version": "12.0.1.0.0",
    "category": "web",
    "author": "Tech Receptives, "
              "Kaushal Prajapati, "
              "Odoo Community Association (OCA), "
              "Trobz",
    "license": "LGPL-3",
    "data": [
        "views/assets.xml",
    ],
    "depends": [
        "web_widget_image_webcam",
    ],
    "qweb": [
        "static/src/xml/web_widget_image_webcam.xml",
    ],
    "installable": True,
}
