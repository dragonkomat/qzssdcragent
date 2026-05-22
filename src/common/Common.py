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

import argparse
from logging import Logger
from types import SimpleNamespace

from common import OutputItem
from inout import Input, Email, ReportFile, StdOut

class Common:
    args:argparse.Namespace = None
    log:Logger = None
    config:SimpleNamespace = None

    def __init__(self):
        self.input = Input(self)
        self.email = Email(self)
        self.report_file = ReportFile(self)
        self.stdout = StdOut(self)

    def check_config(self, config):
        self.config = SimpleNamespace(**config)
        config_output = SimpleNamespace(**self.config.Output)
        self.input.check_config(self.config.Input)
        self.email.check_config(config_output.Email)
        self.report_file.check_config(config_output.ReportFile)
        self.stdout.check_config(config_output.StdOut)

    def start(self):
        pass

    def output_message(self, out_item:OutputItem):
        pass
