source .env

psql -h $HOST -p $PORT -U $USERNAME -d $DATABASE_NAME -f schema.sql