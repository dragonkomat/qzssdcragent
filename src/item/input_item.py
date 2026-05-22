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
from datetime import datetime

from azarashi.qzss_dcr_lib.report.qzss_dc_report import *

class InputItem:
    
    def __init__(self, report:QzssDcReportBase):
        self.report = report

    def is_training(self) -> bool:
        """
        訓練・試験かどうか
        """
        report = self.report

        if isinstance(report, QzssDcReportJmaBase):
            if report.report_classification_no == 7:
                return True
        elif isinstance(report, QzssDcXtendedMessageBase):
            camf = report.camf
            # 参照: QzssDcXtendedMessageBase.__init__()
            # 参照: QzssDcxDecoder.decode()
            if camf.a1 == 0:
                return True
            elif camf.a4 == 13 or camf.a4 == 113:
                # 参照: qzss_dcx_camf_a4_hazard_type
                return True
            elif camf.a9 == 0 and camf.a11 == 29:
                # 参照: qzss_dcx_camf_a11_international_library
                return True
            elif camf.a9 == 1 and (camf.a11 == 126 or camf.a11 == 136):
                # 参照: qzss_dcx_camf_a11_japanese_library_ja
                return True
            elif report.ignore_a17_to_a18 is False and camf.a17 == 2:
                # B3 – second ellipse definition
                if camf.c10 == 30:
                    # 参照: qzss_dcx_camf_c10_guidance_library_for_second_ellipse
                    return True
        return False

    def is_cancelation(self) -> bool:
        """
        取り消しかどうか (解除ではない)
        """
        report = self.report

        if isinstance(report, QzssDcReportJmaBase):
            if report.report_classification_no == 2:
                return True        
        return False

    def is_partial(self) -> bool:
        """
        部分的かどうか

        南海トラフ地震情報が受信中の場合など
        """
        report = self.report
        if isinstance(report, QzssDcReportJmaNankaiTroughEarthquake):
            if report.completed is False:
                return True
        return False
