#!/usr/bin/env bash
MYDIR=$(dirname $0)

if [ "`whoami`" != "root" ]; then
  echo "Require root privilege"
  exit 1
fi

INSTALL_DIR=/opt/qzssdcragent
SERVICE_DIR=/lib/systemd/system
SERVICE_NAME=qzssdcragent.service

systemctl stop ${SERVICE_NAME}
systemctl disable ${SERVICE_NAME}
rm -f ${SERVICE_DIR}/${SERVICE_NAME}
systemctl daemon-reload

rm -rf ${INSTALL_DIR}

exit 0
