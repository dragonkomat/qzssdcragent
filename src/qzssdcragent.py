#!/usr/bin/env python3

# MIT License
#
# Copyright (c) 2023 Toyohiko Komatsu (dragonkomat)
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
import configparser
import signal
import smtplib
import ssl
import subprocess
import sys
import os
import time
import io
from datetime import datetime, timedelta
from email.mime.text import MIMEText
import logging
from logging import handlers
import dill
#import pdb

import azarashi
from azarashi.qzss_dcr_lib.definition import *
from azarashi.qzss_dcr_lib.report import qzss_dc_report

DATETIME_FORMAT = '%Y/%m/%d %H:%M:%S'

DEFAULT_CONFPATH = '/etc/qzssdcragent.conf'

DEFAULT_CACHEPATH = '/var/cache/qzssdcragent_cache.bin'

DEFAULT_CONFIG = {
    'QzssDcReportJmaAshFall' : {
        'Use':1,
        'LocalGovernments':'',
        },
    'QzssDcReportJmaEarthquakeEarlyWarning' : {
        'Use':1,
        'Regions':'',
        },
    'QzssDcReportJmaFlood' : {
        'Use':1,
        'Regions':'',
        },
    'QzssDcReportJmaHypocenter' : {
        'Use':1,
        },
    'QzssDcReportJmaMarine' : {
        'Use':1,
        'Regions':'',
        },
    'QzssDcReportJmaNankaiTroughEarthquake' : {
        'Use':1,
        },
    'QzssDcReportJmaNorthwestPacificTsunami' : {
        'Use':1,
        'Regions':'',
        },
    'QzssDcReportJmaSeismicIntensity' : {
        'Use':1,
        'Prefectures':'',
        },
    'QzssDcReportJmaTsunami' : {
        'Use':1,
        'Regions':'',
        },
    'QzssDcReportJmaTyphoon' : {
        'Use':1,
        },
    'QzssDcReportJmaVolcano' : {
        'Use':1,
        'LocalGovernments':'',
        },
    'QzssDcReportJmaWeather' : {
        'Use':1,
        'Regions':'',
        },
    'QzssDcxJAlert' : {
        'Use':0,
        },
    'QzssDcxLAlert' : {
        'Use':0,
        },
    'QzssDcxMTInfo' : {
        'Use':0,
        },
    'QzssDcxOutsideJapan' : {
        'Use':0,
        },
    'Input' : {
        'CmdLine':'gpspipe -R',
        'Type':'ublox',
        'CacheValidPeriodHour':24,
        'IgnoreFilterWhenTraining':1,
        },
    'ReportFile' : {
        'Use':1,
        'Path':'/var/log/qzssdcragent.log',
        'When':'D',
        'Interval':7,
        'BackupCount':5,
        'ReportIncompleteInfo':0,
        'IgnoreFilter':0,
        'ReportTraining':1,
        },
    'StdOut' : {
        'Use':0,
        'ReportIncompleteInfo':0,
        'IgnoreFilter':0,
        'ReportTraining':1,
        },
    'Mail' : {
        'Use':0,
        'Host':'',
        'Port':0,
        'Id':'',
        'Password':'',
        'Address':'',
        'Tls':0,
        'Ssl':0,
        'SuplessHeaderFromText':1,
        'ReportIncompleteInfo':0,
        'IgnoreFilter':0,
        'ReportTraining':1,
        },
}

args:'argparse.Namespace' = None
config:'configparser.ConfigParser' = None
cache:'list' = None
log:'logging.Logger' = None
report:'logging.Logger' = None

def remove_expired_cache(dtcurrent:datetime):

    # 期限切れキャッシュの削除
    validperiod = config.getint('Input','CacheValidPeriodHour')
    dtexpire = dtcurrent - timedelta(hours=validperiod)
    while len(cache) > 0:
        dtcached, obj = cache[0]
        if dtcached >= dtexpire:
            break
        cache.pop(0)

