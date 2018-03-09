#!/usr/bin/env python
# Copyright (C) 2011-2014 Swift Navigation Inc.
# Contact: Fergus Noble <fergus@swift-nav.com>
#
# This source is subject to the license found in the file 'LICENSE' which must
# be be distributed together with this source. All other rights reserved.
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND,
# EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A PARTICULAR PURPOSE.

from __future__ import absolute_import

import datetime

from sbp.piksi import SBP_MSG_NETWORK_BANDWIDTH_USAGE
from traits.api import Dict, HasTraits, Int, List, String
from traitsui.api import Item, TabularEditor, VGroup, View
from traitsui.tabular_adapter import TabularAdapter

from .utils import sizeof_fmt


# helper function to format seconds to hh:mm:ss
def duration_format(**kwargs):
    return str(datetime.timedelta(**kwargs))


class CellModemView(HasTraits):
    python_console_cmds = Dict()
    _cell_modem_usage = String
    _cell_modem_measurement_duration = String

    traits_view = View(
        VGroup(
            Item(
                '_cell_modem_usage',
                label='Data Consumption (Tx/Rx)',
                style='readonly'
            ),
            Item(
                '_cell_modem_measurement_duration',
                label='Period of Consumption',
                style='readonly'
            ),
            label='Cellular Bandwidth Usage',
            show_border=True
        ),
    )

    def _set_network_usage(self, interface_name, duration, tx_usage, rx_usage):
        self._cell_modem_usage  = "{}/{} ({})".format(tx_usage,
                                                      rx_usage,
                                                      interface_name)
        self._cell_modem_measurement_duration = duration

    def _network_callback(self, m, **metadata):
        for interface in m.interfaces:
            stripped_name = interface.interface_name.rstrip('\0')
            if stripped_name == self.cellmodem_interface_name:
                self._set_network_usage(stripped_name,
                                        duration_format(milliseconds=interface.duration),
                                        sizeof_fmt(interface.tx_bytes),
                                        sizeof_fmt(interface.rx_bytes))

    def __init__(self, link):
        super(CellModemView, self).__init__()
        #self.cellmodem_interface_name = "ppp0"
        self.cellmodem_interface_name = "eth0"
        self._set_network_usage(self.cellmodem_interface_name, "-", "-", "-")
        self.link = link
        self.link.add_callback(self._network_callback,
                               SBP_MSG_NETWORK_BANDWIDTH_USAGE)

        self.python_console_cmds = {'cell': self}
