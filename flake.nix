{
  description = "Business Master autonomous economic control system dev shell";

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
            ffmpeg
            postgresql_17
            android-tools
            jq
          ];

          shellHook = ''
            export PYTHONUNBUFFERED=1
            echo "Business Master dev shell"
            echo "Run: uv sync --extra dev && uv run bm doctor"
          '';
        };
      });
    };
}
