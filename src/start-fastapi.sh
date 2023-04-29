#!/bin/sh

wait_database()
{
  HOST=$1
  PORT=$2
  TYPE=$3

  echo "Waiting for $TYPE..."

  while ! nc -z $HOST $PORT; do
    sleep 0.1
  done

  echo "$TYPE started"
}

if [ ${CACHE_DB_TYPE} = "postgres" ]
  then
    wait_database $PG_HOST $PG_PORT $DB_TYPE
fi

gunicorn main:app --workers 4\
 --worker-class uvicorn.workers.UvicornWorker\
  --bind 0.0.0.0:8101\
   --log-level "$LOGGING_LEVEL"

exec "$@"