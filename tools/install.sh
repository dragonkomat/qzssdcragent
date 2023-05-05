#!/usr/bin/env bash
MYDIR=$(dirname $0)

if [ "`whoami`" != "root" ]; then
  echo "Require root privilege"
  exit 1
fi

TOOLS_DIR=${MYDIR}
SRC_DIR=${MYDIR}/../src
INSTALL_DIR=/opt/qzssdcragent
EXEC_NAME=qzssdcragent.py
SERVICE_DIR=/lib/systemd/system
SERVICE_NAME=qzssdcragent.service
CONF_DIR=/etc
CONF_NAME=qzssdcragent.conf

mkdir -p ${INSTALL_DIR}
cp ${SRC_DIR}/*.py ${INSTALL_DIR}/.
chown root:root ${INSTALL_DIR}/*.py
chmod 544 ${INSTALL_DIR}/${EXEC_NAME}

if [ ! -f ${CONF_DIR}/${CONF_NAME} ]; then
    cp ${TOOLS_DIR}/${CONF_NAME} ${CONF_DIR}/.
    chown root:root ${CONF_DIR}/${CONF_NAME}
    chmod 600 ${CONF_DIR}/${CONF_NAME}
fi

cat - > ${SERVICE_DIR}/${SERVICE_NAME} << _EOF_
[Unit]
Description=QZSS DCReport Agent
After=gpsd.service

[Service]
Type=exec
ExecStart=${INSTALL_DIR}/${EXEC_NAME} -c ${CONF_DIR}/${CONF_NAME}

[Install]
WantedBy=multi-user.target
_EOF_
chown root:root ${SERVICE_DIR}/${SERVICE_NAME}
chmod 644 ${SERVICE_DIR}/${SERVICE_NAME}

systemctl daemon-reload
systemctl enable ${SERVICE_NAME}
systemctl start ${SERVICE_NAME}

exit 0
