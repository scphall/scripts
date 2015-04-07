#!/bin/bash

mycd () {
  local input=$1
  local newdir
  local -i count
  case "$input" in
    "?")
      dirs -v
      return 0
      ;;
    ...*)
      newdir="/.."
      for (( count=1; count < ${#input}; count++ )) do
        newdir=$newdir"/.."
      done
      newdir=${newdir:1}
      ;;
    -*)
      local index=${input:1}
      [[ -z $index ]] && index=1
      [[ "$index" == "-" ]] && index=2
      newdir=$(dirs +$index)
      [[ -z $newdir ]] && return 1
      ;;
    "")
      newdir=$HOME
      ;;
    *)
      newdir=$input
  esac
  [[ ${newdir:0:1} == '~' ]] && newdir="$HOME${newdir:1}"

  # Change directory magic line
  pushd $newdir > /dev/null
  [[ $? -ne 0 ]] && return 1

  #remove any other occurence of the dir, skipping the top of the stack
  for count in {1..10}; do
    ndir=$(dirs +${count} 2>/dev/null)
    [[ $? -ne 0 ]] && return 0
    [[ ${ndir:0:1} == '~' ]] && ndir="$HOME${ndir:1}"
    if [[ $ndir == $PWD ]]; then
      popd -n +$((count--)) 2>&1 > /dev/null
    fi
  done

  #trim extras from the dir list
  popd -n +10 2>&1 > /dev/null

  return 0
}

cl () {
  mycd $1
  ls -G
}

alias cd=mycd

