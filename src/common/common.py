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
import argparse
from copy import deepcopy
from logging import Logger
import sys
from types import SimpleNamespace
from ruamel.yaml import YAML
from pathlib import Path
import threading

from azarashi.qzss_dcr_lib.report.qzss_dc_report import *

from item import *
from report import *
from common import Utils
from inout import *

class Common:

    def __init__(self, args:argparse.Namespace, log:Logger):
        self.args = args
        self.log = log
        self.config = None
        assert self.args is not None
        assert self.log is not None

        # 入出力クラス群のオブジェクトの生成
        self.input = Input(self)
        self.email = Email(self)
        self.report_file = ReportFile(self)
        self.stdout = StdOut(self)

        # レポート処理テーブルの生成
        # レポート処理クラス群のオブジェクトの生成
        self.report_types = {
            QzssDcReportJmaAshFall:                 DcrJmaAshFall(self),
            QzssDcReportJmaEarthquakeEarlyWarning:  DcrJmaEarthquakeEarlyWarning(self),
            QzssDcReportJmaFlood:                   DcrJmaFlood(self),
            QzssDcReportJmaHypocenter:              DcrJmaHypocenter(self),
            QzssDcReportJmaMarine:                  DcrJmaMarine(self),
            QzssDcReportJmaNankaiTroughEarthquake:  DcrJmaNankaiTroughEarthquake(self),
            QzssDcReportJmaNorthwestPacificTsunami: DcrJmaNorthwestPacificTsunami(self),
            QzssDcReportJmaSeismicIntensity:        DcrJmaSeismicIntensity(self),
            QzssDcReportJmaTsunami:                 DcrJmaTsunami(self),
            QzssDcReportJmaTyphoon:                 DcrJmaTyphoon(self),
            QzssDcReportJmaVolcano:                 DcrJmaVolcano(self),
            QzssDcReportJmaWeather:                 DcrJmaWeather(self),
            QzssDcxJAlert:                          DcxJAlert(self),
            QzssDcxLAlert:                          DcxLAlert(self),
            QzssDcxMTInfo:                          DcxMTInfo(self),
            QzssDcxNullMsg:                         DcxNullMsg(self),
            QzssDcxOutsideJapan:                    DcxOutsideJapan(self),
            QzssDcxUnknown:                         DcxUnknown(self)
        }

        # 設定ファイルのロードと確認
        self.config_all = self.load_config()
        self.check_config()

        # ロックオブジェクトの初期化
        self.lock_report = threading.Lock()

        # 状態確認タイマーの初期化
        assert self.config is not None
        self.check_state_timer = Utils.RepeatTimer(
            float(self.config.StateCheckPeriod),
            self.check_state
        )

    def load_config(self) -> SimpleNamespace:
        """
        設定ファイルのロード
        """
        args = self.args

        yaml = YAML(typ="safe", pure=True)
        config = yaml.load(Path(args.config_file))
        config_sns = Utils.dict_to_simplenamespace(config)
        return config_sns

    def check_config(self):
        """
        設定データの適用と確認
        """
        assert self.config_all is not None
        config_all = self.config_all
        self.config = config_all.Common

        # 各レポート処理クラスへの設定の適用
        for key in self.report_types.keys():

            # レポートクラス毎にデフォルト値とレポートクラス固有設定値をマージする
            if hasattr(config_all.Report, key.__name__):
                conf_report_child = getattr(config_all.Report, key.__name__)
            else:
                conf_report_child = None
            if conf_report_child is None:
                conf_report_child = deepcopy(config_all.Report.Default)
            else:
                assert type(conf_report_child) == SimpleNamespace
                conf_report_child = SimpleNamespace(**(config_all.Report.Default.__dict__ | conf_report_child.__dict__))
 
            # 設定の適用
            self.report_types[key].check(key, conf_report_child)

        # 入出力クラスへの設定の適用
        self.input.check_config(config_all.Input)
        self.email.check_config(config_all.Output.Email)
        self.report_file.check_config(config_all.Output.ReportFile)
        self.stdout.check_config(config_all.Output.StdOut)

        if self.args.test_only:
            self.log.info("Check completed.")
            sys.exit(0)

    def check_state(self):

        # 各レポート処理クラスの状態の確認
        with self.lock_report:
            for key in self.report_types.keys():
                    self.report_types[key].check_state()
        
    def process_message(self, item_in:InputItem):
        log = self.log
        
        with self.lock_report:
            reporttype = type(item_in.report)
            if reporttype in self.report_types:
                self.report_types[reporttype].process(item_in)
            else:
                log.warning(f"Unexpected report type: {reporttype}")

    def output_message(self, item_out:OutputItem):
        if item_out.use:
            self.stdout.output_message(item_out)
            self.report_file.output_message(item_out)
            self.email.output_message(item_out)

    def start(self):
        self.input.load_cache()
        self.check_state_timer.start()   
        self.input.message_loop()       # 戻ってこない

    def signal_handler(self, signum, frame):
        log = self.log
        log.warning(f"Signal handler called with signal {signum}.")

        # タイマー(スレッド)を止める
        if self.check_state_timer.is_alive():
            self.check_state_timer.cancel()

        self.input.save_cache()
