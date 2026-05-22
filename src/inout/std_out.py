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

from item import *
from common import *
from inout import *

class StdOut(IOBase):

    def __init__(self, common:Common):
        super().__init__(common)

    def check_config(self, config:SimpleNamespace):
        super().check_config(config)

    def output_message(self, item_out:OutputItem):

        # 出力可否の判定
        if self.config.Use is False:
            return
        if item_out.training:
            if self.config.BlockTraining:
                return
            if item_out.config_training.StdOut is False:
                return
        else:
            if item_out.config.StdOut is False:
                return

        # 出力
        outstr = f"----- {item_out.timestamp.isoformat()} {item_out.azclass.__name__} --------------------\n"
        if self.config.WithFilteredNmea and item_out.match is False:
            # フィルターにマッチしていないがWithFilteredNmeaがTrueの場合
            if self.config.EmailStyle:
                outstr += f"NMEA: {item_out.nmea}"
            else:
                outstr += f"{item_out.nmea}"
            print(outstr)
        else:
            if item_out.match:
                if self.config.EmailStyle:
                    if self.config.WithNmea:
                        outstr += f"NMEA: {item_out.nmea}\n"
                    outstr += f"Subject: {item_out.mail_subject}\n"
                    outstr += f"Text:\n{item_out.mail_text}"
                else:
                    if self.config.WithNmea:
                        outstr += f"{item_out.nmea}\n"
                    outstr += f"{item_out.message}"
                print(outstr)
            else:
                pass
