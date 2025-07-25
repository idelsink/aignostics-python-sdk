"""Tests for authentication settings module."""

import os
from pathlib import Path
from unittest import mock

import appdirs
import pytest
from pydantic import SecretStr

from aignostics.platform import (
    API_ROOT_DEV,
    API_ROOT_PRODUCTION,
    API_ROOT_STAGING,
    AUDIENCE_DEV,
    AUDIENCE_PRODUCTION,
    AUDIENCE_STAGING,
    AUTHORIZATION_BASE_URL_DEV,
    AUTHORIZATION_BASE_URL_PRODUCTION,
    AUTHORIZATION_BASE_URL_STAGING,
    DEVICE_URL_DEV,
    DEVICE_URL_PRODUCTION,
    DEVICE_URL_STAGING,
    JWS_JSON_URL_DEV,
    JWS_JSON_URL_PRODUCTION,
    JWS_JSON_URL_STAGING,
    REDIRECT_URI_DEV,
    REDIRECT_URI_PRODUCTION,
    REDIRECT_URI_STAGING,
    TOKEN_URL_DEV,
    TOKEN_URL_PRODUCTION,
    TOKEN_URL_STAGING,
    UNKNOWN_ENDPOINT_URL,
    Settings,
    settings,
)
from aignostics.utils import __project_name__


@pytest.fixture
def mock_env_vars():  # noqa: ANN201
    """Mock environment variables required for settings."""
    with mock.patch.dict(
        os.environ,
        {
            f"{__project_name__.upper()}_CLIENT_ID_DEVICE": "test-client-id-device",
            f"{__project_name__.upper()}_CLIENT_ID_INTERACTIVE": "test-client-id-interactive",
        },
    ):
        yield


@pytest.fixture
def reset_cached_settings():  # noqa: ANN201
    """Reset the cached authentication settings."""
    from aignostics.platform._settings import __cached_settings

    # Store original
    original = __cached_settings

    settings.__cached_settings = None

    yield

    # Restore original
    settings.__cached_settings = original


def test_authentication_settings_production(mock_env_vars, reset_cached_settings) -> None:
    """Test authentication settings with production API root."""
    # Create settings with production API root
    settings = Settings(
        client_id_device=SecretStr("test-client-id-device"),
        client_id_interactive=SecretStr("test-client-id-interactive"),
        api_root=API_ROOT_PRODUCTION,
    )

    # Validate production-specific settings
    assert settings.api_root == API_ROOT_PRODUCTION
    assert settings.audience == AUDIENCE_PRODUCTION
    assert settings.authorization_base_url == AUTHORIZATION_BASE_URL_PRODUCTION
    assert settings.token_url == TOKEN_URL_PRODUCTION
    assert settings.redirect_uri == REDIRECT_URI_PRODUCTION
    assert settings.device_url == DEVICE_URL_PRODUCTION
    assert settings.jws_json_url == JWS_JSON_URL_PRODUCTION

    # Test other properties
    assert settings.scope == "offline_access, profile, email, openid"
    assert settings.scope_elements == ["offline_access", "profile", "email", "openid"]
    assert settings.cache_dir == appdirs.user_cache_dir(__project_name__)
    assert settings.token_file == Path(settings.cache_dir) / ".token"
    assert settings.request_timeout_seconds == 30
    assert settings.authorization_backoff_seconds == 3


def test_authentication_settings_staging(mock_env_vars) -> None:
    """Test authentication settings with staging API root."""
    settings = Settings(
        client_id_device=SecretStr("test-client-id-device"),
        client_id_interactive=SecretStr("test-client-id-interactive"),
        api_root=API_ROOT_STAGING,
    )

    assert settings.api_root == API_ROOT_STAGING
    assert settings.audience == AUDIENCE_STAGING
    assert settings.authorization_base_url == AUTHORIZATION_BASE_URL_STAGING
    assert settings.token_url == TOKEN_URL_STAGING
    assert settings.redirect_uri == REDIRECT_URI_STAGING
    assert settings.device_url == DEVICE_URL_STAGING
    assert settings.jws_json_url == JWS_JSON_URL_STAGING


def test_authentication_settings_dev(mock_env_vars) -> None:
    """Test authentication settings with dev API root."""
    settings = Settings(
        client_id_device=SecretStr("test-client-id-device"),
        client_id_interactive=SecretStr("test-client-id-interactive"),
        api_root=API_ROOT_DEV,
    )

    assert settings.api_root == API_ROOT_DEV
    assert settings.audience == AUDIENCE_DEV
    assert settings.authorization_base_url == AUTHORIZATION_BASE_URL_DEV
    assert settings.token_url == TOKEN_URL_DEV
    assert settings.redirect_uri == REDIRECT_URI_DEV
    assert settings.device_url == DEVICE_URL_DEV
    assert settings.jws_json_url == JWS_JSON_URL_DEV