def check_partial_match(conf_items, values, confcheck=False) -> bool:

    # 設定値が空欄の場合は常にTrueを報告
    if len(conf_items) == 1 and conf_items[0] == '':
        return True

    found = False
    for item in conf_items:
        item = item.strip()
        for value in values:
            if item in value:
                found = True
                break
        if confcheck:
            # 設定チェック時：見つかったら次の設定ワードを確認する
            if found:
                found = False
                continue
            else:
                return False
        else:
            # 通常時：見つかったらチェックを終了する
            if found:
                break
            else:
                continue
    if confcheck:
        # 設定チェック時：全ての設定ワードが見つかったとしてTrueを報告
        return True
    else:
        # 通常時：全ての設定ワードに一致しない場合にFalseを報告
        return found

def send_mail(subject:str, text:str, clsname:str):

    msg = MIMEText(text, 'plain', 'utf-8')
    msg['Subject'] = subject
    msg['To'] = config.get('Mail','Address')
    msg['From'] = config.get('Mail','Address')

    try:
        host = config.get('Mail','Host')
        port = config.getint('Mail','Port')
        if config.getboolean('Mail','Ssl'):
            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL(host, port, context=context)
        else:
            server = smtplib.SMTP(host, port)
            if config.getboolean('Mail','Tls'):
                server.starttls()
        server.login(config.get('Mail','Id'), config.get('Mail','Password'))
        server.send_message(msg)
        server.quit()
        log.info(f'Mail: {clsname} send success.')

    except Exception as e:
        log.exception(e)
        log.warning(f'Mail: {clsname} send failed.')

def process_mail(dt:datetime, item, filtered, training, incomplete):

    if not config.getboolean('Mail','Use'):
        return
    if incomplete and not config.getboolean('Mail','ReportIncompleteInfo'):
        return
    if training and not config.getboolean('Mail','ReportTraining'):
        return
    if filtered and not config.getboolean('Mail','IgnoreFilter'):
        return

    text = str(item)

    if isinstance(item, qzss_dc_report.QzssDcXtendedMessageBase):
        if isinstance(item, qzss_dc_report.QzssDcxJAlert):
            subject = 'J-Alert'
        elif isinstance(item, qzss_dc_report.QzssDcxLAlert):
            subject = 'L-Alert'
        elif isinstance(item, qzss_dc_report.QzssDcxMTInfo):
            subject = 'Municipality-Transmitted Information'
        elif isinstance(item, qzss_dc_report.QzssDcxOutsideJapan):
            subject = 'Information from Organizations outside Japan'
        else:
            subject = f'不明なクラス({type(item)})'
        if training:
            subject = '[訓練/試験]' + subject
        subject = '災危情報: ' + subject

    elif isinstance(item, qzss_dc_report.QzssDcReportJmaBase):
        subject = item.get_header()
        if config.getboolean('Mail','SuplessHeaderFromText'):
            # 本文に含まれるヘッダーを取り除く
            text = text.replace(subject,'',1)
    else:
        subject = f'災危情報: 不明なクラス({type(item)})'

    text += f'\n\n情報受信時刻: {dt.strftime(DATETIME_FORMAT)}\n'
    send_mail(subject, text, item.__class__.__name__)

def process_report_file(dtcurrent:datetime, item, filtered, training, incomplete):

    if incomplete and not config.getboolean('ReportFile','ReportIncompleteInfo'):
        return
    if training and not config.getboolean('ReportFile','ReportTraining'):
        return
    if filtered and not config.getboolean('ReportFile','IgnoreFilter'):
        return
    report.info(f'\n----- {dtcurrent.strftime(DATETIME_FORMAT)} --------------------')
    report.info(item)

def process_stdout(dtcurrent:datetime, item, filtered, training, incomplete):

    if not config.getboolean('StdOut','Use'):
        return
    if incomplete and not config.getboolean('StdOut','ReportIncompleteInfo'):
        return
    if training and not config.getboolean('StdOut','ReportTraining'):
        return
    if filtered and not config.getboolean('StdOut','IgnoreFilter'):
        return
    print(f'\n----- {dtcurrent.strftime(DATETIME_FORMAT)} --------------------')
    print(item)

