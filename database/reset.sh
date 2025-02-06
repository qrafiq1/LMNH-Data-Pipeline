echo "Reseting rds database..."
psql -h c14-qasim-museum-db.c57vkec7dkkx.eu-west-2.rds.amazonaws.com -p 5432 -U postgres -d museum -f schema.sql
echo "Database has been reset!"