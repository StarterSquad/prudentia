#!/bin/bash

LAST_SQL_PROCESSED="last_sql_processed"
if [ -f ${LAST_SQL_PROCESSED} ]
then
    LAST_SQL=$(cat ${LAST_SQL_PROCESSED})
else
    LAST_SQL=-1
fi

SQL_FILES=$(ls *.sql | sort -n -t . -k 1)
# TODO sql files name must follow the syntax  <number>.<name_with_underscore>.sql

for file in ${SQL_FILES}
do
    INDEX=${file%.*.sql}
    if [ ${INDEX} -gt ${LAST_SQL} ]
    then
        echo "Executing:" ${file}

        mysql --user=$1 --password=$2 --host=$3 < ./${file}

        RET=$?
        if [[ ${RET} != 0 ]]
        then
            exit ${RET}
        fi
    else
        echo "Skipping:" ${file}
    fi
done

echo "Index of last sql processed:" ${INDEX}
echo ${INDEX} > ${LAST_SQL_PROCESSED}