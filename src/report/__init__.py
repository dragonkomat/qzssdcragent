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

from .report_base import ReportBase

from .dcr_report_base import DcrReportBase
from .dcr_jma_ash_fall import DcrJmaAshFall
from .dcr_jma_earthquake_early_warning import DcrJmaEarthquakeEarlyWarning
from .dcr_jma_flood import DcrJmaFlood
from .dcr_jma_hypocenter import DcrJmaHypocenter
from .dcr_jma_marine import DcrJmaMarine
from .dcr_jma_nankai_trough_earthquake import DcrJmaNankaiTroughEarthquake
from .dcr_jma_northwest_pacific_tsunami import DcrJmaNorthwestPacificTsunami
from .dcr_jma_seismic_intensity import DcrJmaSeismicIntensity
from .dcr_jma_tsunami import DcrJmaTsunami
from .dcr_jma_typhoon import DcrJmaTyphoon
from .dcr_jma_volcano import DcrJmaVolcano
from .dcr_jma_weather import DcrJmaWeather

from .dcx_report_base import DcxReportBase
from .dcx_j_alert import DcxJAlert
from .dcx_l_alert import DcxLAlert
from .dcx_mt_info import DcxMTInfo
from .dcx_null_msg import DcxNullMsg
from .dcx_outside_japan import DcxOutsideJapan
from .dcx_unknown import DcxUnknown
