"""
Customization Service

Provides theming, personalization, and customization capabilities
for the ThetaAI platform including dynamic themes, layouts, and user preferences.
"""

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from backend.core.logging import get_logger

logger = get_logger(__name__)


class ThemeMode(str, Enum):
    """Available theme modes."""
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"
    AUTO = "auto"


class LayoutType(str, Enum):
    """Available layout types."""
    DEFAULT = "default"
    COMPACT = "compact"
    SPACIOUS = "spacious"
    CUSTOM = "custom"


class ColorScheme(str, Enum):
    """Predefined color schemes."""
    BLUE = "blue"
    GREEN = "green"
    PURPLE = "purple"
    ORANGE = "orange"
    RED = "red"
    CUSTOM = "custom"


@dataclass
class Theme:
    """Represents a complete theme configuration."""
    id: str
    name: str
    mode: ThemeMode
    primary_color: str
    secondary_color: str
    accent_color: str
    background_color: str
    text_color: str
    border_color: str
    is_system_default: bool = False
    is_custom: bool = False
    created_by: str | None = None
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(UTC).isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now(UTC).isoformat()


@dataclass
class Layout:
    """Represents a layout configuration."""
    id: str
    name: str
    type: LayoutType
    sidebar_width: int
    content_spacing: int
    card_border_radius: int
    font_size: str
    is_system_default: bool = False
    is_custom: bool = False
    created_by: str | None = None
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(UTC).isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now(UTC).isoformat()


@dataclass
class UserPreferences:
    """Represents user customization preferences."""
    user_id: str
    theme_id: str
    layout_id: str
    language: str
    timezone: str
    notifications_enabled: bool
    auto_save_enabled: bool
    keyboard_shortcuts_enabled: bool
    animations_enabled: bool
    compact_mode: bool
    sidebar_collapsed: bool
    recent_colors: list[str]
    favorite_themes: list[str]
    custom_css: str | None = None
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(UTC).isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now(UTC).isoformat()


@dataclass
class CustomComponent:
    """Represents a custom UI component."""
    id: str
    name: str
    type: str
    html_template: str
    css_styles: str
    javascript_code: str
    is_active: bool
    created_by: str
    created_at: str
    updated_at: str


