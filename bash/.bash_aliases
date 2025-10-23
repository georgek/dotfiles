# -*- mode: sh; -*-

mkcd () {
  mkdir -p "$1"
  cd "$1"
}

tempcd () {
  cd "$(mktemp -d)"
  chmod -R 0700 .
  if [[ $# -eq 1 ]]; then
    mkdir -p "$1"
    cd "$1"
    chmod -R 0700 .
  fi
}
