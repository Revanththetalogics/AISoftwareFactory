"""
Comprehensive tests for CustomizationService to increase coverage.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from backend.services.customization_service import (
    CustomizationService,
    ThemeMode,
    LayoutType,
    ColorScheme,
    Theme,
    Layout,
    UserPreferences,
    CustomComponent
)


class TestCustomizationService:
    """Comprehensive tests for CustomizationService."""

    @pytest.fixture
    def customization_service(self):
        """Create CustomizationService instance."""
        service = CustomizationService()
        # Clear existing custom data for clean tests
        # Keep system defaults but clear custom entries
        custom_themes = {k: v for k, v in service.themes.items() if not v.is_system_default}
        custom_layouts = {k: v for k, v in service.layouts.items() if not v.is_system_default}
        for theme_id in custom_themes:
            del service.themes[theme_id]
        for layout_id in custom_layouts:
            del service.layouts[layout_id]
        service.user_preferences.clear()
        service.custom_components.clear()
        return service

    def test_init(self, customization_service):
        """Test CustomizationService initialization."""
        assert customization_service is not None
        assert isinstance(customization_service.themes, dict)
        assert isinstance(customization_service.layouts, dict)
        assert isinstance(customization_service.user_preferences, dict)
        assert isinstance(customization_service.custom_components, dict)
        
        # Should have default themes and layouts
        assert len(customization_service.themes) > 0
        assert len(customization_service.layouts) > 0

    @pytest.mark.asyncio
    async def test_create_theme_success(self, customization_service):
        """Test successful theme creation."""
        theme = await customization_service.create_theme(
            name="Custom Dark Theme",
            mode=ThemeMode.DARK,
            primary_color="#6366f1",
            secondary_color="#8b5cf6",
            accent_color="#ec4899",
            background_color="#0f172a",
            text_color="#f1f5f9",
            border_color="#334155",
            created_by="user123"
        )

        assert isinstance(theme, Theme)
        assert theme.name == "Custom Dark Theme"
        assert theme.mode == ThemeMode.DARK
        assert theme.primary_color == "#6366f1"
        assert theme.is_custom is True
        assert theme.created_by == "user123"
        assert theme.id.startswith("theme_")
        assert "created_at" in theme.__dict__
        assert "updated_at" in theme.__dict__

        # Verify theme was stored
        assert theme.id in customization_service.themes
        assert customization_service.themes[theme.id] == theme

    @pytest.mark.asyncio
    async def test_get_theme_success(self, customization_service):
        """Test getting theme by ID."""
        # Create theme first
        theme = await customization_service.create_theme(
            name="Test Theme",
            mode=ThemeMode.LIGHT,
            primary_color="#000000",
            secondary_color="#ffffff",
            accent_color="#ff0000",
            background_color="#ffffff",
            text_color="#000000",
            border_color="#cccccc"
        )

        # Get theme
        retrieved_theme = await customization_service.get_theme(theme.id)

        assert retrieved_theme is not None
        assert retrieved_theme.id == theme.id
        assert retrieved_theme.name == "Test Theme"

    @pytest.mark.asyncio
    async def test_get_theme_not_found(self, customization_service):
        """Test getting non-existent theme."""
        result = await customization_service.get_theme("nonexistent-theme-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_list_themes_success(self, customization_service):
        """Test listing all themes."""
        # Create custom theme
        custom_theme = await customization_service.create_theme(
            name="Custom Theme",
            mode=ThemeMode.DARK,
            primary_color="#000000",
            secondary_color="#ffffff",
            accent_color="#ff0000",
            background_color="#000000",
            text_color="#ffffff",
            border_color="#333333"
        )

        # List themes (includes system defaults)
        themes = await customization_service.list_themes()

        assert len(themes) >= 1  # At least our custom theme plus system themes
        theme_ids = [t.id for t in themes]
        assert custom_theme.id in theme_ids

    @pytest.mark.asyncio
    async def test_list_themes_filter_system(self, customization_service):
        """Test listing themes with system filter."""
        # Create custom theme
        await customization_service.create_theme(
            name="Custom Theme",
            mode=ThemeMode.LIGHT,
            primary_color="#000000",
            secondary_color="#ffffff",
            accent_color="#ff0000",
            background_color="#ffffff",
            text_color="#000000",
            border_color="#cccccc"
        )

        # List only custom themes
        custom_themes = await customization_service.list_themes(include_system=False)

        # Should only have our custom theme (no system themes)
        assert len(custom_themes) == 1
        assert custom_themes[0].is_custom is True

    @pytest.mark.asyncio
    async def test_update_theme_success(self, customization_service):
        """Test updating theme."""
        # Create custom theme first
        theme = await customization_service.create_theme(
            name="Original Theme",
            mode=ThemeMode.LIGHT,
            primary_color="#000000",
            secondary_color="#ffffff",
            accent_color="#ff0000",
            background_color="#ffffff",
            text_color="#000000",
            border_color="#cccccc"
        )

        # Update theme
        updated_theme = await customization_service.update_theme(
            theme_id=theme.id,
            name="Updated Theme",
            primary_color="#ff0000",
            background_color="#000000"
        )

        assert updated_theme.id == theme.id
        assert updated_theme.name == "Updated Theme"
        assert updated_theme.primary_color == "#ff0000"
        assert updated_theme.background_color == "#000000"
        # Updated timestamp should be newer
        assert updated_theme.updated_at >= theme.updated_at

    @pytest.mark.asyncio
    async def test_update_theme_system_forbidden(self, customization_service):
        """Test updating system theme (should be forbidden)."""
        # Try to update system default theme
        system_theme_id = "theme_light"
        
        with pytest.raises(ValueError) as exc_info:
            await customization_service.update_theme(
                theme_id=system_theme_id,
                name="Modified System Theme"
            )

        assert "Cannot modify system default themes" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_delete_theme_success(self, customization_service):
        """Test deleting theme."""
        # Create custom theme first
        theme = await customization_service.create_theme(
            name="To Delete Theme",
            mode=ThemeMode.LIGHT,
            primary_color="#000000",
            secondary_color="#ffffff",
            accent_color="#ff0000",
            background_color="#ffffff",
            text_color="#000000",
            border_color="#cccccc"
        )

        # Verify theme exists
        assert theme.id in customization_service.themes

        # Delete theme
        result = await customization_service.delete_theme(theme.id)

        assert result is True
        # Verify theme was removed
        assert theme.id not in customization_service.themes

    @pytest.mark.asyncio
    async def test_delete_theme_system_forbidden(self, customization_service):
        """Test deleting system theme (should be forbidden)."""
        system_theme_id = "theme_light"
        
        with pytest.raises(ValueError) as exc_info:
            await customization_service.delete_theme(system_theme_id)

        assert "Cannot delete system default themes" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_layout_success(self, customization_service):
        """Test creating layout configuration."""
        layout = await customization_service.create_layout(
            name="Custom Dashboard Layout",
            layout_type=LayoutType.CUSTOM,
            sidebar_width=300,
            content_spacing=20,
            card_border_radius=10,
            font_size="medium",
            created_by="user123"
        )

        assert isinstance(layout, Layout)
        assert layout.name == "Custom Dashboard Layout"
        assert layout.type == LayoutType.CUSTOM
        assert layout.sidebar_width == 300
        assert layout.content_spacing == 20
        assert layout.card_border_radius == 10
        assert layout.font_size == "medium"
        assert layout.is_custom is True
        assert layout.created_by == "user123"
        assert layout.id.startswith("layout_")
        assert "created_at" in layout.__dict__
        assert "updated_at" in layout.__dict__

        # Verify layout was stored
        assert layout.id in customization_service.layouts
        assert customization_service.layouts[layout.id] == layout

    @pytest.mark.asyncio
    async def test_get_layout_success(self, customization_service):
        """Test getting layout configuration."""
        # Create layout first
        layout = await customization_service.create_layout(
            name="Test Layout",
            layout_type=LayoutType.COMPACT,
            sidebar_width=250,
            content_spacing=15,
            card_border_radius=5,
            font_size="small"
        )

        # Get layout
        retrieved_layout = await customization_service.get_layout(layout.id)

        assert retrieved_layout is not None
        assert retrieved_layout.id == layout.id
        assert retrieved_layout.name == "Test Layout"

    @pytest.mark.asyncio
    async def test_list_layouts_success(self, customization_service):
        """Test listing layout configurations."""
        # Create custom layout
        custom_layout = await customization_service.create_layout(
            name="Custom Layout",
            layout_type=LayoutType.CUSTOM,
            sidebar_width=350,
            content_spacing=25,
            card_border_radius=12,
            font_size="large"
        )

        # List layouts (includes system defaults)
        layouts = await customization_service.list_layouts()

        assert len(layouts) >= 1  # At least our custom layout plus system layouts
        layout_ids = [l.id for l in layouts]
        assert custom_layout.id in layout_ids

    @pytest.mark.asyncio
    async def test_get_user_preferences_new_user(self, customization_service):
        """Test getting user preferences for new user (creates defaults)."""
        user_id = "newuser123"
        
        # Get preferences for new user
        preferences = await customization_service.get_user_preferences(user_id)

        assert isinstance(preferences, UserPreferences)
        assert preferences.user_id == user_id
        assert preferences.theme_id == "theme_light"  # Default theme
        assert preferences.layout_id == "layout_default"  # Default layout
        assert preferences.language == "en-US"
        assert preferences.notifications_enabled is True
        assert "created_at" in preferences.__dict__
        assert "updated_at" in preferences.__dict__

        # Verify preferences were stored
        assert user_id in customization_service.user_preferences
        assert customization_service.user_preferences[user_id] == preferences

    @pytest.mark.asyncio
    async def test_get_user_preferences_existing_user(self, customization_service):
        """Test getting existing user preferences."""
        user_id = "existinguser123"
        
        # Create preferences first
        await customization_service.get_user_preferences(user_id)
        
        # Update preferences
        await customization_service.update_user_preferences(
            user_id=user_id,
            theme_id="theme_dark",
            notifications_enabled=False
        )

        # Get preferences again
        preferences = await customization_service.get_user_preferences(user_id)

        assert preferences.user_id == user_id
        assert preferences.theme_id == "theme_dark"  # Updated value
        assert preferences.notifications_enabled is False  # Updated value

    @pytest.mark.asyncio
    async def test_update_user_preferences_success(self, customization_service):
        """Test updating user preferences."""
        user_id = "user123"
        
        # Get initial preferences
        initial_prefs = await customization_service.get_user_preferences(user_id)

        # Update preferences
        updated_prefs = await customization_service.update_user_preferences(
            user_id=user_id,
            theme_id="theme_dark",
            layout_id="layout_compact",
            language="es-ES",
            notifications_enabled=False,
            compact_mode=True,
            recent_colors=["#ff0000", "#00ff00", "#0000ff"],
            favorite_themes=["theme_dark", "theme_blue_professional"]
        )

        assert updated_prefs.user_id == user_id
        assert updated_prefs.theme_id == "theme_dark"
        assert updated_prefs.layout_id == "layout_compact"
        assert updated_prefs.language == "es-ES"
        assert updated_prefs.notifications_enabled is False
        assert updated_prefs.compact_mode is True
        assert updated_prefs.recent_colors == ["#ff0000", "#00ff00", "#0000ff"]
        assert updated_prefs.favorite_themes == ["theme_dark", "theme_blue_professional"]
        # Updated timestamp should be newer
        assert updated_prefs.updated_at >= initial_prefs.updated_at

    @pytest.mark.asyncio
    async def test_create_custom_component_success(self, customization_service):
        """Test creating custom component."""
        component = await customization_service.create_custom_component(
            name="Custom Button",
            component_type="button",
            html_template="<button>{{text}}</button>",
            css_styles=".custom-button { color: red; }",
            javascript_code="console.log('Custom button loaded');",
            created_by="user123"
        )

        assert isinstance(component, CustomComponent)
        assert component.name == "Custom Button"
        assert component.type == "button"
        assert component.html_template == "<button>{{text}}</button>"
        assert component.css_styles == ".custom-button { color: red; }"
        assert component.javascript_code == "console.log('Custom button loaded');"
        assert component.is_active is True
        assert component.created_by == "user123"
        assert component.id.startswith("component_")
        assert "created_at" in component.__dict__
        assert "updated_at" in component.__dict__

        # Verify component was stored
        assert component.id in customization_service.custom_components
        assert customization_service.custom_components[component.id] == component

    @pytest.mark.asyncio
    async def test_get_custom_component_success(self, customization_service):
        """Test getting custom component."""
        # Create component first
        component = await customization_service.create_custom_component(
            name="Test Component",
            component_type="card",
            html_template="<div>{{content}}</div>",
            css_styles=".test-card { padding: 1rem; }",
            javascript_code="alert('Hello');",
            created_by="user123"
        )

        # Get component
        retrieved_component = await customization_service.get_custom_component(component.id)

        assert retrieved_component is not None
        assert retrieved_component.id == component.id
        assert retrieved_component.name == "Test Component"

    @pytest.mark.asyncio
    async def test_list_custom_components_success(self, customization_service):
        """Test listing custom components."""
        # Create multiple components
        component1 = await customization_service.create_custom_component(
            name="Component 1",
            component_type="input",
            html_template="<input />",
            css_styles="",
            javascript_code="",
            created_by="user123"
        )

        component2 = await customization_service.create_custom_component(
            name="Component 2",
            component_type="select",
            html_template="<select></select>",
            css_styles="",
            javascript_code="",
            created_by="user123"
        )

        # List components
        components = await customization_service.list_custom_components()

        assert len(components) == 2
        component_names = [c.name for c in components]
        assert "Component 1" in component_names
        assert "Component 2" in component_names

    @pytest.mark.asyncio
    async def test_toggle_component_status_success(self, customization_service):
        """Test toggling component status."""
        # Create component first
        component = await customization_service.create_custom_component(
            name="Toggle Test Component",
            component_type="div",
            html_template="<div>Test</div>",
            css_styles="",
            javascript_code="",
            created_by="user123"
        )

        # Component should be active initially
        assert component.is_active is True

        # Deactivate component
        result = await customization_service.toggle_component_status(component.id, False)

        assert result is True
        updated_component = customization_service.custom_components[component.id]
        assert updated_component.is_active is False
        assert updated_component.updated_at >= component.updated_at

        # Activate component again
        result = await customization_service.toggle_component_status(component.id, True)

        assert result is True
        updated_component = customization_service.custom_components[component.id]
        assert updated_component.is_active is True

    @pytest.mark.asyncio
    async def test_get_system_defaults_success(self, customization_service):
        """Test getting system defaults."""
        defaults = await customization_service.get_system_defaults()

        assert isinstance(defaults, dict)
        assert "default_theme" in defaults
        assert "default_layout" in defaults
        assert "available_modes" in defaults
        assert "available_layout_types" in defaults
        assert "color_schemes" in defaults
        
        # Check that enums are converted to values
        assert isinstance(defaults["available_modes"], list)
        assert "light" in defaults["available_modes"]
        assert "dark" in defaults["available_modes"]
        
        assert isinstance(defaults["available_layout_types"], list)
        assert "default" in defaults["available_layout_types"]
        assert "compact" in defaults["available_layout_types"]

    @pytest.mark.asyncio
    async def test_export_theme_success(self, customization_service):
        """Test exporting theme."""
        # Create theme
        theme = await customization_service.create_theme(
            name="Export Theme",
            mode=ThemeMode.DARK,
            primary_color="#ff0000",
            secondary_color="#00ff00",
            accent_color="#0000ff",
            background_color="#000000",
            text_color="#ffffff",
            border_color="#333333"
        )

        # Export theme
        exported_data = await customization_service.export_theme(theme.id)

        assert isinstance(exported_data, dict)
        assert "theme" in exported_data
        assert exported_data["theme"]["name"] == "Export Theme"
        assert exported_data["theme"]["mode"] == "dark"
        assert exported_data["theme"]["primary_color"] == "#ff0000"
        assert "exported_at" in exported_data
        assert exported_data["version"] == "1.0"

    @pytest.mark.asyncio
    async def test_import_theme_success(self, customization_service):
        """Test importing theme."""
        theme_data = {
            "theme": {
                "name": "Imported Theme",
                "mode": "light",
                "primary_color": "#abcdef",
                "secondary_color": "#fedcba",
                "accent_color": "#123456",
                "background_color": "#ffffff",
                "text_color": "#000000",
                "border_color": "#cccccc"
            }
        }

        # Import theme
        imported_theme = await customization_service.import_theme(theme_data, "user123")

        assert isinstance(imported_theme, Theme)
        assert imported_theme.name == "Imported Theme"
        assert imported_theme.mode == ThemeMode.LIGHT
        assert imported_theme.primary_color == "#abcdef"
        assert imported_theme.secondary_color == "#fedcba"
        assert imported_theme.created_by == "user123"
        assert imported_theme.id in customization_service.themes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])