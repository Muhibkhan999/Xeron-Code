"""Shared Xeron Code environment policy for FXC client surfaces."""

from collections.abc import Mapping

from free_claude_code.cli.environment import client_environment

XERON_CODE_AUTO_COMPACT_WINDOW = "190000"
XERON_BINARY_NAME = "claude"

# Backwards compatibility
CLAUDE_CODE_AUTO_COMPACT_WINDOW = XERON_CODE_AUTO_COMPACT_WINDOW
CLAUDE_BINARY_NAME = XERON_BINARY_NAME


def xeron_proxy_values(proxy_root_url: str, auth_token: str) -> dict[str, str]:
    """Settings shared by launched Xeron sessions and the VS Code extension."""
    return {
        "ANTHROPIC_BASE_URL": proxy_root_url,
        "ANTHROPIC_AUTH_TOKEN": auth_token,
        "CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY": "1",
        "CLAUDE_CODE_AUTO_COMPACT_WINDOW": XERON_CODE_AUTO_COMPACT_WINDOW,
        "DISABLE_AUTOUPDATER": "1",
        "DISABLE_FEEDBACK_COMMAND": "1",
        "DISABLE_ERROR_REPORTING": "1",
    }


def build_xeron_proxy_env(
    *,
    proxy_root_url: str,
    auth_token: str,
    base_env: Mapping[str, str],
) -> dict[str, str]:
    """Return the canonical environment for Xeron Code proxy sessions."""

    # Xeron's aggregate traffic flag also suppresses gateway model discovery.
    return client_environment(
        base_env,
        proxy_root_url=proxy_root_url,
        remove_prefixes=("ANTHROPIC_",),
        remove_keys=("CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC",),
        updates=xeron_proxy_values(proxy_root_url, auth_token),
    )


# Backwards compatibility aliases
claude_proxy_values = xeron_proxy_values
build_claude_proxy_env = build_xeron_proxy_env
