{
  description = "Discord bot + web app for https://thecompass.diy";

  inputs = {
    nixpkgs.url = "nixpkgs/nixos-25.05";
    flake-utils.url = "github:numtide/flake-utils";

    el_std_py = {
      url = "github:melektron/el_std_py";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.flake-utils.follows = "flake-utils";
    };
  };

  outputs = { self, nixpkgs, flake-utils, ... }@inputs:
    flake-utils.lib.eachDefaultSystem (system: 
      let
        pkgs = import nixpkgs { inherit system; };
      in
      {
        packages.default = pkgs.callPackage ./default.nix {
          el_std_py = inputs.el_std_py.packages."${system}".default;
          typed-argument-parser = self.packages."${system}".python313Packages.typed-argument-parser;
        };
        packages.python313Packages = {
          typed-argument-parser = pkgs.callPackage ./deps/typed_argument_parser.nix {};
        };

        devShells.default = pkgs.mkShell {
          propagatedBuildInputs = [
            pkgs.python313

            pkgs.python313Packages.discordpy
            pkgs.python313Packages.pydantic
            pkgs.python313Packages.fastapi
            pkgs.python313Packages.mariadb
            pkgs.python313Packages.sqlalchemy
            pkgs.python313Packages.sqlmodel
            pkgs.python313Packages.httpx
            pkgs.python313Packages.asyncmy
            pkgs.python313Packages.uvicorn
            pkgs.python313Packages.python-dotenv

            # packages not in nixpkgs
            inputs.el_std_py.packages."${system}".default
            self.packages."${system}".python313Packages.typed-argument-parser
          ];

          shellHook = ''
            if [ ! -d .venv ]; then
              python -m venv .venv
              source .venv/bin/activate
              pip install -e .
            else
              source .venv/bin/activate
            fi
          '';
        };

      }
    );
}