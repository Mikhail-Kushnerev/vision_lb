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

if [ ${DB_TYPE} = "postgres" ]
  then
    wait_database $DB_HOST $DB_PORT $DB_TYPE
fi

alembic upgrade head

gunicorn main:app --workers 4\
 --worker-class uvicorn.workers.UvicornWorker\
  --bind 0.0.0.0:8100

exec "$@"





