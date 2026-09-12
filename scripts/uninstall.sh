#!/bin/sh
set -eu

PACKAGE_NAME="free-xeron-code"
FXC_HOME_DIRNAME=".fxc"
FXC_MACOS_BUNDLE_ID="io.github.Muhibkhan999.free-xeron-code"
FXC_MACOS_OWNER_FILE=".free-xeron-code-owner"
# Include retired entry points so older installations are fully stopped and removed.
FXC_COMMANDS="fxc-desktop fxc-server fxc-xeron fxc-codex fxc-pi fxc-opencode fxc-cline fxc-hermes fxc-dsh fxc-grok fxc-muse fxc-aider fxc-init free-xeron-code"

dry_run=0
uv_tool_bin=""

show_usage() {
    cat <<'USAGE'
Usage: uninstall.sh [options]

Removes the Free Xeron Code uv tool and deletes ~/.fxc/ after removal is verified.
Does not remove uv, Xeron Code, Codex, Pi, OpenCode, Cline, Hermes Agent, DeepSeek Harness, Grok Build, Muse Code, Aider, the uv-managed Python runtime, or shared PATH entries.

Options:
  --dry-run                Print commands without running them.
  --help                   Show this help text.
USAGE
}

fail() {
    printf 'error: %s\n' "$*" >&2
    exit 1
}

step() {
    printf '\n==> %s\n' "$1"
}

quote_arg() {
    case "$1" in
        *[!A-Za-z0-9_./:@%+=,-]*|"")
            escaped=$(printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g')
            printf '"%s"' "$escaped"
            ;;
        *)
            printf '%s' "$1"
            ;;
    esac
}

print_command() {
    printf '+'
    for arg in "$@"; do
        printf ' '
        quote_arg "$arg"
    done
    printf '\n'
}

run() {
    print_command "$@"
    if [ "$dry_run" -eq 1 ]; then
        return 0
    fi

    if "$@"; then
        return 0
    else
        status=$?
    fi
    fail "Command failed with exit code $status: $1"
}

is_missing_uv_tool_error() {
    normalized=$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]')
    case "$normalized" in
        *"$PACKAGE_NAME"*"is not installed"*) return 0 ;;
        *) return 1 ;;
    esac
}

add_path_entry() {
    [ -n "$1" ] || return 0
    case ":$PATH:" in
        *":$1:"*) ;;
        *) PATH="$1:$PATH" ;;
    esac
}

add_known_uv_paths() {
    if [ -n "${XDG_BIN_HOME:-}" ]; then
        add_path_entry "$XDG_BIN_HOME"
    fi
    add_path_entry "$HOME/.local/bin"
    add_path_entry "$HOME/.cargo/bin"
    export PATH
    hash -r 2>/dev/null || true
}

fxc_process_ids() {
    command_name=$1

    if command -v pgrep >/dev/null 2>&1; then
        {
            pgrep -x "$command_name" 2>/dev/null || true
            pgrep -f "(^|/)${command_name}([[:space:]]|$)" 2>/dev/null || true
        } | sort -nu
        return 0
    fi

    ps -A -o pid= -o args= 2>/dev/null |
        awk -v command_name="$command_name" '
            BEGIN {
                pattern = "(^|/)" command_name "([[:space:]]|$)"
            }
            {
                process_id = $1
                sub(/^[[:space:]]*[0-9]+[[:space:]]+/, "")
                if ($0 ~ pattern) {
                    print process_id
                }
            }
        ' || true
}

is_fxc_command_running() {
    [ -n "$(fxc_process_ids "$1")" ]
}

assert_no_fxc_processes_running() {
    running=""
    for command_name in $FXC_COMMANDS; do
        if is_fxc_command_running "$command_name"; then
            running="${running} ${command_name}"
        fi
    done

    if [ -n "$running" ]; then
        fail "Free Xeron Code is still running (${running# }). Stop those processes, then rerun uninstall."
    fi
}

initialize_uv_context() {
    add_known_uv_paths

    if [ "$dry_run" -eq 1 ]; then
        print_command uv tool dir --bin
        return 0
    fi

    if ! command -v uv >/dev/null 2>&1; then
        fail "uv is required to remove the Free Xeron Code tool. Install uv, then rerun this uninstaller; ~/.fxc was not deleted."
    fi

    print_command uv tool dir --bin
    if uv_tool_bin=$(uv tool dir --bin); then
        :
    else
        status=$?
        fail "Could not determine the uv tool bin directory (exit code $status); ~/.fxc was not deleted."
    fi
    [ -n "$uv_tool_bin" ] || fail "uv returned an empty tool bin directory; ~/.fxc was not deleted."
}

