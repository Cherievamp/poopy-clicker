{
  description = "Poopy Clicker — jogo de cliques com goobers";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        python = pkgs.python3.withPackages (ps: [ ps.pyqt6 ]);
      in {
        packages.default = pkgs.stdenv.mkDerivation {
          name = "poopy-clicker";
          src = self;
          buildInputs = [ python pkgs.makeWrapper pkgs.qt6.qtmultimedia ];
          installPhase = ''
            mkdir -p $out/{bin,lib/poopy-clicker,share/applications,share/icons/hicolor/128x128/apps}
            cp -R . $out/lib/poopy-clicker/
            makeWrapper ${python}/bin/python $out/bin/poopy-clicker \
              --add-flags "-m poopy_clicker" \
              --prefix LD_LIBRARY_PATH : ${pkgs.lib.makeLibraryPath [ pkgs.qt6.qtmultimedia ]}
            install -Dm644 $out/lib/poopy-clicker/poopy-clicker.desktop $out/share/applications/
            cp $out/lib/poopy-clicker/poopy_clicker/assets/Algo.png \
              $out/share/icons/hicolor/128x128/apps/poopy-clicker.png
          '';
        };

        devShells.default = pkgs.mkShell {
          packages = [ python pkgs.qt6.qtmultimedia ];
        };
      });
}