def process_report(dtcurrent:datetime, item):

    # 訓練かどうかの確認
    training = False
    if isinstance(item, qzss_dc_report.QzssDcReportJmaBase):
        if item.report_classification_no == 7:
            training = True
    elif isinstance(item, qzss_dc_report.QzssDcXtendedMessageBase):
        if item.camf.a1 == 0:
            training = True

    # 各クラス毎の確認
    filtered = False
    incomplete = False
    if isinstance(item, qzss_dc_report.QzssDcxNullMsg):
        # Nullメッセージは常に無視
        return
    elif isinstance(item, qzss_dc_report.QzssDcxUnknown):
        # Unknownメッセージは警告を表示
        log.warning(f'QzssDcxUnknown: {type(item)}\n{item}')
        return
    elif isinstance(item, qzss_dc_report.QzssDcReportJmaAshFall):
        if not config.getboolean('QzssDcReportJmaAshFall','Use'):
            log.info('DCReport: QzssDcReportJmaAshFall Skipped. (Use=0)')
            filtered = True
        else:
            lg = config.get('QzssDcReportJmaAshFall','LocalGovernments').split(',')
            if not check_partial_match(lg, item.local_governments):
                log.info('DCReport: QzssDcReportJmaAshFall Skipped. (LocalGovernment not found)')
                filtered = True
    elif isinstance(item, qzss_dc_report.QzssDcReportJmaEarthquakeEarlyWarning):
        if not config.getboolean('QzssDcReportJmaEarthquakeEarlyWarning','Use'):
            log.info('DCReport: QzssDcReportJmaEarthquakeEarlyWarning Skipped. (Use=0)')
            filtered = True
        else:
            regions = config.get('QzssDcReportJmaEarthquakeEarlyWarning','Regions').split(',')
            if not check_partial_match(regions, item.eew_forecast_regions):
                log.info('DCReport: QzssDcReportJmaEarthquakeEarlyWarning Skipped. (Region not found)')
                filtered = True
    elif isinstance(item, qzss_dc_report.QzssDcReportJmaFlood):
        if not config.getboolean('QzssDcReportJmaFlood','Use'):
            log.info('DCReport: QzssDcReportJmaFlood Skipped. (Use=0)')
            filtered = True
        else:
            regions = config.get('QzssDcReportJmaFlood','Regions').split(',')
            if not check_partial_match(regions, item.flood_forecast_regions):
                log.info('DCReport: QzssDcReportJmaFlood Skipped. (Region not found)')
                filtered = True
    elif isinstance(item, qzss_dc_report.QzssDcReportJmaHypocenter):
        if not config.getboolean('QzssDcReportJmaHypocenter','Use'):
            log.info('DCReport: QzssDcReportJmaHypocenter Skipped. (Use=0)')
            filtered = True
    elif isinstance(item, qzss_dc_report.QzssDcReportJmaMarine):
        if not config.getboolean('QzssDcReportJmaMarine','Use'):
            log.info('DCReport: QzssDcReportJmaMarine Skipped. (Use=0)')
            filtered = True
        else:
            regions = config.get('QzssDcReportJmaMarine','Regions').split(',')
            if not check_partial_match(regions, item.marine_forecast_regions):
                log.info('DCReport: QzssDcReportJmaMarine Skipped. (Region not found)')
                filtered = True
    elif isinstance(item, qzss_dc_report.QzssDcReportJmaNankaiTroughEarthquake):
        if not config.getboolean('QzssDcReportJmaNankaiTroughEarthquake','Use'):
            log.info('DCReport: QzssDcReportJmaNankaiTroughEarthquake Skipped. (Use=0)')
            filtered = True
        if not item.completed:
            log.info('DCReport: QzssDcReportJmaNankaiTroughEarthquake Skipped. (Incomplete)')
            incomplete = True
    elif isinstance(item, qzss_dc_report.QzssDcReportJmaNorthwestPacificTsunami):
        if not config.getboolean('QzssDcReportJmaNorthwestPacificTsunami','Use'):
            log.info('DCReport: QzssDcReportJmaNorthwestPacificTsunami Skipped. (Use=0)')
            filtered = True
        else:
            regions = config.get('QzssDcReportJmaNorthwestPacificTsunami','Regions').split(',')
            if not check_partial_match(regions, item.coastal_regions_en):
                log.info('DCReport: QzssDcReportJmaNorthwestPacificTsunami Skipped. (Region not found)')
                filtered = True
    elif isinstance(item, qzss_dc_report.QzssDcReportJmaSeismicIntensity):
        if not config.getboolean('QzssDcReportJmaSeismicIntensity','Use'):
            log.info('DCReport: QzssDcReportJmaSeismicIntensity Skipped. (Use=0)')
            filtered = True
        else:
            prefectures = config.get('QzssDcReportJmaSeismicIntensity','Prefectures').split(',')
            if not check_partial_match(prefectures, item.prefectures):
                log.info('DCReport: QzssDcReportJmaSeismicIntensity Skipped. (Prefecture not found)')
                filtered = True
    elif isinstance(item, qzss_dc_report.QzssDcReportJmaTsunami):
        if not config.getboolean('QzssDcReportJmaTsunami','Use'):
            log.info('DCReport: QzssDcReportJmaTsunami Skipped. (Use=0)')
            filtered = True
        else:
            regions = config.get('QzssDcReportJmaTsunami','Regions').split(',')
            if not check_partial_match(regions, item.tsunami_forecast_regions):
                log.info('DCReport: QzssDcReportJmaTsunami Skipped. (Region not found)')
                filtered = True
    elif isinstance(item, qzss_dc_report.QzssDcReportJmaTyphoon):
        if not config.getboolean('QzssDcReportJmaTyphoon','Use'):
            log.info('DCReport: QzssDcReportJmaTyphoon Skipped. (Use=0)')
            filtered = True
    elif isinstance(item, qzss_dc_report.QzssDcReportJmaVolcano):
        if not config.getboolean('QzssDcReportJmaVolcano','Use'):
            log.info('DCReport: QzssDcReportJmaVolcano Skipped. (Use=0)')
            filtered = True
        else:
            lg = config.get('QzssDcReportJmaVolcano','LocalGovernments').split(',')
            if not check_partial_match(lg, item.local_governments):
                log.info('DCReport: QzssDcReportJmaVolcano Skipped. (LocalGovernment not found)')
                filtered = True
    elif isinstance(item, qzss_dc_report.QzssDcReportJmaWeather):
        if not config.getboolean('QzssDcReportJmaWeather','Use'):
            log.info('DCReport: QzssDcReportJmaWeather Skipped. (Use=0)')
            filtered = True
        else:
            regions = config.get('QzssDcReportJmaWeather','Regions').split(',')
            if not check_partial_match(regions, item.weather_forecast_regions):
                log.info('DCReport: QzssDcReportJmaWeather Skipped. (Region not found)')
                filtered = True
    elif isinstance(item, qzss_dc_report.QzssDcxJAlert):
        if not config.getboolean('QzssDcxJAlert','Use'):
            log.info('DCReport: QzssDcxJAlert Skipped. (Use=0)')
            filtered = True
    elif isinstance(item, qzss_dc_report.QzssDcxLAlert):
        if not config.getboolean('QzssDcxLAlert','Use'):
            log.info('DCReport: QzssDcxLAlert Skipped. (Use=0)')
            filtered = True
    elif isinstance(item, qzss_dc_report.QzssDcxMTInfo):
        if not config.getboolean('QzssDcxMTInfo','Use'):
            log.info('DCReport: QzssDcxMTInfo Skipped. (Use=0)')
            filtered = True
    elif isinstance(item, qzss_dc_report.QzssDcxOutsideJapan):
        if not config.getboolean('QzssDcxOutsideJapan','Use'):
            log.info('DCReport: QzssDcxOutsideJapan Skipped. (Use=0)')
            filtered = True
    else:
        log.warning(f'Unknown DCReport instance: {type(item)}\n{item}')
        return

    if item.timestamp is not None:
        dt = item.timestamp
    else:
        dt = dtcurrent

    # 訓練時はフィルターを無視する
    if training and config.getboolean('Input','IgnoreFilterWhenTraining'):
        filtered = False

    # レポートファイルへの出力
    process_report_file(dt, item, filtered, training, incomplete)
    # メール送信
    process_mail(dt, item, filtered, training, incomplete)
    # 標準出力
    process_stdout(dt, item, filtered, training, incomplete)

