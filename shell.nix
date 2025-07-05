{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  # Установите NIX_LD_LIBRARY_PATH, чтобы включить необходимые библиотеки
  NIX_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
    pkgs.stdenv.cc.cc
  ];

  # Укажите динамический компоновщик
  NIX_LD = pkgs.lib.fileContents "${pkgs.stdenv.cc}/nix-support/dynamic-linker";

  # Настройте shellHook для экспорта LD_LIBRARY_PATH
  shellHook = ''
    export LD_LIBRARY_PATH=$NIX_LD_LIBRARY_PATH
  '';
}
