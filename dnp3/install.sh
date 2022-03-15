#!/bin/sh

pip install /opt/dnp3/python/*
pip install /opt/dnp3/python_custom/*
mv /opt/dnp3/bin/* /usr/bin/
rm -fr /opt/dnp3
