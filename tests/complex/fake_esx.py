from __future__ import print_function

#
# Module for abstraction of all virtualization backends, part of virt-who
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

import sys
import time

from xml.etree import ElementTree

from fake_virt import FakeVirt
from fake_server import FakeHandler


class EsxHandler(FakeHandler):
    def do_GET(self):
        print('[FakeEsx] GET', self.path)

    def do_POST(self):
        print("[FakeEsx] POST", self.path)
        if self.path == '/sdk':
            try:
                length = int(self.headers.getheader('content-length'))
            except AttributeError:
                length = int(self.headers.get('content-length'))
            data = self.rfile.read(length)
            xml = ElementTree.fromstring(data)
            body = xml.find('{http://schemas.xmlsoap.org/soap/envelope/}Body')
            root = body[0]
            print("[FakeEsx] post ", self.path, root.tag, self.server._data_version.value)

            if 'RetrieveServiceContent' in root.tag:
                self.write_file('esx', 'esx_retrieveservicecontent.xml')
            elif 'Login' in root.tag:
                if root.find('{urn:vim25}userName').text != 'A!bc3#\'"' or \
                        root.find('{urn:vim25}password').text != 'A!bc3#\'"':
                    self.send_error(401, 'Cannot complete login due to an incorrect user name or password.')
                self.write_file('esx', 'esx_loginresponse.xml')
            elif 'Logout' in root.tag:
                self.write_file('esx', 'esx_logoutresponse.xml')
            elif 'CreateFilter' in root.tag:
                self.write_file('esx', 'esx_createfilterresponse.xml')
            elif 'WaitForUpdatesEx' in root.tag:
                time.sleep(1)
                version = self.server._data_version.value
                self.write_file('esx', 'esx_waitforupdatesexresponse_%d.xml' % version)
            elif 'CancelWaitForUpdatesEx' in root.tag:
                self.write_file('esx', 'esx_cancelwaitforupdatesexresponse.xml')
            elif 'DestroyPropertyFilter' in root.tag:
                self.write_file('esx', 'esx_destroypropertyfilterresponse.xml')


class FakeEsx(FakeVirt):

    virt_type = "esx"

    def __init__(self, port=None):
        super(FakeEsx, self).__init__(EsxHandler, port=port)
        self.server._data_version = self._data_version


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        port = int(sys.argv[1])
    else:
        port = None

    esx = FakeEsx(port)
    print(esx.virt_who_config())
    esx.run()
