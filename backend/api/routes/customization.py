"""
Customization API Routes

Provides REST endpoints for theming, layouts, and user customization features.
"""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.api.models import APIResponse
from backend.core.logging import get_logger
from backend.services.customization_service import (
    LayoutType,
    ThemeMode,
    customization_service,
)

router = APIRouter(prefix="/customization", tags=["Customization"])
logger = get_logger(__name__)


class ThemeCreate(BaseModel):
    """Theme creation request model."""
    name: str
    mode: str
    primary_color: str
    secondary_color: str
    accent_color: str
    background_color: str
    text_color: str
    border_color: str


class ThemeUpdate(BaseModel):
    """Theme update request model."""
    name: str | None = None
    primary_color: str | None = None
    secondary_color: str | None = None
    accent_color: str | None = None
    background_color: str | None = None
    text_color: str | None = None
    border_color: str | None = None


class LayoutCreate(BaseModel):
    """Layout creation request model."""
    name: str
    type: str
    sidebar_width: int
    content_spacing: int
    card_border_radius: int
    font_size: str


class UserPreferencesUpdate(BaseModel):
    """User preferences update request model."""
    theme_id: str | None = None
    layout_id: str | None = None
    language: str | None = None
    timezone: str | None = None
    notifications_enabled: bool | None = None
    auto_save_enabled: bool | None = None
    keyboard_shortcuts_enabled: bool | None = None
    animations_enabled: bool | None = None
    compact_mode: bool | None = None
    sidebar_collapsed: bool | None = None
    recent_colors: list[str] | None = None
    favorite_themes: list[str] | None = None
    custom_css: str | None = None


class CustomComponentCreate(BaseModel):
    """Custom component creation request model."""
    name: str
    type: str
    html_template: str
    css_styles: str
    javascript_code: str


