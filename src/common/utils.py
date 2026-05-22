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
from collections import namedtuple
from types import SimpleNamespace

class Utils:

    @staticmethod
    def dict_to_namedtuple(typename, data):
        """
        dictオブジェクトを再帰的にnamedtupleに変換する
        """
        return namedtuple(typename, data.keys())(
            *(Utils.dict_to_namedtuple(typename + '_' + k, v) if isinstance(v, dict) else v for k, v in data.items())
        )

    @staticmethod
    def dict_to_simplenamespace(data):
        """
        dictオブジェクトを再帰的にSimpleNamaspaceに変換する
        """
        if isinstance(data, dict):
            return SimpleNamespace(**{k: Utils.dict_to_simplenamespace(v) for k, v in data.items()})
        elif isinstance(data, list):
            return [Utils.dict_to_simplenamespace(v) for v in data]
        return data
