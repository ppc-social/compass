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

  # prepare for docker use
  if command -V podman
  then
    DOCKER_CMD=podman
  elif command -V docker
  then
    DOCKER_CMD=docker
  else
    echo You need docker or podman installed on your system for this devshell to work
    exit 1
  fi
  export DOCKER_CMD
  export container_id=compass_app_dev_mariadb

  # load dev environment
  if test -f .env.development
  then
    echo
  else
    echo you need to create an .env.development file, containing your secrets/configs like seen in the .env.example file
    exit 1
  fi
  export $(cat .env.development | xargs)
  
  alias mariadb="podman exec -it compass_app_dev_mariadb mariadb -u root -pexample"
  alias run="poetry run python ./src/compass_app.py"
  alias python="poetry run python"

  # launch db in shell if it isn't disabled (you may want to manage it manually if you use multiple shells)
  if [ $DISABLE_DB_IN_SHELL != "true" ]; 
  then 
    bash ./dev/start_container.bash
    # auto-stop when exiting
    trap "bash ./dev/stop_container.bash" EXIT
  fi
 '';
}
