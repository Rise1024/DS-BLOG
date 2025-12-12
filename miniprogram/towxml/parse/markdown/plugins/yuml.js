const config = require('../../../config');
const mermaidChart = (code) => {
    return `<mermaid value="${encodeURIComponent(code)}"></mermaid>`;
}

module.exports = md => {
    const temp = md.renderer.rules.fence.bind(md.renderer.rules)
    md.renderer.rules.fence = (tokens, idx, options, env, slf) => {
        const token = tokens[idx]
        const code = token.content.trim();
        const info = token.info ? token.info.trim() : '';
        
        // 识别 mermaid 代码块
        if (info === 'mermaid') {
            return mermaidChart(code)
        }
        
        // 识别 yuml 代码块
        if (info === 'yuml') {
            return mermaidChart(code)
        }
        
        // 自动检测 mermaid 图表（通过代码内容判断）
        const firstLine = code.split(/\n/)[0].trim();
        if (firstLine === 'gantt' || 
            firstLine === 'sequenceDiagram' || 
            firstLine.match(/^graph (?:TB|BT|RL|LR|TD);?$/) ||
            firstLine.match(/^flowchart (?:TB|BT|RL|LR|TD);?$/) ||
            firstLine.match(/^classDiagram/) ||
            firstLine.match(/^stateDiagram/) ||
            firstLine.match(/^erDiagram/) ||
            firstLine.match(/^journey/) ||
            firstLine.match(/^gitgraph/)) {
            return mermaidChart(code)
        }
        
        return temp(tokens, idx, options, env, slf)
    }
};