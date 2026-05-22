# MIT License
#
# Copyright (c) 2026 Toyohiko Komatsu (dragonkomat)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# -*- coding: utf-8 -*-

from __future__ import annotations
from types import SimpleNamespace

from azarashi.qzss_dcr_lib.report.qzss_dc_report import QzssDcReportJmaHypocenter

from report import *
from item import *
from common import *

class DcrJmaHypocenter(DcrReportBase):
    def __init__(self, common:Common):
        super().__init__(common)

    def check_config(self, azclass:type, config:SimpleNamespace):
        assert azclass == QzssDcReportJmaHypocenter
        super().check_config(azclass, config)

    def process_message(self, item_in:InputItem, item_out:OutputItem) -> OutputItem:
        assert isinstance(item_in.report, QzssDcReportJmaHypocenter)
        item_out = super().process_message(item_in, item_out)
        return item_out
