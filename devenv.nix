{ pkgs, lib, config, inputs, ... }:

{
  # https://devenv.sh/packages/
  packages = [ pkgs.git ];

  languages.java.enable = true;
  languages.java.jdk.package = pkgs.jdk8;
  languages.java.maven.enable = true;

  languages.python.enable=true;
  languages.python.package=pkgs.python311;
  languages.python.uv.enable=true;
  languages.python.venv.enable=true;
  languages.python.venv.requirements=''
    black
    pyhocon
    ortools
  '';

  # https://devenv.sh/tests/
  enterTest = ''
    echo "Running tests"
    git --version | grep --color=auto "${pkgs.git.version}"
  '';

  # https://devenv.sh/pre-commit-hooks/
  pre-commit.hooks.shellcheck.enable = true;

  # See full reference at https://devenv.sh/reference/options/
}
