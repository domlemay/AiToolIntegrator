"""Pydantic v2 models for AiToolIntegrator configuration and plugin validation."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, field_validator, model_validator

VALID_CATEGORIES = {
    "llm-runtime",
    "coding-assistant",
    "agent-framework",
    "agent-orchestrator",
    "prompt-engineering",
    "image-generation",
    "speech-to-text",
    "rag-framework",
    "dev-tool",
}

VALID_ISOLATION_TYPES = {"venv", "docker", "none"}
VALID_ENTRY_TYPES = {"python", "binary"}
VALID_INSTALL_METHODS = {"auto", "script", "binary", "docker"}


class DescriptionModel(BaseModel):
    """Short and long descriptions for a plugin or registry entry."""

    short: str
    long: str

    @field_validator("short")
    @classmethod
    def short_not_empty(cls, v: str) -> str:
        """Validate that short description is not empty."""
        if not v.strip():
            raise ValueError("short description cannot be empty")
        return v


class SourceModel(BaseModel):
    """Source repository information for a plugin."""

    repo: str
    branch: str = "main"
    homepage: str | None = None

    @field_validator("repo")
    @classmethod
    def repo_is_url(cls, v: str) -> str:
        """Validate that repo looks like a URL."""
        if not v.startswith(("https://", "http://", "git@")):
            raise ValueError(f"repo must be a valid URL, got: {v!r}")
        return v


class EntryModel(BaseModel):
    """Plugin execution entrypoint configuration."""

    module: str = "run.py"
    function: str = "run"
    type: str = "python"

    @field_validator("type")
    @classmethod
    def valid_type(cls, v: str) -> str:
        """Validate entry type."""
        if v not in VALID_ENTRY_TYPES:
            raise ValueError(f"entry.type must be one of {VALID_ENTRY_TYPES}")
        return v


class InstallModel(BaseModel):
    """Plugin installation configuration."""

    method: str = "auto"
    script: str | None = "install.py"
    requirements: str | None = "requirements.txt"

    @field_validator("method")
    @classmethod
    def valid_method(cls, v: str) -> str:
        """Validate install method."""
        if v not in VALID_INSTALL_METHODS:
            raise ValueError(f"install.method must be one of {VALID_INSTALL_METHODS}")
        return v


class RequirementsModel(BaseModel):
    """System and Python requirements for a plugin."""

    python: str = ">=3.11"
    platforms: list[str] = ["windows", "macos", "linux"]
    gpu: bool = False
    min_ram_gb: int = 4


class IsolationModel(BaseModel):
    """Plugin isolation configuration."""

    type: str = "venv"
    docker_image: str | None = None

    @field_validator("type")
    @classmethod
    def valid_type(cls, v: str) -> str:
        """Validate isolation type."""
        if v not in VALID_ISOLATION_TYPES:
            raise ValueError(f"isolation.type must be one of {VALID_ISOLATION_TYPES}")
        return v

    @model_validator(mode="after")
    def docker_requires_image(self) -> IsolationModel:
        """Validate that docker isolation specifies an image."""
        if self.type == "docker" and not self.docker_image:
            raise ValueError("isolation.docker_image required when type is 'docker'")
        return self


class PluginManifest(BaseModel):
    """Validates a plugin's plugin.yaml manifest — Spec V1."""

    name: str
    version: str
    spec_version: str = "1.0.0"
    display_name: str
    description: DescriptionModel
    source: SourceModel
    category: str
    tags: list[str]
    entry: EntryModel = EntryModel()
    install: InstallModel = InstallModel()
    requirements: RequirementsModel = RequirementsModel()
    isolation: IsolationModel = IsolationModel()

    @field_validator("name")
    @classmethod
    def name_is_slug(cls, v: str) -> str:
        """Validate that name is a valid slug (lowercase, hyphens/underscores only)."""
        import re

        if not re.match(r"^[a-z0-9][a-z0-9_-]*$", v):
            raise ValueError(f"name must be a slug (lowercase, hyphens/underscores), got: {v!r}")
        return v

    @field_validator("tags")
    @classmethod
    def tags_not_empty(cls, v: list[str]) -> list[str]:
        """Validate that at least one tag is provided."""
        if not v:
            raise ValueError("at least one tag is required")
        return v

    @field_validator("category")
    @classmethod
    def valid_category(cls, v: str) -> str:
        """Validate plugin category."""
        if v not in VALID_CATEGORIES:
            raise ValueError(f"category must be one of {sorted(VALID_CATEGORIES)}")
        return v


class RegistryEntry(BaseModel):
    """Validates a single tool entry in tools.json."""

    name: str
    version: str
    description_short: str
    description_long: str
    repo: str
    homepage: str | None = None
    license: str = "MIT"
    stars: int = 0
    category: str
    tags: list[str]
    language: str = "python"
    platforms: list[str] = ["windows", "macos", "linux"]
    requires_gpu: bool = False
    min_ram_gb: int = 4

    @field_validator("name")
    @classmethod
    def name_is_slug(cls, v: str) -> str:
        """Validate name is a valid slug."""
        import re

        if not re.match(r"^[a-z0-9][a-z0-9_-]*$", v):
            raise ValueError(f"name must be a slug, got: {v!r}")
        return v

    @field_validator("stars")
    @classmethod
    def stars_non_negative(cls, v: int) -> int:
        """Validate star count is non-negative."""
        if v < 0:
            raise ValueError("stars must be >= 0")
        return v

    @field_validator("category")
    @classmethod
    def valid_category(cls, v: str) -> str:
        """Validate category."""
        if v not in VALID_CATEGORIES:
            raise ValueError(f"category must be one of {sorted(VALID_CATEGORIES)}")
        return v


class AppConfig(BaseModel):
    """Global application configuration."""

    plugins_dir: str = ""
    registry_path: str = ""
    log_level: str = "INFO"
    github_token: str | None = None

    @field_validator("log_level")
    @classmethod
    def valid_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid:
            raise ValueError(f"log_level must be one of {valid}")
        return v.upper()


class PluginConfig(BaseModel):
    """Runtime configuration for a plugin execution."""

    plugin_name: str
    config_data: dict[str, Any] = {}
    cli_args: list[str] = []

    def merged(self, overrides: dict[str, Any]) -> PluginConfig:
        """Return a new PluginConfig with overrides applied."""
        merged_data = {**self.config_data, **overrides}
        return PluginConfig(
            plugin_name=self.plugin_name,
            config_data=merged_data,
            cli_args=self.cli_args,
        )