def test_authentication_settings_unknown_api_root(mock_env_vars) -> None:
    """Test authentication settings with unknown API root raises ValueError."""
    with pytest.raises(ValueError, match=UNKNOWN_ENDPOINT_URL):
        Settings(
            client_id_device=SecretStr("test-client-id-device"),
            client_id_interactive=SecretStr("test-client-id-interactive"),
            api_root="https://unknown.example.com",
        )


def test_scope_elements_empty() -> None:
    """Test scope_elements property with empty scope."""
    settings = Settings(
        client_id_device=SecretStr("test-client-id-device"),
        client_id_interactive=SecretStr("test-client-id-interactive"),
        scope="",
        api_root=API_ROOT_PRODUCTION,
    )
    assert settings.scope_elements == []


def test_scope_elements_multiple() -> None:
    """Test scope_elements property with multiple scopes."""
    settings = Settings(
        client_id_device=SecretStr("test-client-id-device"),
        client_id_interactive=SecretStr("test-client-id-interactive"),
        scope="offline_access, profile, email",
        api_root=API_ROOT_PRODUCTION,
    )
    assert settings.scope_elements == ["offline_access", "profile", "email"]


def test_authentication_settings_with_refresh_token(mock_env_vars) -> None:
    """Test authentication settings with refresh token."""
    settings = Settings(
        client_id_device=SecretStr("test-client-id-device"),
        client_id_interactive=SecretStr("test-client-id-interactive"),
        refresh_token=SecretStr("test-refresh-token"),
        api_root=API_ROOT_PRODUCTION,
    )
    assert settings.refresh_token == SecretStr("test-refresh-token")


def test_lazy_authentication_settings(mock_env_vars, reset_cached_settings) -> None:
    """Test lazy loading of authentication settings."""
    # First call should create the settings
    settings1 = settings()
    assert settings1 is not None

    # Second call should return the same instance
    settings2 = settings()
    assert settings2 is settings1


@pytest.mark.sequential
# TODO(Helmut): fix race
@pytest.mark.skip
def test_authentication_settings_with_env_vars(mock_env_vars, reset_cached_settings) -> None:
    """Test authentication settings from environment variables."""
    settings1 = settings()
    assert settings1.client_id_device.get_secret_value() == "test-client-id-device"
    assert settings1.client_id_interactive.get_secret_value() == "test-client-id-interactive"


# TODO(Helmut): fixme
@pytest.mark.skip
def test_custom_env_file_location(mock_env_vars) -> None:
    """Test custom env file location."""
    custom_env_file = "/home/dummy/test_env_file"
    with mock.patch.dict(os.environ, {f"{__project_name__.upper()}_ENV_FILE": custom_env_file}):
        settings = Settings.model_config
        assert custom_env_file in settings["env_file"]


def test_custom_cache_dir(mock_env_vars) -> None:
    """Test custom cache directory."""
    custom_cache_dir = "/home/dummy/test_cache_dir"
    settings = Settings(
        client_id_device=SecretStr("test-client-id-device"),
        client_id_interactive=SecretStr("test-client-id-interactive"),
        cache_dir=custom_cache_dir,
        api_root=API_ROOT_PRODUCTION,
    )
    assert settings.cache_dir == custom_cache_dir
    assert settings.token_file == Path(custom_cache_dir) / ".token"


def test_issuer_computed_field_production(mock_env_vars) -> None:
    """Test issuer computed field with production authorization base URL."""
    settings = Settings(
        client_id_device=SecretStr("test-client-id-device"),
        client_id_interactive=SecretStr("test-client-id-interactive"),
        api_root=API_ROOT_PRODUCTION,
    )
    # Production authorization_base_url is https://aignostics-platform.eu.auth0.com/authorize
    # So issuer should be https://aignostics-platform.eu.auth0.com/
    expected_issuer = "https://aignostics-platform.eu.auth0.com/"
    assert settings.issuer == expected_issuer


def test_issuer_computed_field_staging(mock_env_vars) -> None:
    """Test issuer computed field with staging authorization base URL."""
    settings = Settings(
        client_id_device=SecretStr("test-client-id-device"),
        client_id_interactive=SecretStr("test-client-id-interactive"),
        api_root=API_ROOT_STAGING,
    )
    # Staging authorization_base_url is https://todo (placeholder)
    # So issuer should be https://todo/
    expected_issuer = "https://todo/"
    assert settings.issuer == expected_issuer


def test_issuer_computed_field_dev(mock_env_vars) -> None:
    """Test issuer computed field with dev authorization base URL."""
    settings = Settings(
        client_id_device=SecretStr("test-client-id-device"),
        client_id_interactive=SecretStr("test-client-id-interactive"),
        api_root=API_ROOT_DEV,
    )
    # Dev authorization_base_url is https://dev-8ouohmmrbuh2h4vu.eu.auth0.com/authorize
    # So issuer should be https://dev-8ouohmmrbuh2h4vu.eu.auth0.com/
    expected_issuer = "https://dev-8ouohmmrbuh2h4vu.eu.auth0.com/"
    assert settings.issuer == expected_issuer


