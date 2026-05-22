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

from abc import ABC, abstractmethod
from logging import Logger
from types import SimpleNamespace

from common import Common, OutputItem

class ReportBase(ABC):
    config:SimpleNamespace = None
    common:Common = None
    log:Logger = None
    azclass:type = None

    def __init__(self, common):
        assert isinstance(common, Common)
        self.common = common
        self.log = common.log

    @abstractmethod
    def check_config(self, azclass:type, config):
        pass

    @abstractmethod
    def process_message(self, in_msg, out_item:OutputItem) -> OutputItem:
        return out_item

    def check(self, azclass:type, config):
        self.azclass = azclass
        self.config = SimpleNamespace(**config)
        print(f"{azclass.__name__}: {self.config}")
        self.check_config(azclass, self.config)

    def process(self, in_msg):
        assert self.config is not None
        out_item = OutputItem(
            config=SimpleNamespace(**self.config.Output),
            config_training=SimpleNamespace(**self.config.OutputTraining)
        )
        out_item = self.process_message(in_msg, out_item)
        self.common.output_message(out_item)