class CustomizationService:
    """Main service for handling theming and customization."""

    def __init__(self):
        self.themes: dict[str, Theme] = {}
        self.layouts: dict[str, Layout] = {}
        self.user_preferences: dict[str, UserPreferences] = {}
        self.custom_components: dict[str, CustomComponent] = {}
        self._initialize_default_themes()
        self._initialize_default_layouts()

    def _initialize_default_themes(self):
        """Initialize with default themes."""
        # Light theme
        light_theme = Theme(
            id="theme_light",
            name="Light Theme",
            mode=ThemeMode.LIGHT,
            primary_color="#3B82F6",
            secondary_color="#6B7280",
            accent_color="#10B981",
            background_color="#FFFFFF",
            text_color="#1F2937",
            border_color="#E5E7EB",
            is_system_default=True
        )

        # Dark theme
        dark_theme = Theme(
            id="theme_dark",
            name="Dark Theme",
            mode=ThemeMode.DARK,
            primary_color="#60A5FA",
            secondary_color="#9CA3AF",
            accent_color="#34D399",
            background_color="#111827",
            text_color="#F9FAFB",
            border_color="#374151",
            is_system_default=True
        )

        # Blue professional theme
        blue_theme = Theme(
            id="theme_blue_professional",
            name="Blue Professional",
            mode=ThemeMode.LIGHT,
            primary_color="#2563EB",
            secondary_color="#4B5563",
            accent_color="#0EA5E9",
            background_color="#F9FAFB",
            text_color="#111827",
            border_color="#D1D5DB"
        )

        # Green nature theme
        green_theme = Theme(
            id="theme_green_nature",
            name="Green Nature",
            mode=ThemeMode.LIGHT,
            primary_color="#059669",
            secondary_color="#4B5563",
            accent_color="#10B981",
            background_color="#ECFDF5",
            text_color="#065F46",
            border_color="#A7F3D0"
        )

        self.themes = {
            light_theme.id: light_theme,
            dark_theme.id: dark_theme,
            blue_theme.id: blue_theme,
            green_theme.id: green_theme
        }

    def _initialize_default_layouts(self):
        """Initialize with default layouts."""
        # Default layout
        default_layout = Layout(
            id="layout_default",
            name="Default Layout",
            type=LayoutType.DEFAULT,
            sidebar_width=280,
            content_spacing=24,
            card_border_radius=8,
            font_size="medium",
            is_system_default=True
        )

        # Compact layout
        compact_layout = Layout(
            id="layout_compact",
            name="Compact Layout",
            type=LayoutType.COMPACT,
            sidebar_width=240,
            content_spacing=16,
            card_border_radius=6,
            font_size="small",
            is_system_default=True
        )

        # Spacious layout
        spacious_layout = Layout(
            id="layout_spacious",
            name="Spacious Layout",
            type=LayoutType.SPACIOUS,
            sidebar_width=320,
            content_spacing=32,
            card_border_radius=12,
            font_size="large",
            is_system_default=True
        )

        self.layouts = {
            default_layout.id: default_layout,
            compact_layout.id: compact_layout,
            spacious_layout.id: spacious_layout
        }

    async def create_theme(
        self,
        name: str,
        mode: ThemeMode,
        primary_color: str,
        secondary_color: str,
        accent_color: str,
        background_color: str,
        text_color: str,
        border_color: str,
        created_by: str | None = None
    ) -> Theme:
        """Create a new custom theme."""
        try:
            theme_id = f"theme_{uuid.uuid4().hex[:8]}"

            theme = Theme(
                id=theme_id,
                name=name,
                mode=mode,
                primary_color=primary_color,
                secondary_color=secondary_color,
                accent_color=accent_color,
                background_color=background_color,
                text_color=text_color,
                border_color=border_color,
                is_custom=True,
                created_by=created_by
            )

            self.themes[theme_id] = theme

            logger.info(f"Created theme: {name}", theme_id=theme_id)
            return theme

        except Exception as e:
            logger.error("Failed to create theme", error=str(e))
            raise

    async def get_theme(self, theme_id: str) -> Theme | None:
        """Get a specific theme by ID."""
        return self.themes.get(theme_id)

    async def list_themes(self, include_system: bool = True, include_custom: bool = True) -> list[Theme]:
        """List available themes."""
        themes = list(self.themes.values())

        if not include_system:
            themes = [t for t in themes if not t.is_system_default]

        if not include_custom:
            themes = [t for t in themes if not t.is_custom]

        return themes

    async def update_theme(
        self,
        theme_id: str,
        **updates
    ) -> Theme:
        """Update an existing theme."""
        try:
            theme = self.themes.get(theme_id)
            if not theme:
                raise ValueError(f"Theme {theme_id} not found")

            if theme.is_system_default:
                raise ValueError("Cannot modify system default themes")

            # Update allowed fields
            updatable_fields = [
                'name', 'primary_color', 'secondary_color', 'accent_color',
                'background_color', 'text_color', 'border_color'
            ]

            for field in updatable_fields:
                if field in updates:
                    setattr(theme, field, updates[field])

            theme.updated_at = datetime.now(UTC).isoformat()

            logger.info(f"Updated theme: {theme.name}", theme_id=theme_id)
            return theme

        except Exception as e:
            logger.error("Failed to update theme", error=str(e), theme_id=theme_id)
            raise

    async def delete_theme(self, theme_id: str) -> bool:
        """Delete a custom theme."""
        try:
            theme = self.themes.get(theme_id)
            if not theme:
                return False

            if theme.is_system_default:
                raise ValueError("Cannot delete system default themes")

            del self.themes[theme_id]

            # Update user preferences that used this theme
            for pref in self.user_preferences.values():
                if pref.theme_id == theme_id:
                    pref.theme_id = "theme_light"  # Fallback to default

            logger.info(f"Deleted theme: {theme.name}", theme_id=theme_id)
            return True

        except Exception as e:
            logger.error("Failed to delete theme", error=str(e), theme_id=theme_id)
            raise

    async def create_layout(
        self,
        name: str,
        layout_type: LayoutType,
        sidebar_width: int,
        content_spacing: int,
        card_border_radius: int,
        font_size: str,
        created_by: str | None = None
    ) -> Layout:
        """Create a new custom layout."""
        try:
            layout_id = f"layout_{uuid.uuid4().hex[:8]}"

            layout = Layout(
                id=layout_id,
                name=name,
                type=layout_type,
                sidebar_width=sidebar_width,
                content_spacing=content_spacing,
                card_border_radius=card_border_radius,
                font_size=font_size,
                is_custom=True,
                created_by=created_by
            )

            self.layouts[layout_id] = layout

            logger.info(f"Created layout: {name}", layout_id=layout_id)
            return layout

        except Exception as e:
            logger.error("Failed to create layout", error=str(e))
            raise

    async def get_layout(self, layout_id: str) -> Layout | None:
        """Get a specific layout by ID."""
        return self.layouts.get(layout_id)

    async def list_layouts(self, include_system: bool = True, include_custom: bool = True) -> list[Layout]:
        """List available layouts."""
        layouts = list(self.layouts.values())

        if not include_system:
            layouts = [layout for layout in layouts if not layout.is_system_default]

        if not include_custom:
            layouts = [layout for layout in layouts if not layout.is_custom]

        return layouts

    async def get_user_preferences(self, user_id: str) -> UserPreferences:
        """Get or create user preferences."""
        if user_id not in self.user_preferences:
            # Create default preferences
            preferences = UserPreferences(
                user_id=user_id,
                theme_id="theme_light",
                layout_id="layout_default",
                language="en-US",
                timezone="UTC",
                notifications_enabled=True,
                auto_save_enabled=True,
                keyboard_shortcuts_enabled=True,
                animations_enabled=True,
                compact_mode=False,
                sidebar_collapsed=False,
                recent_colors=["#3B82F6", "#10B981", "#8B5CF6"],
                favorite_themes=["theme_light", "theme_dark"]
            )
            self.user_preferences[user_id] = preferences
        else:
            preferences = self.user_preferences[user_id]

        return preferences

    async def update_user_preferences(
        self,
        user_id: str,
        **updates
    ) -> UserPreferences:
        """Update user preferences."""
        try:
            preferences = await self.get_user_preferences(user_id)

            # Update allowed fields
            updatable_fields = [
                'theme_id', 'layout_id', 'language', 'timezone',
                'notifications_enabled', 'auto_save_enabled', 'keyboard_shortcuts_enabled',
                'animations_enabled', 'compact_mode', 'sidebar_collapsed',
                'recent_colors', 'favorite_themes', 'custom_css'
            ]

            for field in updatable_fields:
                if field in updates:
                    setattr(preferences, field, updates[field])

            preferences.updated_at = datetime.now(UTC).isoformat()

            logger.info(f"Updated preferences for user {user_id}")
            return preferences

        except Exception as e:
            logger.error("Failed to update user preferences", error=str(e), user_id=user_id)
            raise

    async def create_custom_component(
        self,
        name: str,
        component_type: str,
        html_template: str,
        css_styles: str,
        javascript_code: str,
        created_by: str
    ) -> CustomComponent:
        """Create a new custom UI component."""
        try:
            component_id = f"component_{uuid.uuid4().hex[:8]}"

            component = CustomComponent(
                id=component_id,
                name=name,
                type=component_type,
                html_template=html_template,
                css_styles=css_styles,
                javascript_code=javascript_code,
                is_active=True,
                created_by=created_by,
                created_at=datetime.now(UTC).isoformat(),
                updated_at=datetime.now(UTC).isoformat()
            )

            self.custom_components[component_id] = component

            logger.info(f"Created custom component: {name}", component_id=component_id)
            return component

        except Exception as e:
            logger.error("Failed to create custom component", error=str(e))
            raise

    async def get_custom_component(self, component_id: str) -> CustomComponent | None:
        """Get a specific custom component."""
        return self.custom_components.get(component_id)

    async def list_custom_components(self, active_only: bool = True) -> list[CustomComponent]:
        """List custom components."""
        components = list(self.custom_components.values())

        if active_only:
            components = [c for c in components if c.is_active]

        return components

    async def toggle_component_status(self, component_id: str, active: bool) -> bool:
        """Toggle custom component active status."""
        try:
            component = self.custom_components.get(component_id)
            if not component:
                return False

            component.is_active = active
            component.updated_at = datetime.now(UTC).isoformat()

            status = "activated" if active else "deactivated"
            logger.info(f"Component {component.name} {status}", component_id=component_id)
            return True

        except Exception as e:
            logger.error("Failed to toggle component status", error=str(e))
            raise

    async def get_system_defaults(self) -> dict[str, Any]:
        """Get system default configurations."""
        try:
            default_theme = next((t for t in self.themes.values() if t.is_system_default and t.mode == ThemeMode.LIGHT), None)
            default_layout = next((layout for layout in self.layouts.values() if layout.is_system_default and layout.type == LayoutType.DEFAULT), None)

            return {
                "default_theme": default_theme.__dict__ if default_theme else None,
                "default_layout": default_layout.__dict__ if default_layout else None,
                "available_modes": [mode.value for mode in ThemeMode],
                "available_layout_types": [lt.value for lt in LayoutType],
                "color_schemes": [cs.value for cs in ColorScheme]
            }

        except Exception as e:
            logger.error("Failed to get system defaults", error=str(e))
            raise

    async def export_theme(self, theme_id: str) -> dict[str, Any]:
        """Export theme configuration as JSON."""
        try:
            theme = await self.get_theme(theme_id)
            if not theme:
                raise ValueError(f"Theme {theme_id} not found")

            export_data = {
                "theme": theme.__dict__,
                "exported_at": datetime.now(UTC).isoformat(),
                "version": "1.0"
            }

            return export_data

        except Exception as e:
            logger.error("Failed to export theme", error=str(e), theme_id=theme_id)
            raise

    async def import_theme(self, theme_data: dict[str, Any], created_by: str) -> Theme:
        """Import theme configuration from JSON."""
        try:
            theme_info = theme_data.get("theme", {})

            theme = await self.create_theme(
                name=theme_info.get("name", "Imported Theme"),
                mode=ThemeMode(theme_info.get("mode", "light")),
                primary_color=theme_info.get("primary_color", "#3B82F6"),
                secondary_color=theme_info.get("secondary_color", "#6B7280"),
                accent_color=theme_info.get("accent_color", "#10B981"),
                background_color=theme_info.get("background_color", "#FFFFFF"),
                text_color=theme_info.get("text_color", "#1F2937"),
                border_color=theme_info.get("border_color", "#E5E7EB"),
                created_by=created_by
            )

            logger.info(f"Imported theme: {theme.name}")
            return theme

        except Exception as e:
            logger.error("Failed to import theme", error=str(e))
            raise


# Global service instance
customization_service = CustomizationService()
