"""
Comprehensive tests for CustomizationService to increase coverage.
"""


import pytest
from backend.services.customization_service import (
    ColorScheme,
    CustomComponent,
    CustomizationService,
    Layout,
    LayoutType,
    Theme,
    ThemeMode,
    UserPreferences,
)


class TestCustomizationService:
    """Comprehensive tests for CustomizationService."""

    @pytest.fixture
    def customization_service(self):
        """Create CustomizationService instance."""
        return CustomizationService()

    def test_init(self, customization_service):
        """Test CustomizationService initialization."""
        assert customization_service is not None
        assert hasattr(customization_service, 'themes')
        assert hasattr(customization_service, 'layouts')
        assert hasattr(customization_service, 'user_preferences')
        assert hasattr(customization_service, 'custom_components')
        assert isinstance(customization_service.themes, dict)
        assert isinstance(customization_service.layouts, dict)
        assert isinstance(customization_service.user_preferences, dict)
        assert isinstance(customization_service.custom_components, dict)

        # Should have default themes initialized
        assert len(customization_service.themes) > 0
        assert "theme_light" in customization_service.themes
        assert "theme_dark" in customization_service.themes

        # Should have default layouts initialized
        assert len(customization_service.layouts) > 0
        assert "layout_default" in customization_service.layouts
        assert "layout_compact" in customization_service.layouts

    def test_initialize_default_themes(self, customization_service):
        """Test that default themes are properly initialized."""
        # Check light theme
        light_theme = customization_service.themes.get("theme_light")
        assert light_theme is not None
        assert isinstance(light_theme, Theme)
        assert light_theme.name == "Light Theme"
        assert light_theme.mode == ThemeMode.LIGHT
        assert light_theme.is_system_default is True
        assert light_theme.primary_color == "#3B82F6"
        assert light_theme.background_color == "#FFFFFF"

        # Check dark theme
        dark_theme = customization_service.themes.get("theme_dark")
        assert dark_theme is not None
        assert isinstance(dark_theme, Theme)
        assert dark_theme.name == "Dark Theme"
        assert dark_theme.mode == ThemeMode.DARK
        assert dark_theme.is_system_default is True
        assert dark_theme.background_color == "#111827"

        # Check other themes exist
        assert "theme_blue_professional" in customization_service.themes
        assert "theme_green_nature" in customization_service.themes

    def test_initialize_default_layouts(self, customization_service):
        """Test that default layouts are properly initialized."""
        # Check default layout
        default_layout = customization_service.layouts.get("layout_default")
        assert default_layout is not None
        assert isinstance(default_layout, Layout)
        assert default_layout.name == "Default Layout"
        assert default_layout.type == LayoutType.DEFAULT
        assert default_layout.is_system_default is True
        assert default_layout.sidebar_width == 280
        assert default_layout.content_spacing == 24

        # Check compact layout
        compact_layout = customization_service.layouts.get("layout_compact")
        assert compact_layout is not None
        assert isinstance(compact_layout, Layout)
        assert compact_layout.name == "Compact Layout"
        assert compact_layout.type == LayoutType.COMPACT
        assert compact_layout.is_system_default is True
        assert compact_layout.sidebar_width == 240

        # Check spacious layout
        spacious_layout = customization_service.layouts.get("layout_spacious")
        assert spacious_layout is not None
        assert isinstance(spacious_layout, Layout)
        assert spacious_layout.name == "Spacious Layout"
        assert spacious_layout.type == LayoutType.SPACIOUS
        assert spacious_layout.is_system_default is True
        assert spacious_layout.sidebar_width == 320

    @pytest.mark.asyncio
    async def test_create_theme_success(self, customization_service):
        """Test creating theme successfully."""
        result = await customization_service.create_theme(
            name="Ocean Blue Theme",
            mode=ThemeMode.DARK,
            primary_color="#0EA5E9",
            secondary_color="#64748B",
            accent_color="#06B6D4",
            background_color="#0F172A",
            text_color="#F1F5F9",
            border_color="#334155",
            created_by="user123"
        )

        assert result is not None
        assert isinstance(result, Theme)
        assert result.name == "Ocean Blue Theme"
        assert result.mode == ThemeMode.DARK
        assert result.primary_color == "#0EA5E9"
        assert result.secondary_color == "#64748B"
        assert result.accent_color == "#06B6D4"
        assert result.background_color == "#0F172A"
        assert result.text_color == "#F1F5F9"
        assert result.border_color == "#334155"
        assert result.is_custom is True
        assert result.created_by == "user123"
        assert len(result.id) > 0
        assert result.created_at is not None
        assert result.updated_at is not None
        # Should be stored in themes dict
        assert result.id in customization_service.themes

    @pytest.mark.asyncio
    async def test_get_theme_success(self, customization_service):
        """Test getting existing theme."""
        # Get default theme
        result = await customization_service.get_theme("theme_light")

        assert result is not None
        assert isinstance(result, Theme)
        assert result.id == "theme_light"
        assert result.name == "Light Theme"

    @pytest.mark.asyncio
    async def test_get_theme_not_found(self, customization_service):
        """Test getting non-existent theme."""
        result = await customization_service.get_theme("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_list_themes_all(self, customization_service):
        """Test listing all themes."""
        result = await customization_service.list_themes()

        assert isinstance(result, list)
        assert len(result) >= 4  # Should have at least default themes
        for theme in result:
            assert isinstance(theme, Theme)

    @pytest.mark.asyncio
    async def test_list_themes_exclude_system(self, customization_service):
        """Test listing themes excluding system defaults."""
        result = await customization_service.list_themes(include_system=False)

        assert isinstance(result, list)
        # Should not include system default themes
        for theme in result:
            assert theme.is_system_default is False

    @pytest.mark.asyncio
    async def test_list_themes_exclude_custom(self, customization_service):
        """Test listing themes excluding custom themes."""
        # Create a custom theme first
        await customization_service.create_theme(
            name="Custom Test", mode=ThemeMode.LIGHT,
            primary_color="#000", secondary_color="#111", accent_color="#222",
            background_color="#FFF", text_color="#000", border_color="#333"
        )

        result = await customization_service.list_themes(include_custom=False)

        assert isinstance(result, list)
        # Should not include custom themes
        for theme in result:
            assert theme.is_custom is False

    @pytest.mark.asyncio
    async def test_update_theme_success(self, customization_service):
        """Test updating existing custom theme."""
        # Create a custom theme first
        theme = await customization_service.create_theme(
            name="Updatable Theme", mode=ThemeMode.LIGHT,
            primary_color="#000", secondary_color="#111", accent_color="#222",
            background_color="#FFF", text_color="#000", border_color="#333"
        )

        # Update it
        result = await customization_service.update_theme(
            theme_id=theme.id,
            name="Updated Theme Name",
            primary_color="#FF0000",
            background_color="#000000"
        )

        assert result is not None
        assert result.name == "Updated Theme Name"
        assert result.primary_color == "#FF0000"
        assert result.background_color == "#000000"
        assert result.updated_at != result.created_at

    @pytest.mark.asyncio
    async def test_update_theme_not_found(self, customization_service):
        """Test updating non-existent theme."""
        with pytest.raises(ValueError) as exc_info:
            await customization_service.update_theme("nonexistent", name="Test")

        assert "Theme nonexistent not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_theme_system_default_forbidden(self, customization_service):
        """Test that system default themes cannot be updated."""
        with pytest.raises(ValueError) as exc_info:
            await customization_service.update_theme("theme_light", name="Modified")

        assert "Cannot modify system default themes" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_delete_theme_success(self, customization_service):
        """Test deleting custom theme successfully."""
        # Create a custom theme
        theme = await customization_service.create_theme(
            name="Deletable Theme", mode=ThemeMode.LIGHT,
            primary_color="#000", secondary_color="#111", accent_color="#222",
            background_color="#FFF", text_color="#000", border_color="#333"
        )

        # Verify it exists
        assert theme.id in customization_service.themes

        # Delete it
        result = await customization_service.delete_theme(theme.id)

        assert result is True
        assert theme.id not in customization_service.themes

    @pytest.mark.asyncio
    async def test_delete_theme_not_found(self, customization_service):
        """Test deleting non-existent theme."""
        result = await customization_service.delete_theme("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_theme_system_default_forbidden(self, customization_service):
        """Test that system default themes cannot be deleted."""
        with pytest.raises(ValueError) as exc_info:
            await customization_service.delete_theme("theme_light")

        assert "Cannot delete system default themes" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_delete_theme_updates_user_preferences(self, customization_service):
        """Test that deleting theme updates affected user preferences."""
        # Create custom theme
        theme = await customization_service.create_theme(
            name="User Theme", mode=ThemeMode.LIGHT,
            primary_color="#000", secondary_color="#111", accent_color="#222",
            background_color="#FFF", text_color="#000", border_color="#333"
        )

        # Set user preference to use this theme
        await customization_service.update_user_preferences("user123", theme_id=theme.id)

        # Verify user uses this theme
        user_prefs = await customization_service.get_user_preferences("user123")
        assert user_prefs.theme_id == theme.id

        # Delete the theme
        await customization_service.delete_theme(theme.id)

        # User should now use default theme
        updated_prefs = await customization_service.get_user_preferences("user123")
        assert updated_prefs.theme_id == "theme_light"  # Fallback to default

    @pytest.mark.asyncio
    async def test_create_layout_success(self, customization_service):
        """Test creating layout successfully."""
        result = await customization_service.create_layout(
            name="Wide Workspace",
            layout_type=LayoutType.CUSTOM,
            sidebar_width=350,
            content_spacing=40,
            card_border_radius=16,
            font_size="x-large",
            created_by="user456"
        )

        assert result is not None
        assert isinstance(result, Layout)
        assert result.name == "Wide Workspace"
        assert result.type == LayoutType.CUSTOM
        assert result.sidebar_width == 350
        assert result.content_spacing == 40
        assert result.card_border_radius == 16
        assert result.font_size == "x-large"
        assert result.is_custom is True
        assert result.created_by == "user456"
        assert len(result.id) > 0
        # Should be stored in layouts dict
        assert result.id in customization_service.layouts

    @pytest.mark.asyncio
    async def test_get_layout_success(self, customization_service):
        """Test getting existing layout."""
        result = await customization_service.get_layout("layout_default")

        assert result is not None
        assert isinstance(result, Layout)
        assert result.id == "layout_default"
        assert result.name == "Default Layout"

    @pytest.mark.asyncio
    async def test_get_layout_not_found(self, customization_service):
        """Test getting non-existent layout."""
        result = await customization_service.get_layout("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_list_layouts_all(self, customization_service):
        """Test listing all layouts."""
        result = await customization_service.list_layouts()

        assert isinstance(result, list)
        assert len(result) >= 3  # Should have at least default layouts
        for layout in result:
            assert isinstance(layout, Layout)

    @pytest.mark.asyncio
    async def test_list_layouts_exclude_system(self, customization_service):
        """Test listing layouts excluding system defaults."""
        result = await customization_service.list_layouts(include_system=False)

        assert isinstance(result, list)
        for layout in result:
            assert layout.is_system_default is False

    @pytest.mark.asyncio
    async def test_list_layouts_exclude_custom(self, customization_service):
        """Test listing layouts excluding custom layouts."""
        # Create a custom layout first
        await customization_service.create_layout(
            name="Custom Layout", layout_type=LayoutType.CUSTOM,
            sidebar_width=200, content_spacing=10, card_border_radius=4, font_size="small"
        )

        result = await customization_service.list_layouts(include_custom=False)

        assert isinstance(result, list)
        for layout in result:
            assert layout.is_custom is False

    @pytest.mark.asyncio
    async def test_get_user_preferences_creates_default(self, customization_service):
        """Test that getting non-existent user preferences creates defaults."""
        result = await customization_service.get_user_preferences("newuser123")

        assert result is not None
        assert isinstance(result, UserPreferences)
        assert result.user_id == "newuser123"
        assert result.theme_id == "theme_light"  # Default theme
        assert result.layout_id == "layout_default"  # Default layout
        assert result.language == "en-US"
        assert result.notifications_enabled is True
        assert result.auto_save_enabled is True
        assert isinstance(result.recent_colors, list)
        assert isinstance(result.favorite_themes, list)
        assert len(result.recent_colors) > 0
        assert len(result.favorite_themes) > 0

    @pytest.mark.asyncio
    async def test_get_user_preferences_existing(self, customization_service):
        """Test getting existing user preferences."""
        # First get/create preferences
        first_prefs = await customization_service.get_user_preferences("existinguser")

        # Update some preferences
        await customization_service.update_user_preferences(
            "existinguser",
            theme_id="theme_dark",
            notifications_enabled=False
        )

        # Get again
        result = await customization_service.get_user_preferences("existinguser")

        assert result is not None
        assert result.user_id == "existinguser"
        assert result.theme_id == "theme_dark"  # Updated value
        assert result.notifications_enabled is False  # Updated value
        # Should be same instance
        assert result is first_prefs

    @pytest.mark.asyncio
    async def test_update_user_preferences_success(self, customization_service):
        """Test updating user preferences successfully."""
        # First ensure preferences exist
        await customization_service.get_user_preferences("prefuser")

        # Update preferences
        result = await customization_service.update_user_preferences(
            user_id="prefuser",
            theme_id="theme_dark",
            layout_id="layout_compact",
            language="es-ES",
            timezone="Europe/Madrid",
            notifications_enabled=False,
            auto_save_enabled=False,
            compact_mode=True,
            sidebar_collapsed=True,
            recent_colors=["#EF4444", "#F97316", "#EAB308"],
            favorite_themes=["theme_dark", "theme_green_nature"],
            custom_css=".custom { color: red; }"
        )

        assert result is not None
        assert isinstance(result, UserPreferences)
        assert result.theme_id == "theme_dark"
        assert result.layout_id == "layout_compact"
        assert result.language == "es-ES"
        assert result.timezone == "Europe/Madrid"
        assert result.notifications_enabled is False
        assert result.auto_save_enabled is False
        assert result.compact_mode is True
        assert result.sidebar_collapsed is True
        assert result.recent_colors == ["#EF4444", "#F97316", "#EAB308"]
        assert result.favorite_themes == ["theme_dark", "theme_green_nature"]
        assert result.custom_css == ".custom { color: red; }"
        assert result.updated_at != result.created_at

    @pytest.mark.asyncio
    async def test_create_custom_component_success(self, customization_service):
        """Test creating custom component successfully."""
        result = await customization_service.create_custom_component(
            name="Custom Button",
            component_type="button",
            html_template='<button class="custom-btn">{{text}}</button>',
            css_styles='.custom-btn { background: blue; color: white; }',
            javascript_code='console.log("Custom button loaded");',
            created_by="dev123"
        )

        assert result is not None
        assert isinstance(result, CustomComponent)
        assert result.name == "Custom Button"
        assert result.type == "button"
        assert result.html_template == '<button class="custom-btn">{{text}}</button>'
        assert result.css_styles == '.custom-btn { background: blue; color: white; }'
        assert result.javascript_code == 'console.log("Custom button loaded");'
        assert result.created_by == "dev123"
        assert result.is_active is True
        assert len(result.id) > 0
        assert result.created_at is not None
        assert result.updated_at is not None
        # Should be stored in custom_components dict
        assert result.id in customization_service.custom_components

    @pytest.mark.asyncio
    async def test_get_custom_component_success(self, customization_service):
        """Test getting existing custom component."""
        # Create component first
        component = await customization_service.create_custom_component(
            name="Test Component", component_type="div",
            html_template="<div>Test</div>", css_styles="", javascript_code="", created_by="test"
        )

        result = await customization_service.get_custom_component(component.id)

        assert result is not None
        assert result.id == component.id
        assert result.name == "Test Component"

    @pytest.mark.asyncio
    async def test_get_custom_component_not_found(self, customization_service):
        """Test getting non-existent custom component."""
        result = await customization_service.get_custom_component("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_list_custom_components_all_active(self, customization_service):
        """Test listing custom components (active only by default)."""
        # Create active component
        active_component = await customization_service.create_custom_component(
            name="Active Component", component_type="span",
            html_template="<span>Active</span>", css_styles="", javascript_code="", created_by="test"
        )

        # Create inactive component
        inactive_component = await customization_service.create_custom_component(
            name="Inactive Component", component_type="p",
            html_template="<p>Inactive</p>", css_styles="", javascript_code="", created_by="test"
        )
        # Make it inactive
        await customization_service.toggle_component_status(inactive_component.id, False)

        result = await customization_service.list_custom_components()

        assert isinstance(result, list)
        # Should only include active components
        component_ids = [c.id for c in result]
        assert active_component.id in component_ids
        assert inactive_component.id not in component_ids

    @pytest.mark.asyncio
    async def test_list_custom_components_all(self, customization_service):
        """Test listing all custom components including inactive."""
        # Create some components
        await customization_service.create_custom_component(
            name="Comp1", component_type="div", html_template="", css_styles="", javascript_code="", created_by="test"
        )
        comp2 = await customization_service.create_custom_component(
            name="Comp2", component_type="span", html_template="", css_styles="", javascript_code="", created_by="test"
        )
        # Deactivate one
        await customization_service.toggle_component_status(comp2.id, False)

        # Get all components (both active and inactive)
        all_components = list(customization_service.custom_components.values())

        assert isinstance(all_components, list)
        assert len(all_components) >= 2

    @pytest.mark.asyncio
    async def test_toggle_component_status_success(self, customization_service):
        """Test toggling component status successfully."""
        # Create component (active by default)
        component = await customization_service.create_custom_component(
            name="Toggle Test", component_type="button",
            html_template="", css_styles="", javascript_code="", created_by="test"
        )

        # Verify it's active
        assert component.is_active is True

        # Deactivate it
        result = await customization_service.toggle_component_status(component.id, False)

        assert result is True
        assert component.is_active is False
        assert component.updated_at != component.created_at

        # Activate it again
        result = await customization_service.toggle_component_status(component.id, True)

        assert result is True
        assert component.is_active is True

    @pytest.mark.asyncio
    async def test_toggle_component_status_not_found(self, customization_service):
        """Test toggling status of non-existent component."""
        result = await customization_service.toggle_component_status("nonexistent", True)
        assert result is False

    @pytest.mark.asyncio
    async def test_get_system_defaults(self, customization_service):
        """Test getting system default configurations."""
        result = await customization_service.get_system_defaults()

        assert isinstance(result, dict)
        assert "default_theme" in result
        assert "default_layout" in result
        assert "available_modes" in result
        assert "available_layout_types" in result
        assert "color_schemes" in result

        # Check default theme
        default_theme = result["default_theme"]
        assert default_theme is not None
        assert "Light Theme" in str(default_theme) or "theme_light" in str(default_theme)

        # Check default layout
        default_layout = result["default_layout"]
        assert default_layout is not None
        assert "Default Layout" in str(default_layout) or "layout_default" in str(default_layout)

        # Check available modes
        modes = result["available_modes"]
        assert isinstance(modes, list)
        assert "light" in modes
        assert "dark" in modes
        assert "system" in modes

        # Check available layout types
        layout_types = result["available_layout_types"]
        assert isinstance(layout_types, list)
        assert "default" in layout_types
        assert "compact" in layout_types
        assert "spacious" in layout_types

        # Check color schemes
        color_schemes = result["color_schemes"]
        assert isinstance(color_schemes, list)
        assert "blue" in color_schemes
        assert "green" in color_schemes
        assert "purple" in color_schemes

    @pytest.mark.asyncio
    async def test_export_theme_success(self, customization_service):
        """Test exporting theme successfully."""
        result = await customization_service.export_theme("theme_light")

        assert isinstance(result, dict)
        assert "theme" in result
        assert "exported_at" in result
        assert "version" in result

        theme_data = result["theme"]
        assert isinstance(theme_data, dict)
        assert theme_data["id"] == "theme_light"
        assert theme_data["name"] == "Light Theme"
        assert "primary_color" in theme_data
        assert "background_color" in theme_data

    @pytest.mark.asyncio
    async def test_export_theme_not_found(self, customization_service):
        """Test exporting non-existent theme."""
        with pytest.raises(ValueError) as exc_info:
            await customization_service.export_theme("nonexistent")

        assert "Theme nonexistent not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_import_theme_success(self, customization_service):
        """Test importing theme successfully."""
        theme_data = {
            "theme": {
                "name": "Imported Ocean Theme",
                "mode": "dark",
                "primary_color": "#0EA5E9",
                "secondary_color": "#64748B",
                "accent_color": "#06B6D4",
                "background_color": "#0F172A",
                "text_color": "#F1F5F9",
                "border_color": "#334155"
            },
            "exported_at": "2024-01-01T00:00:00Z",
            "version": "1.0"
        }

        result = await customization_service.import_theme(theme_data, "importer123")

        assert result is not None
        assert isinstance(result, Theme)
        assert result.name == "Imported Ocean Theme"
        assert result.mode == ThemeMode.DARK
        assert result.primary_color == "#0EA5E9"
        assert result.background_color == "#0F172A"
        assert result.created_by == "importer123"
        assert result.is_custom is True

    @pytest.mark.asyncio
    async def test_import_theme_minimal_data(self, customization_service):
        """Test importing theme with minimal data (uses defaults)."""
        theme_data = {
            "theme": {
                "name": "Minimal Import"
            }
        }

        result = await customization_service.import_theme(theme_data, "importer456")

        assert result is not None
        assert isinstance(result, Theme)
        assert result.name == "Minimal Import"
        # Should use default values for missing fields
        assert result.mode == ThemeMode.LIGHT  # Default
        assert result.primary_color == "#3B82F6"  # Default

    def test_theme_post_init(self):
        """Test Theme post-initialization."""
        # Without timestamps
        theme = Theme(
            id="test-theme", name="Test Theme", mode=ThemeMode.LIGHT,
            primary_color="#000", secondary_color="#111", accent_color="#222",
            background_color="#FFF", text_color="#000", border_color="#333"
        )
        assert len(theme.created_at) > 0
        assert len(theme.updated_at) > 0
        # Timestamps should be very close (within same second)
        assert theme.created_at[:19] == theme.updated_at[:19]

        # With timestamps provided
        custom_created = "2024-01-01T00:00:00Z"
        custom_updated = "2024-01-02T00:00:00Z"
        theme_with_times = Theme(
            id="test-theme-2", name="Test Theme 2", mode=ThemeMode.DARK,
            primary_color="#000", secondary_color="#111", accent_color="#222",
            background_color="#FFF", text_color="#000", border_color="#333",
            created_at=custom_created, updated_at=custom_updated
        )
        assert theme_with_times.created_at == custom_created
        assert theme_with_times.updated_at == custom_updated

    def test_layout_post_init(self):
        """Test Layout post-initialization."""
        # Without timestamps
        layout = Layout(
            id="test-layout", name="Test Layout", type=LayoutType.COMPACT,
            sidebar_width=200, content_spacing=10, card_border_radius=5, font_size="small"
        )
        assert len(layout.created_at) > 0
        assert len(layout.updated_at) > 0

        # With timestamps provided
        custom_created = "2024-01-01T00:00:00Z"
        layout_with_times = Layout(
            id="test-layout-2", name="Test Layout 2", type=LayoutType.DEFAULT,
            sidebar_width=300, content_spacing=20, card_border_radius=10, font_size="medium",
            created_at=custom_created
        )
        assert layout_with_times.created_at == custom_created

    def test_user_preferences_post_init(self):
        """Test UserPreferences post-initialization."""
        # Without timestamps
        prefs = UserPreferences(
            user_id="testuser", theme_id="theme_light", layout_id="layout_default",
            language="en-US", timezone="UTC", notifications_enabled=True,
            auto_save_enabled=True, keyboard_shortcuts_enabled=True,
            animations_enabled=True, compact_mode=False, sidebar_collapsed=False,
            recent_colors=["#000"], favorite_themes=["theme_light"]
        )
        assert len(prefs.created_at) > 0
        assert len(prefs.updated_at) > 0

        # With timestamps provided
        custom_created = "2024-01-01T00:00:00Z"
        prefs_with_times = UserPreferences(
            user_id="testuser2", theme_id="theme_dark", layout_id="layout_compact",
            language="es-ES", timezone="Europe/Madrid", notifications_enabled=False,
            auto_save_enabled=False, keyboard_shortcuts_enabled=False,
            animations_enabled=False, compact_mode=True, sidebar_collapsed=True,
            recent_colors=["#FFF"], favorite_themes=["theme_dark"],
            created_at=custom_created
        )
        assert prefs_with_times.created_at == custom_created

    def test_enum_values(self):
        """Test enum values are correctly defined."""
        # Test ThemeMode values
        assert ThemeMode.LIGHT.value == "light"
        assert ThemeMode.DARK.value == "dark"
        assert ThemeMode.SYSTEM.value == "system"
        assert ThemeMode.AUTO.value == "auto"

        # Test LayoutType values
        assert LayoutType.DEFAULT.value == "default"
        assert LayoutType.COMPACT.value == "compact"
        assert LayoutType.SPACIOUS.value == "spacious"
        assert LayoutType.CUSTOM.value == "custom"

        # Test ColorScheme values
        assert ColorScheme.BLUE.value == "blue"
        assert ColorScheme.GREEN.value == "green"
        assert ColorScheme.PURPLE.value == "purple"
        assert ColorScheme.ORANGE.value == "orange"
        assert ColorScheme.RED.value == "red"
        assert ColorScheme.CUSTOM.value == "custom"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