uninstall_free_xeron_code() {
    print_command uv tool uninstall "$PACKAGE_NAME"
    if [ "$dry_run" -eq 1 ]; then
        return 0
    fi

    if output=$(uv tool uninstall "$PACKAGE_NAME" 2>&1); then
        if [ -n "$output" ]; then
            printf '%s\n' "$output"
        fi
        return 0
    else
        status=$?
    fi

    if is_missing_uv_tool_error "$output"; then
        printf 'Free Xeron Code uv tool is already absent; verifying its entry points.\n'
        return 0
    fi
    if [ -n "$output" ]; then
        printf '%s\n' "$output" >&2
    fi
    fail "uv tool uninstall $PACKAGE_NAME failed with exit code $status; ~/.fxc was not deleted."
}

verify_fxc_commands_removed() {
    if [ "$dry_run" -eq 1 ]; then
        printf '+ verify all Free Xeron Code entry points are absent from the uv tool bin directory\n'
        return 0
    fi

    remaining=""
    for command_name in $FXC_COMMANDS; do
        command_path="$uv_tool_bin/$command_name"
        if [ -e "$command_path" ] || [ -L "$command_path" ]; then
            remaining="${remaining} ${command_path}"
        fi
    done
    if [ -n "$remaining" ]; then
        fail "Free Xeron Code entry points remain after uv uninstall:${remaining}; ~/.fxc was not deleted."
    fi
}

macos_app_is_fxc_owned() {
    app_dir=$1
    owner_file="$app_dir/Contents/$FXC_MACOS_OWNER_FILE"
    [ -d "$app_dir" ] &&
        [ ! -L "$app_dir" ] &&
        [ -f "$owner_file" ] &&
        [ "$(cat "$owner_file")" = "$FXC_MACOS_BUNDLE_ID" ]
}

remove_macos_desktop_app() {
    [ "$(uname -s)" = "Darwin" ] || return 0

    app_dir="$HOME/Applications/Free Xeron Code.app"
    desktop_link="$HOME/Desktop/Free Xeron Code.app"

    if ! macos_app_is_fxc_owned "$app_dir"; then
        if [ -e "$app_dir" ] || [ -L "$app_dir" ]; then
            printf 'An app not managed by Free Xeron Code exists at %s; leaving it unchanged.\n' "$app_dir"
        fi
        if [ -e "$desktop_link" ] || [ -L "$desktop_link" ]; then
            printf 'The Free Xeron Code desktop item cannot be verified; leaving it unchanged.\n'
        fi
        return 0
    fi

    if [ -L "$desktop_link" ]; then
        if [ "$(readlink "$desktop_link")" = "$app_dir" ]; then
            run rm -f "$desktop_link"
        else
            printf 'A non-FXC link exists at %s; leaving it unchanged.\n' "$desktop_link"
        fi
    elif [ -e "$desktop_link" ]; then
        printf 'A non-FXC item exists at %s; leaving it unchanged.\n' "$desktop_link"
    fi
    if [ -e "$app_dir" ]; then
        run rm -rf "$app_dir"
    fi
}

purge_fxc_home() {
    fxc_home="$HOME/$FXC_HOME_DIRNAME"
    if [ ! -e "$fxc_home" ]; then
        printf 'No FXC config directory at %s; skipping purge.\n' "$fxc_home"
        return 0
    fi

    run rm -rf "$fxc_home"
    if [ "$dry_run" -eq 0 ] && [ -e "$fxc_home" ]; then
        fail "FXC config directory still exists after deletion: $fxc_home"
    fi
}

parse_args() {
    while [ "$#" -gt 0 ]; do
        case "$1" in
            --dry-run)
                dry_run=1
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            *)
                show_usage >&2
                fail "unknown option: $1"
                ;;
        esac
        shift
    done
}

parse_args "$@"
[ -n "${HOME:-}" ] || fail "HOME is not set; cannot locate Free Xeron Code data."

step "Checking for running Free Xeron Code processes"
assert_no_fxc_processes_running

step "Locating the uv-managed Free Xeron Code installation"
initialize_uv_context

step "Removing the Free Xeron Code uv tool"
uninstall_free_xeron_code

step "Verifying Free Xeron Code entry points were removed"
verify_fxc_commands_removed

step "Removing the Free Xeron Code desktop launcher"
remove_macos_desktop_app

step "Purging FXC config and data from ~/.fxc"
purge_fxc_home

if [ "$dry_run" -eq 1 ]; then
    printf '\nDry run complete. No changes were made.\n'
else
    printf '\nFree Xeron Code has been removed and verified.\n'
    printf 'uv, Xeron Code, Codex, Pi, OpenCode, Cline, Hermes Agent, DeepSeek Harness, Grok Build, Muse Code, Aider, the uv-managed Python runtime, and shared PATH entries were left installed.\n'
fi
