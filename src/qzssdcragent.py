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
import json
import re
import signal
import smtplib
import ssl
import subprocess
import sys
import os
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
import logging
from logging import handlers
#import pdb

import azarashi
from azarashi.qzss_dcr_lib.definition import *
from azarashi.qzss_dcr_lib.report import qzss_dc_report

NAME = 'qzssdcragent'

RE_GPSMON_PACKET = re.compile(r'^\(([0-9]+)\) ([0-9a-f]+)$')
RE_GPSMON_JSON = re.compile(r'^\(([0-9]+)\) ({.*})$')
RE_UBLOXHEX_SFRBX_QZSS = re.compile(r'^b5620213(..)0005(..)')

DATETIME_FORMAT = '%Y/%m/%d %H:%M:%S'

DEFAULT_CONFPATH = f'/etc/{NAME}.conf'
DEFAULT_REPORTPATH = f'/var/log/{NAME}.log'

DEFAULT_CONFIG = {
    'QzssDcReportJmaEarthquakeEarlyWarning' : {
        'Use':1,
        'Regions':'',
        },
    'QzssDcReportJmaHypocenter' : {
        'Use':1,
        },
    'QzssDcReportJmaSeismicIntensity' : {
        'Use':1,
        'Prefectures':'',
        },
    'QzssDcReportJmaNankaiTroughEarthquake' : {
        'Use':1,
        'ReportIncompleteInfo':0,
        },
    'QzssDcReportJmaTsunami' : {
        'Use':1,
        'Regions':'',
        },
    'QzssDcReportJmaNorthwestPacificTsunami' : {
        'Use':1,
        'Regions':'',
        },
    'QzssDcReportJmaVolcano' : {
        'Use':1,
        'LocalGovernments':'',
        },
    'QzssDcReportJmaAshFall' : {
        'Use':1,
        'LocalGovernments':'',
        },
    'QzssDcReportJmaWeather' : {
        'Use':1,
        'Regions':'',
        },
    'QzssDcReportJmaFlood' : {
        'Use':1,
        'Regions':'',
        },
    'QzssDcReportJmaTyphoon' : {
        'Use':1,
        },
    'QzssDcReportJmaMarine' : {
        'Use':1,
        'Regions':'',
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
        },
    'Cache' : {
        'ValidPeriodHour':24,
        },
    'General' : {
        'FilterTraining':0,
        'ReportAllInfo':1,
        'ReportRawPacket':0,
        },
}

args:'argparse.Namespace' = None
config:'configparser.ConfigParser' = None
cache = []
log:'logging.Logger' = None
report:'logging.Logger' = None

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

def process_mail(dt:datetime, item):

    if not config.getboolean('Mail','Use'):
        log.info(f'Mail: {item.__class__.__name__} skipped. (Use=0):')
        return

    subject = item.get_header()
    text = str(item)
    if config.getboolean('Mail','SuplessHeaderFromText'):
        # 本文に含まれるヘッダーを取り除く
        text = text.replace(subject,'',1)
    text += f'\n\n情報受信時刻: {dt.strftime(DATETIME_FORMAT)}\n'
    send_mail(subject, text, item.__class__.__name__)

