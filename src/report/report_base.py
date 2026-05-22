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
from abc import ABC, abstractmethod
from logging import Logger
from types import SimpleNamespace
from typing import TYPE_CHECKING

from item import *
from common import *
import pdb

class ReportBase(ABC):

    def __init__(self, common:Common):
        self.common = common
        self.config:SimpleNamespace = None
        self.azclass:type = None
        self.state = SimpleNamespace()

    @abstractmethod
    def check_config(self, azclass:type, config:SimpleNamespace):
        pass

    @abstractmethod
    def process_message(self, in_msg, out_item:OutputItem) -> OutputItem:
        return out_item

    def check_filter_keywords(self, filter_keywords:list, keyword_table):
        """
        "Filter"に設定されたキーワードが設定可能なものかを確認する

        戻り値がTrue: filter_keywordsに指定された全てのキーワードがkeyword_tableに含まれる
        """
        # フィルターが未設定の場合はチェックしない
        if filter_keywords is None or len(filter_keywords) == 0:
            return True
        for keyword in filter_keywords:
            if (keyword in keyword_table) is False:
                # 含まれてない場合
                # TODO: エラー出力後、例外発生→終了
                pdb.set_trace()
                return False
        return True

    def match_filter_keywords(self, filter_keywords:list, keywords):
        """
        keywordsに指定された文字列(or 文字列リストの内のいずれかの文字列)がfilter_keywordsに含まれるか確認する

        戻り値がTrue: keywordsの1つがfilter_keywordsに含まれる
        """
        # フィルターが未設定の場合は「含まれている」扱い
        if filter_keywords is None or len(filter_keywords) == 0:
            return True
        if isinstance(keywords, list):
            for keyword in keywords:
                if keyword in filter_keywords:
                    return True
        else:
            if keywords in filter_keywords:
                return True
        return False

    def check(self, azclass:type, config:SimpleNamespace):
        self.azclass = azclass
        self.config = config
        print(f"{azclass.__name__}: {self.config}")
        self.check_config(azclass, self.config)

    def process(self, item_in):
        common = self.common
        config = self.config
        assert config is not None
        assert self.azclass == type(item_in.report)

        item_out = OutputItem(
            item_in=item_in,
            use=config.Use,
            config=config.Output,
            config_training=config.OutputTraining)

        item_out = self.process_message(item_in, item_out)
        common.output_message(item_out)
