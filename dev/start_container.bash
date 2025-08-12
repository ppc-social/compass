# run mariadb if it is not already running (one may have multiple shells open)
$DOCKER_CMD create --rm -v ./gitignore/mariadb-data:/var/lib/mysql -e MARIADB_ROOT_PASSWORD=example -p 3306:3306 --name $container_id mariadb
echo "container id is: $container_id"

$DOCKER_CMD start $container_id
