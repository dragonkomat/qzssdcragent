#!/usr/bin/env bash

# QzssDcReportJmaEarthquakeEarlyWarning
# QzssDcReportJmaHypocenter
# QzssDcReportJmaSeismicIntensity
# QzssDcReportJmaNankaiTroughEarthquake
# QzssDcReportJmaTsunami
# QzssDcReportJmaNorthwestPacificTsunami
# QzssDcReportJmaVolcano
# QzssDcReportJmaAshFall
# QzssDcReportJmaWeather
# QzssDcReportJmaFlood
# QzssDcReportJmaMarine
# QzssDcReportJmaTyphoon
# QzssDcxNullMsg
# QzssDcxOutsideJapan
# QzssDcxLAlert
# QzssDcxJAlert
# QzssDcxMTInfo
# QzssDcxUnknown

cp _dcr.py dcr_jma_earthquake_early_warning.py
cp _dcr.py dcr_jma_hypocenter.py
cp _dcr.py dcr_jma_seismic_intensity.py
cp _dcr.py dcr_jma_nankai_trough_earthquake.py
cp _dcr.py dcr_jma_tsunami.py
cp _dcr.py dcr_jma_northwest_pacific_tsunami.py
cp _dcr.py dcr_jma_volcano.py
cp _dcr.py dcr_jma_ash_fall.py
cp _dcr.py dcr_jma_weather.py
cp _dcr.py dcr_jma_flood.py
cp _dcr.py dcr_jma_marine.py
cp _dcr.py dcr_jma_typhoon.py

cp _dcx.py dcx_null_msg.py
cp _dcx.py dcx_outside_japan.py
cp _dcx.py dcx_l_alert.py
cp _dcx.py dcx_j_alert.py
cp _dcx.py dcx_mt_info.py
cp _dcx.py dcx_unknown.py

sed -i -e 's/QzssDcrXXXXX/QzssDcReportJmaEarthquakeEarlyWarning/' dcr_jma_earthquake_early_warning.py 
sed -i -e 's/QzssDcrXXXXX/QzssDcReportJmaHypocenter/' dcr_jma_hypocenter.py 
sed -i -e 's/QzssDcrXXXXX/QzssDcReportJmaSeismicIntensity/' dcr_jma_seismic_intensity.py
sed -i -e 's/QzssDcrXXXXX/QzssDcReportJmaNankaiTroughEarthquake/' dcr_jma_nankai_trough_earthquake.py
sed -i -e 's/QzssDcrXXXXX/QzssDcReportJmaTsunami/' dcr_jma_tsunami.py
sed -i -e 's/QzssDcrXXXXX/QzssDcReportJmaNorthwestPacificTsunami/' dcr_jma_northwest_pacific_tsunami.py
sed -i -e 's/QzssDcrXXXXX/QzssDcReportJmaVolcano/' dcr_jma_volcano.py
sed -i -e 's/QzssDcrXXXXX/QzssDcReportJmaAshFall/' dcr_jma_ash_fall.py
sed -i -e 's/QzssDcrXXXXX/QzssDcReportJmaWeather/' dcr_jma_weather.py
sed -i -e 's/QzssDcrXXXXX/QzssDcReportJmaFlood/' dcr_jma_flood.py
sed -i -e 's/QzssDcrXXXXX/QzssDcReportJmaMarine/' dcr_jma_marine.py
sed -i -e 's/QzssDcrXXXXX/QzssDcReportJmaTyphoon/' dcr_jma_typhoon.py

sed -i -e 's/QzssDcxXXXXX/QzssDcxNullMsg/' dcx_null_msg.py
sed -i -e 's/QzssDcxXXXXX/QzssDcxOutsideJapan/' dcx_outside_japan.py
sed -i -e 's/QzssDcxXXXXX/QzssDcxLAlert/' dcx_l_alert.py
sed -i -e 's/QzssDcxXXXXX/QzssDcxJAlert/' dcx_j_alert.py
sed -i -e 's/QzssDcxXXXXX/QzssDcxMTInfo/' dcx_mt_info.py
sed -i -e 's/QzssDcxXXXXX/QzssDcxUnknown/' dcx_unknown.py

sed -i -e 's/DcrYYYYY/DcrJmaEarthquakeEarlyWarning/' dcr_jma_earthquake_early_warning.py 
sed -i -e 's/DcrYYYYY/DcrJmaHypocenter/' dcr_jma_hypocenter.py 
sed -i -e 's/DcrYYYYY/DcrJmaSeismicIntensity/' dcr_jma_seismic_intensity.py
sed -i -e 's/DcrYYYYY/DcrJmaNankaiTroughEarthquake/' dcr_jma_nankai_trough_earthquake.py
sed -i -e 's/DcrYYYYY/DcrJmaTsunami/' dcr_jma_tsunami.py
sed -i -e 's/DcrYYYYY/DcrJmaNorthwestPacificTsunami/' dcr_jma_northwest_pacific_tsunami.py
sed -i -e 's/DcrYYYYY/DcrJmaVolcano/' dcr_jma_volcano.py
sed -i -e 's/DcrYYYYY/DcrJmaAshFall/' dcr_jma_ash_fall.py
sed -i -e 's/DcrYYYYY/DcrJmaWeather/' dcr_jma_weather.py
sed -i -e 's/DcrYYYYY/DcrJmaFlood/' dcr_jma_flood.py
sed -i -e 's/DcrYYYYY/DcrJmaMarine/' dcr_jma_marine.py
sed -i -e 's/DcrYYYYY/DcrJmaTyphoon/' dcr_jma_typhoon.py

sed -i -e 's/DcxYYYYY/DcxNullMsg/' dcx_null_msg.py
sed -i -e 's/DcxYYYYY/DcxOutsideJapan/' dcx_outside_japan.py
sed -i -e 's/DcxYYYYY/DcxLAlert/' dcx_l_alert.py
sed -i -e 's/DcxYYYYY/DcxJAlert/' dcx_j_alert.py
sed -i -e 's/DcxYYYYY/DcxMTInfo/' dcx_mt_info.py
sed -i -e 's/DcxYYYYY/DcxUnknown/' dcx_unknown.py
