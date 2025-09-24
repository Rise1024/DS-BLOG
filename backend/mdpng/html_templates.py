#!/usr/bin/env python3

class BaseHtmlTemplate:
    """基础HTML模板类，定义基本的HTML结构和样式"""
    def __init__(self):
        self.font_import = "@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');"
        self.font_family = "'JetBrains Mono', monospace"
        self.text_color = "#e6e6e6"
        self.background_color = "#a6b2bd"
        self.content_background = "#151718"
        self.link_color = "#ff6347"
        self.heading_color = "#7ec4ff"
        self.code_font_size = "28px"
        self.base_font_size = "28px"

class CoverTemplate(BaseHtmlTemplate):
    """封面页HTML模板"""
    def generate(self, content, config):
        # 根据主题类型选择不同的封面样式
        theme_layout = config['theme'].get('layout', 'carbon')
        if theme_layout == 'xiaohongshu':
            return self._generate_xiaohongshu_cover(content, config)
        elif theme_layout == 'notion':
            return self._generate_notion_cover(content, config)
        return self._generate_carbon_cover(content, config)

    def _generate_xiaohongshu_cover(self, content, config):
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                {config['theme']['font_import']}
                body {{
                    margin: 0;
                    padding: 0;
                    width: 100%;
                    height: 100vh;
                    background: {config['theme']['background']};
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    color: {config['theme']['text_color']};
                    font-family: {config['theme']['font_family']};
                }}
                .cover-container {{
                    background: {config['theme']['content_style']['background']};
                    border-radius: {config['theme']['content_style']['border_radius']};
                    padding: 60px;
                    box-shadow: {config['theme']['content_style']['box_shadow']};
                    text-align: center;
                    max-width: 800px;
                    width: 90%;
                }}
                .cover-title {{
                    font-size: 72px;
                    color: {config['theme']['heading_style']['color']};
                    border-bottom: {config['theme']['heading_style']['border_style']} {config['theme']['heading_style']['border_color']};
                    padding-bottom: 20px;
                    margin-bottom: 30px;
                }}
                .watermark {{
                    margin-top: 40px;
                    font-size: 24px;
                    opacity: 0.7;
                    transform: rotate(-15deg);
                }}
            </style>
        </head>
        <body>
            <div class="cover-container">
                <div class="cover-title">{content}</div>
                <div class="watermark">{config['theme']['watermark']}</div>
            </div>
        </body>
        </html>
        """

    def _generate_notion_cover(self, content, config):
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                {config['theme']['font_import']}
                body {{
                    margin: 0;
                    padding: 40px;
                    width: 100%;
                    height: 100vh;
                    background: {config['theme']['background']};
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    color: {config['theme']['text_color']};
                    font-family: {config['theme']['font_family']};
                }}
                .cover-container {{
                    max-width: {config['theme']['content_style']['max_width']};
                    width: 100%;
                    text-align: left;
                    padding: 60px;
                }}
                .cover-title {{
                    font-size: 84px;
                    font-weight: {config['theme']['heading_style']['font_weight']};
                    color: {config['theme']['heading_style']['color']};
                    line-height: 1.2;
                }}
                .watermark {{
                    margin-top: 40px;
                    font-size: 20px;
                    opacity: 0.5;
                }}
            </style>
        </head>
        <body>
            <div class="cover-container">
                <div class="cover-title">{content}</div>
                <div class="watermark">{config['theme']['watermark']}</div>
            </div>
        </body>
        </html>
        """

    def _generate_carbon_cover(self, content, config):
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                {config['theme']['font_import']}
                body {{
                    margin: 0;
                    padding: 50px;
                    width: 100%;
                    height: 100vh;
                    background: {config['theme']['background']};
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    color: {config['theme']['text_color']};
                    font-family: {config['theme']['font_family']};
                }}
                .cover-container {{
                    background: {self.content_background};
                    border-radius: {config['theme']['carbon_style']['border_radius']};
                    padding: {config['theme']['carbon_style']['padding']};
                    box-shadow: {config['theme']['carbon_style']['shadow']};
                    position: relative;
                    max-width: 900px;
                    width: 90%;
                }}
                .window-controls {{
                    position: absolute;
                    top: 12px;
                    left: 16px;
                    height: 12px;
                    width: 52px;
                    display: flex;
                    gap: 8px;
                }}
                .window-control {{
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                }}
                .window-control.close {{ background: #ff5f56; }}
                .window-control.minimize {{ background: #ffbd2e; }}
                .window-control.maximize {{ background: #27c93f; }}
                .cover-title {{
                    font-size: 76px;
                    text-align: center;
                    margin-top: 40px;
                    text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
                }}
                .watermark {{
                    text-align: center;
                    margin-top: 40px;
                    font-size: 24px;
                    opacity: 0.5;
                }}
            </style>
        </head>
        <body>
            <div class="cover-container">
                <div class="window-controls">
                    <div class="window-control close"></div>
                    <div class="window-control minimize"></div>
                    <div class="window-control maximize"></div>
                </div>
                <div class="cover-title">{content}</div>
                <div class="watermark">{config['theme']['watermark']}</div>
            </div>
        </body>
        </html>
        """

class ContentTemplate(BaseHtmlTemplate):
    """内容页HTML模板"""
    def generate(self, html_content, config, css_code):
        # 根据主题类型选择不同的样式
        theme_layout = config['theme'].get('layout', 'carbon')
        if theme_layout == 'xiaohongshu':
            return self._generate_xiaohongshu(html_content, config, css_code)
        elif theme_layout == 'notion':
            return self._generate_notion(html_content, config, css_code)
        return self._generate_carbon(html_content, config, css_code)

    def _generate_xiaohongshu(self, html_content, config, css_code):
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                {config['theme']['font_import']}
                body {{
                    margin: 0;
                    padding: 50px;
                    min-height: 100vh;
                    width: 100%;
                    background: {self.background_color};
                    color: {config['theme']['text_color']};
                    font-family: {config['theme']['font_family']};
                    line-height: 1.6;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    font-size: {self.base_font_size};
                }}
                
                .content {{
                    background: {self.content_background};
                    border-radius: 25px;
                    padding: 40px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                    position: relative;
                    backdrop-filter: blur(10px);
                    max-width: 980px;
                    width: 100%;
                    word-wrap: break-word;
                    overflow-wrap: break-word;
                    font-size: 30px;
                }}
                
                /* 链接高亮 */
                a {{
                    color: {self.link_color};
                    text-decoration: none;
                    border-bottom: 1px dashed rgba(126, 196, 255, 0.4);
                    transition: all 0.3s ease;
                }}
                
                a:hover {{
                    border-bottom-color: {self.link_color};
                }}
                
                /* 代码块高亮 */
                {css_code}
                
                /* 标题样式增强 */
                h1, h2 {{
                    font-size: 62px !important;
                }}
                
                h3 {{
                    font-size: 42px !important;
                }}
                
                h4 {{
                    font-size: 38px !important;
                }}
                
                h5 {{
                    font-size: 30px !important;
                }}
                
                h6 {{
                    font-size: 28px !important;
                }}
                
                /* Carbon-style window controls */
                .window-controls {{
                    position: absolute;
                    top: 12px;
                    left: 16px;
                    height: 12px;
                    width: 52px;
                    display: flex;
                    gap: 8px;
                }}
                
                .window-control {{
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                }}
                
                .window-control.close {{ background: #ff5f56; }}
                .window-control.minimize {{ background: #ffbd2e; }}
                .window-control.maximize {{ background: #27c93f; }}
                
                /* 小红书风格标题样式 */
                h1, h2 {{
                    color: {config['theme']['heading_style']['color']};
                    letter-spacing: 1px;
                    text-shadow: 0 2px 4px rgba(0,0,0,0.2);
                    text-align: center;
                    font-size: 42px !important;
                    border-bottom: 3px solid #3f72af;
                    padding-bottom: 15px;
                }}
                
                h3, h4, h5, h6 {{
                    color: {self.heading_color};
                    letter-spacing: 1px;
                    text-shadow: 0 2px 4px rgba(0,0,0,0.2);
                    text-align: left;
                }}
                
                h2 {{
                    font-size: 42px !important;
                    border-bottom: 2px solid #3f72af;
                    padding-bottom: 12px;
                }}
                
                h3 {{
                    font-size: 36px !important;
                    color: #6db4ff;
                }}
                
                h4 {{
                    font-size: 30px !important;
                    color: #5ba8ff;
                }}
                
                h5 {{
                    font-size: 20px !important;
                    color: #4a9eff;
                }}
                
                h6 {{
                    font-size: 18px !important;
                    color: #3994ff;
                }}
                
                /* 标题悬停效果 */
                h1:hover, h2:hover, h3:hover, h4:hover, h5:hover, h6:hover {{
                    transform: translateX(5px);
                    transition: transform 0.3s ease;
                }}

                /* Decorative elements */
                .content::before {{
                    content: '';
                    position: absolute;
                    top: -10px;
                    left: -10px;
                    right: -10px;
                    bottom: -10px;
                    border: 2px solid rgba(255, 255, 255, 0.1);
                    border-radius: 30px;
                    z-index: -1;
                }}

                /* Watermark style */
                .watermark {{
                    position: absolute;
                    bottom: 10px;
                    right: 20px;
                    font-size: 14px;
                    opacity: 0.5;
                    color: {self.heading_color};
                    transform: rotate(-15deg);
                }}

                /* Enhanced typography */
                blockquote {{
                    border-left: 4px solid #3f72af;
                    margin: 20px 0;
                    padding: 15px 30px;
                    background: rgba(255, 255, 255, 0.03);
                    color: #a8d0ff;
                }}

                table {{
                    border-collapse: collapse;
                    margin: 25px 0;
                    box-shadow: 0 0 20px rgba(0,0,0,0.15);
                    width: 100%;
                }}

                th, td {{
                    padding: 15px;
                    border: 1px solid #364f6b;
                    text-align: left;
                }}

                th {{
                    background-color: #16213e;
                    color: {self.heading_color};
                }}

                tr:nth-child(even) {{
                    background-color: rgba(255, 255, 255, 0.03);
                }}

                /* Add decorative quote marks for blockquotes */
                blockquote::before {{
                    content: '"';
                    font-size: 60px;
                    color: rgba(126, 196, 255, 0.2);
                    position: absolute;
                    left: 10px;
                    top: -10px;
                }}
                
                /* 小红书风格代码块 */
                pre {{ 
                    padding: {config['theme']['carbon_style']['padding']};
                    padding-top: 56px;
                    border-radius: {config['theme']['carbon_style']['border_radius']};
                    background: #1a1b1f;
                    box-shadow: {config['theme']['carbon_style']['shadow']};
                    margin: 2em 0;
                    font-size: 24px !important;
                    position: relative;
                    overflow: hidden;
                    white-space: pre-wrap;
                    word-wrap: break-word;
                }}

                p {{
                    white-space: pre-wrap;
                    word-wrap: break-word;
                }}
                
                .highlight {{
                    padding: 0;
                    margin: 0;
                    background: transparent;
                }}

                code {{
                    font-family: {self.font_family};
                    font-size: {self.code_font_size};
                    line-height: 1.5;
                    color: #339966;
                }}
                
                /* 小红书风格图片样式 */
                img {{
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                    max-width: 100%;
                    height: auto;
                }}
            </style>
        </head>
        <body>
            <div class="window-controls">
                <div class="window-control close"></div>
                <div class="window-control minimize"></div>
                <div class="window-control maximize"></div>
            </div>
            <div class="content">
                <div class="watermark">{config['theme']['watermark']}</div>
                {html_content}
            </div>
            <script>
                // 为所有代码块添加窗口控制按钮
                document.querySelectorAll('pre').forEach(pre => {{
                    const wrapper = document.createElement('div');
                    wrapper.className = 'window-controls';
                    wrapper.innerHTML = `
                        <div class="window-control close"></div>
                        <div class="window-control minimize"></div>
                        <div class="window-control maximize"></div>
                    `;
                    pre.insertBefore(wrapper, pre.firstChild);
                }});
            </script>
        </body>
        </html>
        """

    def _generate_notion(self, html_content, config, css_code):
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                {config['theme']['font_import']}
                body {{
                    margin: 0;
                    padding: 0;
                    background: {config['theme']['background']};
                    color: {config['theme']['text_color']};
                    font-family: {config['theme']['font_family']};
                    line-height: {config['theme']['content_style']['line_height']};
                    font-size: {self.base_font_size};
                }}
                
                .content {{
                    max-width: {config['theme']['content_style']['max_width']};
                    margin: {config['theme']['content_style']['margin']};
                    padding: {config['theme']['content_style']['padding']};
                    font-size: {self.base_font_size};
                }}
                
                h1, h2, h3, h4, h5, h6 {{
                    color: {config['theme']['heading_style']['color']};
                    font-weight: {config['theme']['heading_style']['font_weight']};
                    margin-top: {config['theme']['heading_style']['margin_top']};
                }}
                
                h1 {{ font-size: 48px; }}
                h2 {{ font-size: 40px; }}
                h3 {{ font-size: 32px; }}
                h4 {{ font-size: 28px; }}
                h5 {{ font-size: 24px; }}
                h6 {{ font-size: 20px; }}
                
                pre {{
                    background: {config['theme']['carbon_style']['background']};
                    padding: {config['theme']['carbon_style']['padding']};
                    border-radius: {config['theme']['carbon_style']['border_radius']};
                    box-shadow: {config['theme']['carbon_style']['shadow']};
                    font-size: {self.code_font_size};
                    overflow-x: auto;
                }}
                
                code {{
                    font-family: {config['theme']['font_family']};
                    font-size: {self.code_font_size};
                }}
                
                img {{
                    max-width: 100%;
                    border-radius: 4px;
                }}
                
                blockquote {{
                    margin: 1.5em 0;
                    padding-left: 1em;
                    border-left: 3px solid #ddd;
                    color: #666;
                }}
                
                a {{
                    color: #0066cc;
                    text-decoration: none;
                }}
                
                a:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <div class="content">
                {html_content}
            </div>
        </body>
        </html>
        """

    def _generate_carbon(self, html_content, config, css_code):
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                {config['theme']['font_import']}
                body {{
                    margin: 0;
                    padding: 50px;
                    min-height: 100vh;
                    width: 100%;
                    background: {self.background_color};
                    color: {config['theme']['text_color']};
                    font-family: {config['theme']['font_family']};
                    line-height: 1.6;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    font-size: {self.base_font_size};
                }}
                
                .content {{
                    background: {self.content_background};
                    border-radius: 15px;
                    padding: 40px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                    position: relative;
                    max-width: 980px;
                    width: 100%;
                    word-wrap: break-word;
                    overflow-wrap: break-word;
                }}
                
                /* 链接样式 */
                a {{
                    color: {self.link_color};
                    text-decoration: none;
                    border-bottom: 1px dashed rgba(255, 99, 71, 0.4);
                    transition: all 0.3s ease;
                }}
                
                a:hover {{
                    border-bottom-color: {self.link_color};
                }}
                
                /* 代码高亮 */
                {css_code}
                
                /* 标题样式 */
                h1, h2, h3, h4, h5, h6 {{
                    color: {self.heading_color};
                    letter-spacing: 0.5px;
                    text-shadow: 0 2px 4px rgba(0,0,0,0.2);
                }}
                
                h1 {{ font-size: 48px; }}
                h2 {{ font-size: 40px; }}
                h3 {{ font-size: 32px; }}
                h4 {{ font-size: 28px; }}
                h5 {{ font-size: 24px; }}
                h6 {{ font-size: 20px; }}
                
                /* 窗口控制按钮 */
                .window-controls {{
                    position: absolute;
                    top: 12px;
                    left: 16px;
                    height: 12px;
                    width: 52px;
                    display: flex;
                    gap: 8px;
                }}
                
                .window-control {{
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                }}
                
                .window-control.close {{ background: #ff5f56; }}
                .window-control.minimize {{ background: #ffbd2e; }}
                .window-control.maximize {{ background: #27c93f; }}
                
                /* 代码块样式 */
                pre {{
                    padding: {config['theme']['carbon_style']['padding']};
                    padding-top: 48px;
                    border-radius: {config['theme']['carbon_style']['border_radius']};
                    background: #1a1b1f;
                    box-shadow: {config['theme']['carbon_style']['shadow']};
                    margin: 2em 0;
                    font-size: {self.code_font_size};
                    position: relative;
                    overflow: hidden;
                }}
                
                code {{
                    font-family: {self.font_family};
                    font-size: {self.code_font_size};
                    line-height: 1.5;
                }}
                
                /* 其他元素样式 */
                blockquote {{
                    border-left: 4px solid {self.heading_color};
                    margin: 20px 0;
                    padding: 15px 30px;
                    background: rgba(126, 196, 255, 0.05);
                    color: #a8d0ff;
                }}
                
                table {{
                    border-collapse: collapse;
                    margin: 25px 0;
                    box-shadow: 0 0 20px rgba(0,0,0,0.15);
                    width: 100%;
                }}
                
                th, td {{
                    padding: 15px;
                    border: 1px solid #2d3748;
                    text-align: left;
                }}
                
                th {{
                    background-color: #1a202c;
                    color: {self.heading_color};
                }}
                
                tr:nth-child(even) {{
                    background-color: rgba(255, 255, 255, 0.03);
                }}
                
                img {{
                    max-width: 100%;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                }}
                
                /* 水印样式 */
                .watermark {{
                    position: absolute;
                    bottom: 10px;
                    right: 20px;
                    font-size: 14px;
                    opacity: 0.5;
                    color: {self.heading_color};
                    transform: rotate(-15deg);
                }}
            </style>
        </head>
        <body>
            <div class="window-controls">
                <div class="window-control close"></div>
                <div class="window-control minimize"></div>
                <div class="window-control maximize"></div>
            </div>
            <div class="content">
                <div class="watermark">{config['theme']['watermark']}</div>
                {html_content}
            </div>
            <script>
                // 为所有代码块添加窗口控制按钮
                document.querySelectorAll('pre').forEach(pre => {{
                    const wrapper = document.createElement('div');
                    wrapper.className = 'window-controls';
                    wrapper.innerHTML = `
                        <div class="window-control close"></div>
                        <div class="window-control minimize"></div>
                        <div class="window-control maximize"></div>
                    `;
                    pre.insertBefore(wrapper, pre.firstChild);
                }});
            </script>
        </body>
        </html>
        """