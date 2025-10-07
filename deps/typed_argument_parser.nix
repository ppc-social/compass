{
  fetchFromGitHub,
  python313Packages,
}:

python313Packages.buildPythonPackage {
  pname = "typed-argument-parser";
  version = "1.10.1";

  # pypy doesn't seem to work properly...
  #src = python313Packages.fetchPypi {
  #  inherit pname version;
  #  hash = "sha256-CP3V73yWSArRHBLUct4hrNMjWZlvaaUlkpm1QP66RWA=";
  #};
  src = fetchFromGitHub {
    owner = "swansonk14";
    repo = "typed-argument-parser";
    rev = "v_1.10.1";
    hash = "sha256-Pv/RUsE4n7Rl1sH6le8P/LckzLeDHxGve6OPHaj+S2g=";
  };

  # do not run tests
  #doCheck = false;

  propagatedBuildInputs = [
    python313Packages.docstring-parser
    python313Packages.typing-inspect
    python313Packages.packaging
  ];

  # specific to buildPythonPackage, see its reference
  pyproject = true;
  build-system = [
    python313Packages.setuptools
    python313Packages.setuptools-scm
    python313Packages.wheel
  ];
}
