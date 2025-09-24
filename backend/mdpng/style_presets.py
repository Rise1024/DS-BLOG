#!/usr/bin/env python3

class BaseTheme:
    """基础主题类，定义主题的基本属性"""
    def __init__(self):
        self.name = "基础风格"
        self.theme = {
            "background": "#ffffff",
            "text_color": "#000000",
            "code_theme": "default",
            "font_family": "Arial, sans-serif",
            "font_import": "@import url('https://fonts.googleapis.com/css2?family=Arial:wght@400;700&display=swap');",
            "watermark": "Base Style",
            "decorative_elements": True,
            "carbon_style": {
                "padding": "40px",
                "border_radius": "3px",
                "shadow": "rgba(15, 15, 15, 0.1) 0px 0px 5px"
            }
        }

class CarbonTheme(BaseTheme):
    """Carbon风格主题"""
    def __init__(self):
        super().__init__()
        self.name = "Carbon风格"
        self.theme.update({
            "background": "#1a1b1f",
            "text_color": "#e6e6e6",
            "code_theme": "monokai",
            "font_family": "'JetBrains Mono', monospace",
            "font_import": "@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');",
            "watermark": "Carbon Style",
            "carbon_style": {
                "padding": "48px",
                "border_radius": "10px",
                "shadow": "rgba(0, 0, 0, 0.55) 0px 8px 24px"
            }
        })

class XiaohongshuTheme(BaseTheme):
    """小红书风格主题"""
    def __init__(self):
        super().__init__()
        self.name = "小红书风格"
        self.theme.update({
            "background": "#f5e6e8",
            "text_color": "#cfadb1",
            "code_theme": "friendly",
            "font_family": "'LXGW WenKai Screen', sans-serif",
            "font_import": "@import url('https://cdn.staticfile.org/lxgw-wenkai-screen-webfont/1.6.0/lxgwwenkaiscreen.css');",
            "watermark": "小红书笔记",
            "decorative_elements": True,
            "layout": "xiaohongshu",
            "heading_style": {
                "color": "#a78a92",
                "font_size": "48px",
                "border_style": "double",
                "border_color": "#d4b5bd"
            },
            "content_style": {
                "background": "#faf6f7",
                "border_radius": "25px",
                "padding": "40px",
                "box_shadow": "0 10px 30px rgba(167, 138, 146, 0.15)"
            },
            "carbon_style": {
                "padding": "32px",
                "border_radius": "20px",
                "shadow": "rgba(167, 138, 146, 0.2) 0px 8px 24px"
            }
        })

class NotionTheme(BaseTheme):
    """Notion风格主题"""
    def __init__(self):
        super().__init__()
        self.name = "Notion风格"
        self.theme.update({
            "background": "#ffffff",
            "text_color": "#37352f",
            "code_theme": "friendly",
            "font_family": "'Inter', sans-serif",
            "font_import": "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');",
            "watermark": "Notion Style",
            "decorative_elements": False,
            "layout": "notion",
            "heading_style": {
                "color": "#000000",
                "font_size": "40px",
                "font_weight": "600",
                "margin_top": "48px"
            },
            "content_style": {
                "background": "#ffffff",
                "max_width": "900px",
                "margin": "0 auto",
                "padding": "40px 96px",
                "line_height": "1.7"
            },
            "carbon_style": {
                "padding": "24px",
                "border_radius": "4px",
                "shadow": "rgba(15, 15, 15, 0.1) 0px 0px 5px",
                "background": "#f7f6f3"
            }
        })

# 创建样式预设字典
STYLE_PRESETS = {
    "carbon": {
        "name": CarbonTheme().name,
        "theme": CarbonTheme().theme
    },
    "xiaohongshu": {
        "name": XiaohongshuTheme().name,
        "theme": XiaohongshuTheme().theme
    },
    "notion": {
        "name": NotionTheme().name,
        "theme": NotionTheme().theme
    }
}