def process_report(dtcurrent:datetime, item):

    filtered = False
    if config.getboolean('General','FilterTraining') and item.report_classification_no == 7:
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
    elif isinstance(item, qzss_dc_report.QzssDcReportJmaHypocenter):
        if not config.getboolean('QzssDcReportJmaHypocenter','Use'):
            log.info('DCReport: QzssDcReportJmaHypocenter Skipped. (Use=0)')
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
    elif isinstance(item, qzss_dc_report.QzssDcReportJmaNankaiTroughEarthquake):
        if not config.getboolean('QzssDcReportJmaNankaiTroughEarthquake','Use'):
            log.info('DCReport: QzssDcReportJmaNankaiTroughEarthquake Skipped. (Use=0)')
            filtered = True
        elif not config.getboolean('QzssDcReportJmaNankaiTroughEarthquake','ReportIncompleteInfo') and not item.completed:
            log.info('DCReport: QzssDcReportJmaNankaiTroughEarthquake Skipped. (Incomplete)')
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
    elif isinstance(item, qzss_dc_report.QzssDcReportJmaNorthwestPacificTsunami):
        if not config.getboolean('QzssDcReportJmaNorthwestPacificTsunami','Use'):
            log.info('DCReport: QzssDcReportJmaNorthwestPacificTsunami Skipped. (Use=0)')
            filtered = True
        else:
            regions = config.get('QzssDcReportJmaNorthwestPacificTsunami','Regions').split(',')
            if not check_partial_match(regions, item.coastal_regions_en):
                log.info('DCReport: QzssDcReportJmaNorthwestPacificTsunami Skipped. (Region not found)')
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
    elif isinstance(item, qzss_dc_report.QzssDcReportJmaAshFall):
        if not config.getboolean('QzssDcReportJmaAshFall','Use'):
            log.info('DCReport: QzssDcReportJmaAshFall Skipped. (Use=0)')
            return
        else:
            lg = config.get('QzssDcReportJmaAshFall','LocalGovernments').split(',')
            if not check_partial_match(lg, item.local_governments):
                log.info('DCReport: QzssDcReportJmaAshFall Skipped. (LocalGovernment not found)')
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
    elif isinstance(item, qzss_dc_report.QzssDcReportJmaFlood):
        if not config.getboolean('QzssDcReportJmaFlood','Use'):
            log.info('DCReport: QzssDcReportJmaFlood Skipped. (Use=0)')
            filtered = True
        else:
            regions = config.get('QzssDcReportJmaFlood','Regions').split(',')
            if not check_partial_match(regions, item.flood_forecast_regions):
                log.info('DCReport: QzssDcReportJmaFlood Skipped. (Region not found)')
                filtered = True
    elif isinstance(item, qzss_dc_report.QzssDcReportJmaTyphoon):
        if not config.getboolean('QzssDcReportJmaTyphoon','Use'):
            log.info('DCReport: QzssDcReportJmaTyphoon Skipped. (Use=0)')
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
    else:
        log.warning(f'Unknown DCReport instance: {type(item)}')

    if item.timestamp is not None:
        dt = item.timestamp
    else:
        dt = dtcurrent

    # レポートファイルへの出力
    if (not filtered) or config.getboolean('General','ReportAllInfo'):
        report.info(item)

    # メール送信
    if not filtered:
        process_mail(dt, item)

def process_packet_json(packet:str):

    try:
        log.info(f'gpsmon info: {json.loads(packet)}')
        # TODO: gpsdのドライバの確認
    except:
        log.info(f'gpsmon info(raw): {packet}')
    pass

def process_packet_raw(packet:str):

    # 受信時刻
    dtcurrent = datetime.now()

    # TODO: u-blox以外のドライバへの対応
    # QZSSのSFRBXかどうかの確認
    r = re.match(RE_UBLOXHEX_SFRBX_QZSS, packet)
    if r is None:
        return

    # RAWパケットをレポートする
    if config.getboolean('General','ReportRawPacket'):
        report.info(f'Raw packet: {packet}')

    # デコード
    binpacket = bytes.fromhex(packet)
    try:
        item = azarashi.decode(binpacket, msg_type='ublox')
    except:
        return

    # キャッシュの確認と追加、レポートの処理
    found = False
    for dtcached, obj in cache:
        if obj == item:
            found = True
            break
    if not found:
        cache.append((dtcurrent, item))
        process_report(dtcurrent, item)

    # 期限切れキャッシュの削除
    validperiod = config.getint('Cache','ValidPeriodHour')
    dtexpire = dtcurrent - timedelta(hours=validperiod)
    while len(cache) > 0:
        dtcached, obj = cache[0]
        if dtcached >= dtexpire:
            break
        cache.pop(0)

def signal_handler(signum, frame):

    log.error(f'Signal handler called with signal {signum}.')
    log.error('Terminate...')
    sys.exit(1)

