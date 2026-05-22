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

from azarashi.qzss_dcr_lib.report.qzss_dc_report import *

from item import InputItem

class OutputItem:
    DATETIME_FORMAT = "%Y/%m/%d %H:%M:%S"

    def __init__(self, /,
                    item_in:InputItem,
                    use:bool,
                    config:SimpleNamespace,
                    config_training:SimpleNamespace):

        self.azclass = type(item_in.report)
        self.use = use
        self.config = config
        self.config_training = config_training

        report = item_in.report

        # 追加のアトリビュートの設定
        self.nmea = report.nmea
        self.timestamp = item_in.report.timestamp
        self.training = item_in.is_training()
        self.partial = item_in.is_partial()
        self.cancelation = item_in.is_cancelation()

        # ファイル出力用の既定のメッセージ
        self.message = str(report)

        # メール送信用の既定のメッセージ
        mail_text = str(report)
        mail_subject = ""
        if isinstance(report, QzssDcXtendedMessageBase):
            if isinstance(report, QzssDcxJAlert):
                mail_subject = "J-Alert"
            elif isinstance(report, QzssDcxLAlert):
                mail_subject = "L-Alert"
            elif isinstance(report, QzssDcxMTInfo):
                mail_subject = "Municipality-Transmitted Information"
            elif isinstance(report, QzssDcxOutsideJapan):
                mail_subject = "Information from Organizations outside Japan"
            else:
                mail_subject = f"不明なクラス({type(report)})"
            if self.training:
                mail_subject = "[訓練/試験]" + mail_subject
            mail_subject = "災危情報: " + mail_subject
        elif isinstance(report, QzssDcReportJmaBase):
            mail_subject = report.get_header()
            # 本文に含まれるヘッダーを取り除く
            mail_text = mail_text.replace(mail_subject,"",1)
        else:
            mail_subject = f"災危情報: 不明なクラス({type(report)})"
        mail_text += f"\n\n情報受信時刻: {report.timestamp.strftime(self.DATETIME_FORMAT)}\n"

        self.mail_text = mail_text
        self.mail_subject = mail_subject