def dcr_report_handler(report, *callback_args, **callback_kwargs):

    # 受信時刻
    dtcurrent = datetime.now() 

    # キャッシュの確認と追加、レポートの処理
    found = False
    for dtcached, obj in cache:
        if obj == report:
            found = True
            break
    if not found:
        cache.append((dtcurrent, report))
        process_report(dtcurrent, report)

    # 期限切れキャッシュの削除
    remove_expired_cache(dtcurrent)

def signal_handler(signum, frame):

    log.error(f'Signal handler called with signal {signum}.')

    # キャッシュのダンプ
    if args.nodump_cache:
        log.warning('cache dump skipped.')
    else:
        log.info('dumping cache...')
        try:
            with open(args.cache_file, 'wb') as f:
                dill.dump(cache, f)
            log.info(f'cache dump completed. (count={len(cache)})')
        except Exception as e:
            log.exception(e)
            log.warning('cache dump failed.')
            try:
                os.remove(args.cache_file)
            except Exception as e:
                pass

    log.error('Terminate...')
    sys.exit(1)

def main():

    # メインループ
    while True:

        log.info('subprocess starting...')

        try:
            
            # gpspipe等のコマンドの実行
            with subprocess.Popen(
                    args=config.get('Input','CmdLine').split(' ')
                    ,stdout=subprocess.PIPE
                    ,stderr=subprocess.DEVNULL
                    ,bufsize=0
                    ,text=False ) as watchproc:

                log.info('subprocess started. Wait for receiving messages...')

                # デコード処理
                with io.BufferedReader(watchproc.stdout, buffer_size=1) as stream:
                    while True:
                        try:
                            azarashi.decode_stream(
                                stream=stream
                                ,msg_type=config.get('Input','Type')
                                ,callback=dcr_report_handler
                                ,unique=False
                                ,ignore_dcr=False
                                ,ignore_dcx=False)
                        except Exception as e:
                            # 例外を起こした場合はdecode_streamのループから抜けてコマンド実行をやり直す
                            log.exception(e)
                            log.warning('decode_stream occurred exception! decode_stream terminated.')
                            break
            
            # コマンド実行を中止する
            watchproc.terminate()

        except Exception as e:
            log.exception(e)
            log.error('subprocess occurred exception! Terminate...')
            sys.exit(3)

        # watch processが終了してしまった場合は5秒待ってから再度実行
        log.warning('subprocess terminated. Retry after 5 seconds...')
        time.sleep(5)

