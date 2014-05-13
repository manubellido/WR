#!/bin/bash

BZIP2=/bin/bzip2
PG_DUMP=/usr/bin/pg_dump

HOST="localhost"
USER="worldrat"
PASS="worldrat"
DBNAME="worldrat"

PREFIX="worldrat"
SUFFIX=$(date "+%Y%m%d-%H%M")
EXTENSION=".sql.bzip2"

DIR=/var/backups/worldrat/postgresql
LOGDIR=/var/backups/worldrat/logs
LOGFILE="$DBNAME.log"
LOGPATH=$LOGDIR/$LOGFILE

TS=$(date)

echo -n "[$TS] Generating backup as of $SUFFIX... " >> $LOGPATH

$PG_DUMP -h $HOST -U $USER -w $DBNAME | $BZIP2 > $DIR/$PREFIX-$SUFFIX$EXTENSION

echo "[done]" >> $LOGPATH
