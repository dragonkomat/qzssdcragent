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

from common import OutputItem
from report import DcxReportBase
from azarashi.qzss_dcr_lib.report.qzss_dc_report import QzssDcxNullMsg

class DcxNullMsg(DcxReportBase):
    def __init__(self, common):
        super(DcxNullMsg, self).__init__(common)

    def check_config(self, azclass:type, config):
        assert azclass == QzssDcxNullMsg
        super(DcxNullMsg, self).check_config(azclass, config)
    
    def process_message(self, in_msg, out_item:OutputItem) -> OutputItem:
        assert isinstance(in_msg, QzssDcxNullMsg)
        out_item = super(DcxNullMsg, self).process_message(in_msg, out_item)
        return out_item
