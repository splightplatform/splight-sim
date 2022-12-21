#!/bin/sh

pip install /opt/c37118/python/*
ln -s /opt/c37118/randomPMU.py /usr/bin/c37118
rm -fr /opt/c37118/python /opt/c37118/requirements.txt /opt/c37118/install.sh
