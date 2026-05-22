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
import logging
from logging import handlers
from types import SimpleNamespace

from item import *
from common import *
from inout import *

class ReportFile(IOBase):

    def __init__(self, common:Common):
        super().__init__(common)
        self.report_file:logging.Logger = None

    def check_config(self, config:SimpleNamespace):
        super().check_config(config)

        common = self.common
        log = common.log

        # レポートファイルの準備
        report_file = logging.getLogger("report")
        if config.Use:
            log.info(f"Report file is {config.Path}")
            report_handler = handlers.TimedRotatingFileHandler(
                filename=config.Path,
                when=config.When,
                interval=config.Interval,
                backupCount=config.BackupCount,
                encoding="utf-8"
                )
            report_formatter = logging.Formatter("%(message)s")
            report_handler.setFormatter(report_formatter)
        else:
            report_handler = logging.NullHandler()
        report_file.addHandler(report_handler)
        report_file.setLevel(logging.INFO)
        self.report_file = report_file

    def output_message(self, item_out:OutputItem):

        # 出力可否の判定
        if self.config.Use is False:
            return
        if item_out.training:
            if item_out.config_training.ReportFile is False:
                return
        else:
            if item_out.config.ReportFile is False:
                return

        # 出力データの生成        
        outstr = f"----- {item_out.timestamp.isoformat()} {item_out.azclass.__name__} --------------------\n"
        if self.config.EmailStyle:
            if self.config.WithNmea:
                outstr += f"NMEA: {item_out.nmea}\n"
            outstr += f"Subject: {item_out.mail_subject}\n"
            outstr += f"Text:\n{item_out.mail_text}\n"
        else:
            if self.config.WithNmea:
                outstr += f"{item_out.nmea}\n"
            outstr += f"{item_out.message}\n"

        # 出力
        self.report_file.info(outstr)