if __name__ == '__main__':

    # stdout/stderrを行バッファモードにする
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)
    sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', buffering=1)

    # シグナルハンドラの登録
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # コマンドパラメーターの解析
    parser = argparse.ArgumentParser()
    parser.add_argument('-c',action='store',dest='config_file',default=DEFAULT_CONFPATH)
    parser.add_argument('-s',action='store',dest='cache_file',default=DEFAULT_CACHEPATH)
    parser.add_argument('-l',action='store',dest='log_level',type=int,default=logging.INFO)
    parser.add_argument('-t',action='store_true',dest='test_only',default=False)
    parser.add_argument('-x',action='store_true',dest='noload_cache',default=False)
    parser.add_argument('-y',action='store_true',dest='nodump_cache',default=False)
    args = parser.parse_args()

    # ログの準備
    log = logging.getLogger('log')
    log_handler = logging.StreamHandler()   # sys.stderr
    log_formatter = logging.Formatter('%(levelname)s: %(message)s')
    log_handler.setFormatter(log_formatter)
    log.addHandler(log_handler)
    log.setLevel(args.log_level)

    # 設定ファイルの読み込み
    config = configparser.ConfigParser()
    config.read_dict(DEFAULT_CONFIG)
    try:
        with open(args.config_file) as cf:
            config.read_file(cf)
        log.info(f'config file is {args.config_file}')
    except Exception as e:
        log.exception(e)
        log.warning(f'config file {args.config_file} read failure. Use default values.')

    # フィルター設定確認
    fail=False
    if not check_partial_match(
            config.get('QzssDcReportJmaAshFall','LocalGovernments').split(','),
            qzss_dcr_jma_local_government.values(),             
            confcheck=True):
        log.error('conf: QzssDcReportJmaAshFall.LocalGovernments have no valid keyword.'
            + f'\n Valid Local Governments: {qzss_dcr_jma_local_government.values()}')
        fail=True
    if not check_partial_match(
            config.get('QzssDcReportJmaEarthquakeEarlyWarning','Regions').split(','),
            qzss_dcr_jma_eew_forecast_region.values(),             
            confcheck=True):
        log.error('conf: QzssDcReportJmaEarthquakeEarlyWarning.Regions have no valid keyword.'
            + f'\n Valid Regions: {qzss_dcr_jma_eew_forecast_region.values()}')
        fail=True
    if not check_partial_match(
            config.get('QzssDcReportJmaFlood','Regions').split(','),
            qzss_dcr_jma_flood_forecast_region.values(),             
            confcheck=True):
        log.error('conf: QzssDcReportJmaFlood.Regions have no valid keyword.'
            + f'\n Valid Regions: {qzss_dcr_jma_flood_forecast_region.values()}')
        fail=True
    if not check_partial_match(
            config.get('QzssDcReportJmaMarine','Regions').split(','),
            qzss_dcr_jma_marine_forecast_region.values(),             
            confcheck=True):
        log.error('conf: QzssDcReportJmaMarine.Regions have no valid keyword.'
            + f'\n Valid Regions: {qzss_dcr_jma_marine_forecast_region.values()}')
        fail=True
    if not check_partial_match(
            config.get('QzssDcReportJmaNorthwestPacificTsunami','Regions').split(','),
            qzss_dcr_jma_coastal_region_en.values(),             
            confcheck=True):
        log.error('conf: QzssDcReportJmaNorthwestPacificTsunami.regions have no valid keyword.'
            + f'\n Valid Regions: {qzss_dcr_jma_coastal_region_en.values()}')
        fail=True
    if not check_partial_match(
            config.get('QzssDcReportJmaSeismicIntensity','Prefectures').split(','),
            qzss_dcr_jma_prefecture.values(),             
            confcheck=True):
        log.error('conf: QzssDcReportJmaSeismicIntensity.Prefectures have no valid keyword.'
            + f'\n Valid Prefectures: {qzss_dcr_jma_prefecture.values()}')
        fail=True
    if not check_partial_match(
            config.get('QzssDcReportJmaTsunami','Regions').split(','),
            qzss_dcr_jma_tsunami_forecast_region.values(),             
            confcheck=True):
        log.error('conf: QzssDcReportJmaTsunami.Regions have no valid keyword.'
            + f'\n Valid Regions: {qzss_dcr_jma_tsunami_forecast_region.values()}')
        fail=True
    if not check_partial_match(
            config.get('QzssDcReportJmaVolcano','LocalGovernments').split(','),
            qzss_dcr_jma_local_government.values(),             
            confcheck=True):
        log.error('conf: QzssDcReportJmaVolcano.LocalGovernments have no valid keyword.'
            + f'\n Valid Local Governments: {qzss_dcr_jma_local_government.values()}')
        fail=True
    if not check_partial_match(
            config.get('QzssDcReportJmaWeather','Regions').split(','),
            qzss_dcr_jma_weather_forecast_region.values(),             
            confcheck=True):
        log.error('conf: QzssDcReportJmaWeather.Regions have no valid keyword.'
            + f'\n Valid Regions: {qzss_dcr_jma_weather_forecast_region.values()}')
        fail=True
    if fail:
        log.error('Terminate...')
        sys.exit(2)

    if args.test_only:
        log.error('-t option set. not execute.')
        log.error('Terminate...')
        sys.exit(4)

    # レポートファイルの準備
    report = logging.getLogger('report')
    if config.getboolean('ReportFile','Use'):
        report_file = config.get('ReportFile','Path')
        log.info(f'Report file is {report_file}')
        report_handler = handlers.TimedRotatingFileHandler(
            filename=report_file,
            when=config.get('ReportFile','When'),
            interval=config.getint('ReportFile','Interval'),
            backupCount=config.getint('ReportFile','BackupCount'),
            encoding='utf-8'
            )
        report_formatter = logging.Formatter('%(message)s')
        report_handler.setFormatter(report_formatter)
    else:
        report_handler = logging.NullHandler()
    report.addHandler(report_handler)
    report.setLevel(logging.INFO)

    # キャッシュのロード
    log.info(f'cache file is {args.cache_file}')
    if args.noload_cache:
        log.warning('cache load skipped.')
    else:
        log.info('loading cache...')
        try:
            with open(args.cache_file, 'rb') as f:
                cache = dill.load(f)
            log.info(f'cache load completed. (count={len(cache)})')
            remove_expired_cache(datetime.now())
        except FileNotFoundError as e:
            log.warning('cache file not found.')
        except Exception as e:
            log.exception(e)
            log.warning('cache load failed.')
        if cache is None:
            cache = []

    main()
