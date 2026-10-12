{
  description = "Business Master standalone economic core dev shell";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" ];
      forAllSystems = f: nixpkgs.lib.genAttrs systems (system: f (import nixpkgs { inherit system; }));
    in {
      devShells = forAllSystems (pkgs: {
        default = pkgs.mkShell {
          packages = with pkgs; [
            python313
            uv
            git
            postgresql_17
            jq
          ];

          shellHook = ''
            export PYTHONUNBUFFERED=1
            echo "Business Master dev shell"
            echo "Run: uv sync && uv run bm doctor"
          '';
        };
      });
    };
}
