{
  python313Packages,
  el_std_py,
  typed-argument-parser,
  lib
}:

python313Packages.buildPythonApplication 
{
  pname = "compass-app";
  version = "0.1.0";
  src = ./.;

  propagatedBuildInputs = with python313Packages; [
    
    discordpy
    pydantic
    fastapi
    mariadb
    sqlalchemy
    sqlmodel
    httpx
    asyncmy
    uvicorn
    python-dotenv

    # packages not in nixpkgs
    el_std_py
    typed-argument-parser
  ];

  pyproject = true;
  build-system = [
    python313Packages.setuptools
    python313Packages.setuptools-scm
    python313Packages.wheel
  ];

  meta = with lib; {
    description = "Discord bot + web app for https://thecompass.diy";
    homepage = "https://github.com/ppc-social/compass";
    platforms = platforms.unix;
    mainProgram = "compass_app";
  };
}