@router.get("/themes/", response_model=APIResponse)
async def list_themes(include_system: bool = True, include_custom: bool = True):
    """
    List available themes.
    
    Args:
        include_system: Whether to include system default themes
        include_custom: Whether to include custom themes
        
    Returns:
        APIResponse with list of themes
    """
    try:
        themes = await customization_service.list_themes(include_system, include_custom)
        themes_data = [theme.__dict__ for theme in themes]

        return APIResponse(
            success=True,
            data=themes_data,
            message=f"Retrieved {len(themes_data)} themes"
        )
    except Exception as e:
        logger.error("Failed to list themes", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list themes: {str(e)}")


@router.post("/themes/", response_model=APIResponse)
async def create_theme(theme_data: ThemeCreate):
    """
    Create a new custom theme.
    
    Args:
        theme_data: Theme creation data
        
    Returns:
        APIResponse with created theme
    """
    try:
        # For demo purposes, using a fixed user ID
        created_by = "user_1"

        theme = await customization_service.create_theme(
            name=theme_data.name,
            mode=ThemeMode(theme_data.mode),
            primary_color=theme_data.primary_color,
            secondary_color=theme_data.secondary_color,
            accent_color=theme_data.accent_color,
            background_color=theme_data.background_color,
            text_color=theme_data.text_color,
            border_color=theme_data.border_color,
            created_by=created_by
        )

        return APIResponse(
            success=True,
            data=theme.__dict__,
            message=f"Theme '{theme.name}' created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Failed to create theme", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create theme: {str(e)}")


@router.get("/themes/{theme_id}", response_model=APIResponse)
async def get_theme(theme_id: str):
    """
    Get a specific theme.
    
    Args:
        theme_id: ID of the theme
        
    Returns:
        APIResponse with theme data
    """
    try:
        theme = await customization_service.get_theme(theme_id)

        if not theme:
            raise HTTPException(status_code=404, detail="Theme not found")

        return APIResponse(
            success=True,
            data=theme.__dict__,
            message=f"Retrieved theme '{theme.name}'"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get theme", error=str(e), theme_id=theme_id)
        raise HTTPException(status_code=500, detail=f"Failed to get theme: {str(e)}")


@router.put("/themes/{theme_id}", response_model=APIResponse)
async def update_theme(theme_id: str, update_data: ThemeUpdate):
    """
    Update an existing theme.
    
    Args:
        theme_id: ID of the theme to update
        update_data: Theme update data
        
    Returns:
        APIResponse with updated theme
    """
    try:
        updates = update_data.dict(exclude_unset=True)
        theme = await customization_service.update_theme(theme_id, **updates)

        return APIResponse(
            success=True,
            data=theme.__dict__,
            message=f"Theme '{theme.name}' updated successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Failed to update theme", error=str(e), theme_id=theme_id)
        raise HTTPException(status_code=500, detail=f"Failed to update theme: {str(e)}")


@router.delete("/themes/{theme_id}", response_model=APIResponse)
async def delete_theme(theme_id: str):
    """
    Delete a custom theme.
    
    Args:
        theme_id: ID of the theme to delete
        
    Returns:
        APIResponse confirming deletion
    """
    try:
        success = await customization_service.delete_theme(theme_id)

        if success:
            return APIResponse(
                success=True,
                message="Theme deleted successfully"
            )
        else:
            raise HTTPException(status_code=404, detail="Theme not found")

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Failed to delete theme", error=str(e), theme_id=theme_id)
        raise HTTPException(status_code=500, detail=f"Failed to delete theme: {str(e)}")


@router.get("/layouts/", response_model=APIResponse)
async def list_layouts(include_system: bool = True, include_custom: bool = True):
    """
    List available layouts.
    
    Args:
        include_system: Whether to include system default layouts
        include_custom: Whether to include custom layouts
        
    Returns:
        APIResponse with list of layouts
    """
    try:
        layouts = await customization_service.list_layouts(include_system, include_custom)
        layouts_data = [layout.__dict__ for layout in layouts]

        return APIResponse(
            success=True,
            data=layouts_data,
            message=f"Retrieved {len(layouts_data)} layouts"
        )
    except Exception as e:
        logger.error("Failed to list layouts", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list layouts: {str(e)}")


@router.post("/layouts/", response_model=APIResponse)
async def create_layout(layout_data: LayoutCreate):
    """
    Create a new custom layout.
    
    Args:
        layout_data: Layout creation data
        
    Returns:
        APIResponse with created layout
    """
    try:
        # For demo purposes, using a fixed user ID
        created_by = "user_1"

        layout = await customization_service.create_layout(
            name=layout_data.name,
            layout_type=LayoutType(layout_data.type),
            sidebar_width=layout_data.sidebar_width,
            content_spacing=layout_data.content_spacing,
            card_border_radius=layout_data.card_border_radius,
            font_size=layout_data.font_size,
            created_by=created_by
        )

        return APIResponse(
            success=True,
            data=layout.__dict__,
            message=f"Layout '{layout.name}' created successfully"
        )
    except Exception as e:
        logger.error("Failed to create layout", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create layout: {str(e)}")


@router.get("/layouts/{layout_id}", response_model=APIResponse)
async def get_layout(layout_id: str):
    """
    Get a specific layout.
    
    Args:
        layout_id: ID of the layout
        
    Returns:
        APIResponse with layout data
    """
    try:
        layout = await customization_service.get_layout(layout_id)

        if not layout:
            raise HTTPException(status_code=404, detail="Layout not found")

        return APIResponse(
            success=True,
            data=layout.__dict__,
            message=f"Retrieved layout '{layout.name}'"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get layout", error=str(e), layout_id=layout_id)
        raise HTTPException(status_code=500, detail=f"Failed to get layout: {str(e)}")


@router.get("/preferences/", response_model=APIResponse)
async def get_user_preferences():
    """
    Get current user's preferences.
    
    Returns:
        APIResponse with user preferences
    """
    try:
        # For demo purposes, using a fixed user ID
        user_id = "user_1"

        preferences = await customization_service.get_user_preferences(user_id)

        return APIResponse(
            success=True,
            data=preferences.__dict__,
            message="Retrieved user preferences"
        )
    except Exception as e:
        logger.error("Failed to get user preferences", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get user preferences: {str(e)}")


@router.put("/preferences/", response_model=APIResponse)
async def update_user_preferences(update_data: UserPreferencesUpdate):
    """
    Update user preferences.
    
    Args:
        update_data: Preferences update data
        
    Returns:
        APIResponse with updated preferences
    """
    try:
        # For demo purposes, using a fixed user ID
        user_id = "user_1"

        updates = update_data.dict(exclude_unset=True)
        preferences = await customization_service.update_user_preferences(user_id, **updates)

        return APIResponse(
            success=True,
            data=preferences.__dict__,
            message="User preferences updated successfully"
        )
    except Exception as e:
        logger.error("Failed to update user preferences", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to update user preferences: {str(e)}")


@router.get("/defaults", response_model=APIResponse)
async def get_system_defaults():
    """
    Get system default configurations.
    
    Returns:
        APIResponse with system defaults
    """
    try:
        defaults = await customization_service.get_system_defaults()

        return APIResponse(
            success=True,
            data=defaults,
            message="Retrieved system defaults"
        )
    except Exception as e:
        logger.error("Failed to get system defaults", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get system defaults: {str(e)}")


@router.post("/themes/{theme_id}/export", response_model=APIResponse)
async def export_theme(theme_id: str):
    """
    Export theme configuration as JSON.
    
    Args:
        theme_id: ID of the theme to export
        
    Returns:
        APIResponse with exported theme data
    """
    try:
        export_data = await customization_service.export_theme(theme_id)

        return APIResponse(
            success=True,
            data=export_data,
            message="Theme exported successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Failed to export theme", error=str(e), theme_id=theme_id)
        raise HTTPException(status_code=500, detail=f"Failed to export theme: {str(e)}")


@router.post("/themes/import", response_model=APIResponse)
async def import_theme(theme_data: dict[str, Any]):
    """
    Import theme configuration from JSON.
    
    Args:
        theme_data: Theme data to import
        
    Returns:
        APIResponse with imported theme
    """
    try:
        # For demo purposes, using a fixed user ID
        created_by = "user_1"

        theme = await customization_service.import_theme(theme_data, created_by)

        return APIResponse(
            success=True,
            data=theme.__dict__,
            message=f"Theme '{theme.name}' imported successfully"
        )
    except Exception as e:
        logger.error("Failed to import theme", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to import theme: {str(e)}")


@router.post("/components/", response_model=APIResponse)
async def create_custom_component(component_data: CustomComponentCreate):
    """
    Create a new custom UI component.
    
    Args:
        component_data: Component creation data
        
    Returns:
        APIResponse with created component
    """
    try:
        # For demo purposes, using a fixed user ID
        created_by = "user_1"

        component = await customization_service.create_custom_component(
            name=component_data.name,
            component_type=component_data.type,
            html_template=component_data.html_template,
            css_styles=component_data.css_styles,
            javascript_code=component_data.javascript_code,
            created_by=created_by
        )

        component_dict = component.__dict__
        del component_dict['html_template']  # Don't expose raw HTML in response
        del component_dict['css_styles']     # Don't expose raw CSS
        del component_dict['javascript_code'] # Don't expose raw JS

        return APIResponse(
            success=True,
            data=component_dict,
            message=f"Custom component '{component.name}' created successfully"
        )
    except Exception as e:
        logger.error("Failed to create custom component", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create custom component: {str(e)}")


@router.get("/components/", response_model=APIResponse)
async def list_custom_components(active_only: bool = True):
    """
    List custom components.
    
    Args:
        active_only: Whether to return only active components
        
    Returns:
        APIResponse with list of components
    """
    try:
        components = await customization_service.list_custom_components(active_only)
        components_data = []

        for component in components:
            component_dict = component.__dict__.copy()
            del component_dict['html_template']  # Don't expose raw HTML
            del component_dict['css_styles']     # Don't expose raw CSS
            del component_dict['javascript_code'] # Don't expose raw JS
            components_data.append(component_dict)

        return APIResponse(
            success=True,
            data=components_data,
            message=f"Retrieved {len(components_data)} custom components"
        )
    except Exception as e:
        logger.error("Failed to list custom components", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list custom components: {str(e)}")


@router.get("/components/{component_id}", response_model=APIResponse)
async def get_custom_component(component_id: str):
    """
    Get a specific custom component.
    
    Args:
        component_id: ID of the component
        
    Returns:
        APIResponse with component data
    """
    try:
        component = await customization_service.get_custom_component(component_id)

        if not component:
            raise HTTPException(status_code=404, detail="Component not found")

        component_dict = component.__dict__.copy()
        del component_dict['html_template']  # Don't expose raw HTML
        del component_dict['css_styles']     # Don't expose raw CSS
        del component_dict['javascript_code'] # Don't expose raw JS

        return APIResponse(
            success=True,
            data=component_dict,
            message=f"Retrieved component '{component.name}'"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get custom component", error=str(e), component_id=component_id)
        raise HTTPException(status_code=500, detail=f"Failed to get custom component: {str(e)}")


@router.post("/components/{component_id}/toggle", response_model=APIResponse)
async def toggle_component_status(component_id: str, active: bool):
    """
    Toggle custom component active status.
    
    Args:
        component_id: ID of the component
        active: Desired active status
        
    Returns:
        APIResponse confirming status change
    """
    try:
        success = await customization_service.toggle_component_status(component_id, active)

        if success:
            status = "activated" if active else "deactivated"
            return APIResponse(
                success=True,
                message=f"Component {status} successfully"
            )
        else:
            raise HTTPException(status_code=404, detail="Component not found")

    except Exception as e:
        logger.error("Failed to toggle component status", error=str(e), component_id=component_id)
        raise HTTPException(status_code=500, detail=f"Failed to toggle component status: {str(e)}")


@router.get("/preview/theme/{theme_id}", response_model=APIResponse)
async def preview_theme(theme_id: str):
    """
    Get theme preview data for live preview.
    
    Args:
        theme_id: ID of the theme to preview
        
    Returns:
        APIResponse with theme preview CSS variables
    """
    try:
        theme = await customization_service.get_theme(theme_id)

        if not theme:
            raise HTTPException(status_code=404, detail="Theme not found")

        # Generate CSS variables for preview
        css_variables = {
            "--primary-color": theme.primary_color,
            "--secondary-color": theme.secondary_color,
            "--accent-color": theme.accent_color,
            "--background-color": theme.background_color,
            "--text-color": theme.text_color,
            "--border-color": theme.border_color,
        }

        preview_data = {
            "theme": theme.__dict__,
            "css_variables": css_variables,
            "preview_html": "<div class='theme-preview'>Preview Content</div>"
        }

        return APIResponse(
            success=True,
            data=preview_data,
            message="Theme preview generated"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to generate theme preview", error=str(e), theme_id=theme_id)
        raise HTTPException(status_code=500, detail=f"Failed to generate theme preview: {str(e)}")


@router.get("/stats", response_model=APIResponse)
async def get_customization_stats():
    """
    Get customization system statistics.
    
    Returns:
        APIResponse with customization statistics
    """
    try:
        themes = await customization_service.list_themes()
        layouts = await customization_service.list_layouts()
        components = await customization_service.list_custom_components()
        user_prefs = len(customization_service.user_preferences)

        stats = {
            "total_themes": len(themes),
            "system_themes": len([t for t in themes if t.is_system_default]),
            "custom_themes": len([t for t in themes if t.is_custom]),
            "total_layouts": len(layouts),
            "system_layouts": len([l for l in layouts if l.is_system_default]),
            "custom_layouts": len([l for l in layouts if l.is_custom]),
            "total_components": len(components),
            "active_components": len([c for c in components if c.is_active]),
            "users_with_preferences": user_prefs
        }

        return APIResponse(
            success=True,
            data=stats,
            message="Retrieved customization statistics"
        )
    except Exception as e:
        logger.error("Failed to get customization stats", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get customization stats: {str(e)}")
