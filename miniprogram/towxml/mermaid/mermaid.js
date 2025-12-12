const app = getApp();

Component({
  options: {
    styleIsolation: 'shared'
  },
  properties: {
    data: {
      type: Object,
      value: {}
    }
  },
  data: {
    code: '',
    imageUrl: '',
    isLoading: true,
    error: ''
  },
  lifetimes: {
    attached: function() {
      const _ts = this;
      console.log('Mermaid 组件 attached, data:', this.data);
      
      let dataAttr = this.data.data && this.data.data.attrs;
      
      if (!dataAttr || !dataAttr.value) {
        console.warn('Mermaid 组件: 数据为空', dataAttr);
        _ts.setData({
          isLoading: false,
          error: 'Mermaid 代码为空'
        });
        return;
      }
      
      const code = decodeURIComponent(dataAttr.value);
      console.log('Mermaid 组件: 解析到代码，长度:', code.length);
      _ts.setData({ code });
      
      // 尝试从后端 API 获取渲染后的图片
      _ts.renderMermaid(code);
    }
  },
  methods: {
    // 渲染 Mermaid 图表
    renderMermaid: function(code) {
      const _ts = this;
      const serverUrl = app.globalData.serverUrl;
      
      console.log('Mermaid renderMermaid: serverUrl =', serverUrl);
      console.log('Mermaid renderMermaid: code length =', code.length);
      
      // 方案1: 尝试使用后端 API 将 mermaid 转为图片
      if (serverUrl) {
        const apiUrl = `${serverUrl}/api/v1/mermaid/render`;
        console.log('Mermaid: 请求 API:', apiUrl);
        
        wx.request({
          url: apiUrl,
          method: 'POST',
          header: {
            'Content-Type': 'application/json'
          },
          data: {
            code: code
          },
          success: (res) => {
            console.log('Mermaid API 响应:', res.statusCode, res.data);
            if (res.statusCode === 200 && res.data.success && res.data.data && res.data.data.imageUrl) {
              const imageUrl = res.data.data.imageUrl;
              console.log('Mermaid: 获取到图片 URL:', imageUrl.substring(0, 100) + '...');
              
              // 如果是 data URL，直接使用
              // 如果是普通 URL，也直接使用
              _ts.setData({
                imageUrl: imageUrl,
                isLoading: false,
                error: ''
              });
            } else {
              console.warn('Mermaid API 返回失败:', res.data);
              // API 失败，尝试使用在线服务
              _ts.tryOnlineService(code);
            }
          },
          fail: (err) => {
            console.error('Mermaid API 请求失败:', err);
            // API 失败，尝试使用在线服务
            _ts.tryOnlineService(code);
          }
        });
      } else {
        console.warn('Mermaid: serverUrl 未配置');
        // 没有配置 serverUrl，尝试使用在线服务
        _ts.tryOnlineService(code);
      }
    },
    
    // 尝试使用在线服务（mermaid.ink）
    // 注意：由于小程序网络限制，这个方案可能不可用
    // 建议使用后端 API
    tryOnlineService: function(code) {
      const _ts = this;
      // 直接使用备用方案，因为小程序可能无法直接访问外部服务
      _ts.fallbackToCode();
    },
    
    // 备用方案：显示代码
    fallbackToCode: function() {
      this.setData({
        isLoading: false,
        error: '',
        imageUrl: ''
      });
    },
    
    // 图片加载成功
    onImageLoad: function(e) {
      this.setData({
        isLoading: false
      });
    },
    
    // 图片加载失败
    onImageError: function(e) {
      this.setData({
        isLoading: false,
        error: '图片加载失败',
        imageUrl: ''
      });
    }
  }
});