def test_issuer_computed_field_custom_url(mock_env_vars) -> None:
    """Test issuer computed field with custom authorization base URL."""
    # Avoid triggering api_root-based validator by setting all required fields manually
    settings = Settings(
        client_id_device=SecretStr("test-client-id-device"),
        client_id_interactive=SecretStr("test-client-id-interactive"),
        api_root="https://custom.platform.example.com",  # Custom api_root that doesn't match any preset
        authorization_base_url="https://custom.example.com/auth/oauth2/authorize",
        audience="test-audience",
        token_url="https://custom.example.com/auth/oauth2/token",  # noqa: S106
        redirect_uri="https://custom.example.com/callback",
        device_url="https://custom.example.com/auth/oauth2/device",
        jws_json_url="https://custom.example.com/auth/.well-known/jwks.json",
    )
    expected_issuer = "https://custom.example.com/"
    assert settings.issuer == expected_issuer


def test_issuer_computed_field_malformed_url_no_scheme(mock_env_vars) -> None:
    """Test issuer computed field with malformed URL (no scheme) falls back gracefully."""
    settings = Settings(
        client_id_device=SecretStr("test-client-id-device"),
        client_id_interactive=SecretStr("test-client-id-interactive"),
        api_root="https://custom.platform.example.com",  # Custom api_root that doesn't match any preset
        authorization_base_url="example.com/oauth2/auth",
        audience="test-audience",
        token_url="https://example.com/oauth2/token",  # noqa: S106
        redirect_uri="https://example.com/callback",
        device_url="https://example.com/oauth2/device",
        jws_json_url="https://example.com/.well-known/jwks.json",
    )
    # Should fall back to rsplit logic which removes the last path segment
    expected_issuer = "example.com/oauth2/"
    assert settings.issuer == expected_issuer


def test_issuer_computed_field_malformed_url_no_domain(mock_env_vars) -> None:
    """Test issuer computed field with malformed URL (no domain) falls back gracefully."""
    settings = Settings(
        client_id_device=SecretStr("test-client-id-device"),
        client_id_interactive=SecretStr("test-client-id-interactive"),
        api_root="https://custom.platform.example.com",  # Custom api_root that doesn't match any preset
        authorization_base_url="https:///oauth2/auth",
        audience="test-audience",
        token_url="https://example.com/oauth2/token",  # noqa: S106
        redirect_uri="https://example.com/callback",
        device_url="https://example.com/oauth2/device",
        jws_json_url="https://example.com/.well-known/jwks.json",
    )
    # Should fall back to rsplit logic which removes the last path segment
    expected_issuer = "https:///oauth2/"
    assert settings.issuer == expected_issuer


def test_issuer_computed_field_url_with_port(mock_env_vars) -> None:
    """Test issuer computed field with URL containing port number."""
    settings = Settings(
        client_id_device=SecretStr("test-client-id-device"),
        client_id_interactive=SecretStr("test-client-id-interactive"),
        api_root="https://custom.platform.example.com",  # Custom api_root that doesn't match any preset
        authorization_base_url="https://localhost:8080/oauth2/auth",
        audience="test-audience",
        token_url="https://localhost:8080/oauth2/token",  # noqa: S106
        redirect_uri="https://localhost:8080/callback",
        device_url="https://localhost:8080/oauth2/device",
        jws_json_url="https://localhost:8080/.well-known/jwks.json",
    )
    expected_issuer = "https://localhost:8080/"
    assert settings.issuer == expected_issuer


def test_issuer_computed_field_url_with_subdirectory(mock_env_vars) -> None:
    """Test issuer computed field with URL containing multiple path segments."""
    settings = Settings(
        client_id_device=SecretStr("test-client-id-device"),
        client_id_interactive=SecretStr("test-client-id-interactive"),
        api_root="https://custom.platform.example.com",  # Custom api_root that doesn't match any preset
        authorization_base_url="https://example.com/auth/v1/oauth2/authorize",
        audience="test-audience",
        token_url="https://example.com/auth/v1/oauth2/token",  # noqa: S106
        redirect_uri="https://example.com/callback",
        device_url="https://example.com/auth/v1/oauth2/device",
        jws_json_url="https://example.com/auth/v1/.well-known/jwks.json",
    )
    expected_issuer = "https://example.com/"
    assert settings.issuer == expected_issuer


def test_issuer_computed_field_url_with_query_params(mock_env_vars) -> None:
    """Test issuer computed field with URL containing query parameters."""
    settings = Settings(
        client_id_device=SecretStr("test-client-id-device"),
        client_id_interactive=SecretStr("test-client-id-interactive"),
        api_root="https://custom.platform.example.com",  # Custom api_root that doesn't match any preset
        authorization_base_url="https://example.com/oauth2/auth?param=value",
        audience="test-audience",
        token_url="https://example.com/oauth2/token",  # noqa: S106
        redirect_uri="https://example.com/callback",
        device_url="https://example.com/oauth2/device",
        jws_json_url="https://example.com/.well-known/jwks.json",
    )
    expected_issuer = "https://example.com/"
    assert settings.issuer == expected_issuer
