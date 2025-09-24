# dev.nix - Configuración para Project IDX
{ pkgs, ... }:

{
  # Paquetes a instalar
  packages = [
    pkgs.python3
    pkgs.python3Packages.pip
    pkgs.python3Packages.virtualenv
  ];

  # Variables de entorno
  env = {
    PYTHONPATH = ".";
  };
}