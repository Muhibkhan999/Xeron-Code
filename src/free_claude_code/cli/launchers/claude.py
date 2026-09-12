"""Installed Xeron launcher: native command handling with an FXC connection."""

from collections.abc import Sequence

from free_claude_code.cli.claude_env import XERON_BINARY_NAME, build_xeron_proxy_env

from .resources import LaunchResources
from .runner import HarnessSpec, LaunchContext, PreparedLaunch, launch_harness


def _configure(
    ctx: LaunchContext, args: list[str], _files: LaunchResources
) -> PreparedLaunch:
    return PreparedLaunch(
        [ctx.binary_path, *args],
        build_xeron_proxy_env(
            proxy_root_url=ctx.proxy_root_url,
            auth_token=ctx.auth_token,
            base_env=ctx.base_env,
        ),
    )


SPEC = HarnessSpec(
    binary_name=XERON_BINARY_NAME,
    display_name="Xeron Code",
    install_hint="Install Claude Code with: npm install -g @anthropic-ai/claude-code",
    configure=_configure,
)


def launch(argv: Sequence[str] | None = None) -> None:
    launch_harness(SPEC, argv)
