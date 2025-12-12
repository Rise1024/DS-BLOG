"""
Mermaid 图表渲染 API
使用本地 mermaid-cli 进行渲染
"""
from flask import Blueprint, request, jsonify
from config.config import logger
import base64
import subprocess
import tempfile
import os

mermaid_bp = Blueprint("mermaid", __name__, url_prefix="/api/v1/mermaid")


@mermaid_bp.route("/render", methods=["POST"])
def render_mermaid():
    """
    将 Mermaid 代码渲染为图片
    
    请求体:
    {
        "code": "graph TD\n    A-->B"
    }
    
    返回:
    {
        "success": true,
        "data": {
            "imageUrl": "data:image/svg+xml;base64,..."
        }
    }
    
    注意: 需要系统安装 mermaid-cli
    安装命令: npm install -g @mermaid-js/mermaid-cli
    """
    try:
        data = request.get_json()
        if not data or "code" not in data:
            return jsonify({"success": False, "error": "缺少 mermaid 代码"}), 400
        
        code = data.get("code", "").strip()
        if not code:
            return jsonify({"success": False, "error": "mermaid 代码为空"}), 400
        
        # 使用本地 mermaid-cli 渲染
        # 需要系统安装: npm install -g @mermaid-js/mermaid-cli
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False, encoding='utf-8') as f:
                f.write(code)
                temp_file = f.name
            
            output_file = None
            try:
                # 使用 mermaid-cli 渲染
                output_file = temp_file.replace('.mmd', '.svg')
                result = subprocess.run(
                    ['mmdc', '-i', temp_file, '-o', output_file],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0 and os.path.exists(output_file):
                    # 读取 SVG 文件
                    with open(output_file, 'r', encoding='utf-8') as f:
                        svg_content = f.read()
                    
                    # 转为 base64
                    svg_base64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
                    image_url = f"data:image/svg+xml;base64,{svg_base64}"
                    
                    logger.info("Mermaid 图表渲染成功")
                    return jsonify({
                        "success": True,
                        "data": {
                            "imageUrl": image_url,
                            "source": "local_mermaid_cli"
                        }
                    })
                else:
                    error_msg = result.stderr if result.stderr else "渲染失败"
                    logger.error(f"mermaid-cli 渲染失败: {error_msg}")
                    raise Exception(f"mermaid-cli 渲染失败: {error_msg}")
            finally:
                # 确保清理临时文件
                if os.path.exists(temp_file):
                    try:
                        os.unlink(temp_file)
                    except Exception as e:
                        logger.warning(f"清理临时文件失败: {e}")
                if output_file and os.path.exists(output_file):
                    try:
                        os.unlink(output_file)
                    except Exception as e:
                        logger.warning(f"清理输出文件失败: {e}")
        except FileNotFoundError:
            error_msg = "mermaid-cli 未安装，请运行: npm install -g @mermaid-js/mermaid-cli"
            logger.error(error_msg)
            return jsonify({
                "success": False,
                "error": error_msg
            }), 500
        except Exception as e:
            error_msg = f"使用本地 mermaid-cli 失败: {str(e)}"
            logger.error(error_msg)
            return jsonify({
                "success": False,
                "error": error_msg
            }), 500
        
    except Exception as e:
        logger.error(f"渲染 mermaid 图表时发生错误: {str(e)}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500

