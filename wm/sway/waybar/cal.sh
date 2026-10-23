#!/bin/sh
# Runtime deps: foot, bash, cal
exec foot -a cal-popup bash -c 'cal; read -rsn1'
