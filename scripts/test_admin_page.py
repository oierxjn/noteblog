#!/usr/bin/env python3
"""
测试 AI 摘要插件 admin 页面
"""
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

def test_admin_page():
    """测试 admin 页面"""
    app = create_app()
    
    with app.test_client() as client:
        print("=== 测试 AI 摘要插件 admin 页面 ===")
        
        try:
            response = client.get('/plugins/ai_summary/admin')
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ 页面访问成功")
                print(f"响应长度: {len(response.data)} 字节")
                
                # 检查响应内容
                content = response.data.decode('utf-8')
                if 'AI 摘要插件' in content:
                    print("✅ 页面内容正确")
                else:
                    print("❌ 页面内容异常")
                    
                if 'config.model' in content or 'GLM-4.5-Flash' in content:
                    print("✅ 配置数据正确渲染")
                else:
                    print("❌ 配置数据渲染异常")
                    
            else:
                print(f"❌ 页面访问失败: {response.status_code}")
                print(f"响应内容: {response.data.decode('utf-8')}")
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_admin_page()
