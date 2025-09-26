# dev.nix - Configuración para Project IDX
{ pkgs, ... }:

{
  # Paquetes a instalar
  packages = [
    pkgs.python3
    pkgs.python3Packages.pip
    pkgs.python3Packages.virtualenv
    pkgs.python3Packages.pymongo
    pkgs.python3Packages.flask
    pkgs.python3Packages.python-dotenv
  ];

  # Variables de entorno
  env = {
    PYTHONPATH = ".";
  };
}