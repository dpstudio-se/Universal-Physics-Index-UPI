#!/bin/sh
# Trusted Linux broker primitives. Source only from a root-owned protected deployment.
# CIP_ROOT is a dedicated root-owned installation, never a candidate-supplied path.
set -eu

cip_guard() {
    [ "$(id -u)" = 0 ] || return 1
    [ -n "${CIP_ROOT:-}" ] && [ ! -L "$CIP_ROOT" ] || return 1
    [ "$(stat -c '%u:%a' "$CIP_ROOT")" = '0:755' ] || return 1
    for directory in trusted trusted/history trusted/promotion chambers chambers/a chambers/b; do
        [ ! -L "$CIP_ROOT/$directory" ] || return 1
        [ "$(stat -c '%u:%a' "$CIP_ROOT/$directory")" = '0:755' ] || return 1
    done
    [ "$(sha256sum "$CIP_ROOT/trusted/rules" | cut -d ' ' -f 1)" = \
      "$(cat "$CIP_ROOT/trusted/trust")" ] || return 1
    for file in manifest trust rules checkpoint.sha256 history/accepted promotion/state; do
        [ -f "$CIP_ROOT/trusted/$file" ] && [ ! -L "$CIP_ROOT/trusted/$file" ] || return 1
        [ "$(stat -c '%u:%a' "$CIP_ROOT/trusted/$file")" = '0:444' ] || return 1
    done
    [ ! -L "$CIP_ROOT/chambers/a/candidate" ] || return 1
    [ "$(stat -c '%u:%a' "$CIP_ROOT/chambers/a/candidate")" = '41001:644' ] || return 1
    [ "$(stat -c '%h' "$CIP_ROOT/chambers/a/candidate")" = 1 ] || return 1
    [ ! -L "$CIP_ROOT/chambers/b/candidate" ] || return 1
    [ "$(stat -c '%u:%a' "$CIP_ROOT/chambers/b/candidate")" = '41002:644' ] || return 1
    [ "$(stat -c '%h' "$CIP_ROOT/chambers/b/candidate")" = 1 ] || return 1
}

cip_writer() {
    cip_guard || return 1
    # Only this broker may launch these reserved UIDs. Recovery checks quiescence.
    setpriv --reuid 41001 --regid 41001 --clear-groups \
        --no-new-privs --bounding-set=-all --inh-caps=-all --ambient-caps=-all \
        --landlock-access fs \
        --landlock-rule path-beneath:read-file,read-dir,execute:/ \
        --landlock-rule "path-beneath:write-file,truncate:$CIP_ROOT/chambers/a/candidate" \
        -- "$@" 9>&-
}

cip_verifier() {
    cip_guard || return 1
    setpriv --reuid 41003 --regid 41003 --clear-groups \
        --no-new-privs --bounding-set=-all --inh-caps=-all --ambient-caps=-all \
        --landlock-access fs \
        --landlock-rule path-beneath:read-file,read-dir,execute:/ \
        -- "$@" 9>&-
}

cip_recover() {
    cip_guard || return 1
    # No writer may keep an old inode open or race the recovered state. The trusted
    # launcher must serialize launch/recovery with the same exclusive lock.
    for process in /proc/[0-9]*/status; do
        if awk '$1 == "Uid:" && ($2 == 41001 || $3 == 41001) { found=1 } END { exit !found }' \
            "$process" 2>/dev/null; then return 1; fi
    done
    expected=$(cat "$CIP_ROOT/trusted/checkpoint.sha256")
    actual=$(sha256sum "$CIP_ROOT/trusted/history/accepted" | cut -d ' ' -f 1)
    [ "$expected" = "$actual" ] || return 1
    # The directory is root-owned; the writer can edit only the candidate inode.
    # Stage on the same filesystem. Any failure before rename leaves candidate intact.
    staged=$(mktemp "$CIP_ROOT/chambers/a/.restore.XXXXXX") || return 1
    if ! cp "$CIP_ROOT/trusted/history/accepted" "$staged" ||
       [ "$(sha256sum "$staged" | cut -d ' ' -f 1)" != "$expected" ] ||
       ! chown 41001:41001 "$staged" || ! chmod 644 "$staged"; then
        rm -f "$staged"
        return 1
    fi
    sync -f "$staged" || { rm -f "$staged"; return 1; }
    mv -f "$staged" "$CIP_ROOT/chambers/a/candidate"
    # Rename is the commit point. Do not report a later failed check as 'no change'.
}