def main():

    # メインループ
    while True:

        log.info('gpsmon process starting...')

        try:
            
            # gpsmonコマンドの実行
            with subprocess.Popen(
                    ['stdbuf','-oL','gpsmon','-a']
                    ,stdout=subprocess.PIPE
                    ,stderr=subprocess.DEVNULL
                    ,bufsize=0
                    ,text=True ) as gpsmon:

                log.info('gpsmon process started. Wait for receiving messages...')

                # gpsmonの出力を読み込む
                for line in gpsmon.stdout:

                    # 通常パケットの処理
                    r = re.match(RE_GPSMON_PACKET, line)
                    if r is not None:
                        packet = r.group(2)
                        process_packet_raw(packet)
                        continue

                    # JSONパケットの処理
                    r = re.match(RE_GPSMON_JSON, line)
                    if r is not None:
                        packet = r.group(2)
                        process_packet_json(packet)
                        continue

        except Exception as e:
            log.exception(e)
            log.error('gpsmon process occurred exception! Terminate...')
            sys.exit(3)

        # gpsmonが終了してしまった場合は5秒待ってから再度実行
        log.warning('gpsmon process terminated. Retry after 5 seconds...')
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
    parser.add_argument('-r',action='store',dest='report_file',default=DEFAULT_REPORTPATH)
    parser.add_argument('-l',action='store',dest='log_level',default=logging.INFO)
    parser.add_argument('-n',action='store_true',dest='no_report',default=False)
    args = parser.parse_args()

    # ログの準備
    log = logging.getLogger('log')
    log_handler = logging.StreamHandler()   # sys.stderr
    log_formatter = logging.Formatter('%(levelname)s: %(message)s')
    log_handler.setFormatter(log_formatter)
    log.addHandler(log_handler)
    log.setLevel(args.log_level)

    # レポートファイルの準備
    report = logging.getLogger('report')
    if args.no_report:
        report_handler = logging.NullHandler()
    else:
        report_handler = handlers.TimedRotatingFileHandler(
            filename=args.report_file,
            when='D',
            interval=7,
            backupCount=5,
            encoding='utf-8'
            )        
        report_formatter = logging.Formatter('%(asctime)s %(message)s')
        report_handler.setFormatter(report_formatter)
    report.addHandler(report_handler)
    report.setLevel(logging.INFO)

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
            config.get('QzssDcReportJmaEarthquakeEarlyWarning','Regions').split(','),
            qzss_dcr_jma_eew_forecast_region.values(),             
            confcheck=True):
        log.error('conf: QzssDcReportJmaEarthquakeEarlyWarning.Regions have no valid keyword.'
            + f'\n Valid Regions: {qzss_dcr_jma_eew_forecast_region.values()}')
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
            config.get('QzssDcReportJmaNorthwestPacificTsunami','Regions').split(','),
            qzss_dcr_jma_coastal_region_en.values(),             
            confcheck=True):
        log.error('conf: QzssDcReportJmaNorthwestPacificTsunami.regions have no valid keyword.'
            + f'\n Valid Regions: {qzss_dcr_jma_coastal_region_en.values()}')
        fail=True
    if not check_partial_match(
            config.get('QzssDcReportJmaVolcano','LocalGovernments').split(','),
            qzss_dcr_jma_local_government.values(),             
            confcheck=True):
        log.error('conf: QzssDcReportJmaVolcano.LocalGovernments have no valid keyword.'
            + f'\n Valid Local Governments: {qzss_dcr_jma_local_government.values()}')
        fail=True
    if not check_partial_match(
            config.get('QzssDcReportJmaAshFall','LocalGovernments').split(','),
            qzss_dcr_jma_local_government.values(),             
            confcheck=True):
        log.error('conf: QzssDcReportJmaAshFall.LocalGovernments have no valid keyword.'
            + f'\n Valid Local Governments: {qzss_dcr_jma_local_government.values()}')
        fail=True
    if not check_partial_match(
            config.get('QzssDcReportJmaWeather','Regions').split(','),
            qzss_dcr_jma_weather_forecast_region.values(),             
            confcheck=True):
        log.error('conf: QzssDcReportJmaWeather.Regions have no valid keyword.'
            + f'\n Valid Regions: {qzss_dcr_jma_weather_forecast_region.values()}')
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
    if fail:
        log.error('Terminate...')
        sys.exit(2)

    main()
