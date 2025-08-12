{ pkgs ? import <nixpkgs> {}
, ...
}: pkgs.mkShell {
 buildInputs = with pkgs; [
 	poetry
  libmysqlclient.dev
 ];

 LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
  pkgs.libgcc.lib
 ];

 shellHook = ''
  mkdir -p ./gitignore/mariadb-data

  if command -V podman
  then
    DOCKER_CMD=podman
  elif command -V docker
  then
    DOCKER_CMD=podman
  else
    echo You need docker or podman installed on your system for this devshell to work
    exit 1
  fi

  if test -f .env.development
  then
    echo
  else
    echo you need to create an .env.development file, containing your secrets/configs like seen in the .env.example file
    exit 1
  fi

  export $(cat .env.development | xargs)
  
  # run mariadb
  container_id=compass_app_dev_mariadb
  $DOCKER_CMD create --rm -v ./gitignore/mariadb-data:/var/lib/mysql -e MARIADB_ROOT_PASSWORD=example -p 3306:3306 --name $container_id mariadb
  echo "container id is: $container_id"

  $DOCKER_CMD start $container_id

  trap "$DOCKER_CMD stop $container_id" EXIT

  alias mariadb="podman exec -it compass_app_dev_mariadb mariadb -u root -pexample"

  alias run="poetry run python ./src/compass_app.py"

  alias python="poetry run python"


 '';
}
