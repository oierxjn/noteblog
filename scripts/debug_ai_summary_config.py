#!/usr/bin/env python3
"""
调试 AI 摘要插件配置问题
"""
import os
import sys
import json

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.plugin import Plugin

def debug_ai_summary_config():
    """调试 AI 摘要插件配置"""
    app = create_app()
    
    with app.app_context():
        print("=== 调试 AI 摘要插件配置 ===")
        
        # 1. 检查插件是否存在
        plugin = Plugin.query.filter_by(name='ai_summary').first()
        if not plugin:
            print("❌ AI 摘要插件未找到")
            return
        
        print(f"✅ 找到插件: {plugin.name}")
        print(f"   - 显示名称: {plugin.display_name}")
        print(f"   - 版本: {plugin.version}")
        print(f"   - 是否激活: {plugin.is_active}")
        
        # 2. 检查配置数据
        print("\n=== 配置数据检查 ===")
        print(f"config_data (原始): {repr(plugin.config_data)}")
        
        if plugin.config_data:
            try:
                config = json.loads(plugin.config_data)
                print(f"✅ JSON 解析成功: {config}")
                print(f"   - 类型: {type(config)}")
                print(f"   - 键: {list(config.keys()) if isinstance(config, dict) else 'N/A'}")
                
                # 检查每个键的值
                if isinstance(config, dict):
                    for key, value in config.items():
                        print(f"   - {key}: {repr(value)} (类型: {type(value)})")
                        
            except json.JSONDecodeError as e:
                print(f"❌ JSON 解析失败: {e}")
        else:
            print("⚠️  config_data 为空")
        
        # 3. 检查 get_config() 方法
        print("\n=== get_config() 方法测试 ===")
        try:
            config = plugin.get_config()
            print(f"✅ get_config() 成功: {config}")
            print(f"   - 类型: {type(config)}")
            
            if isinstance(config, dict):
                for key, value in config.items():
                    print(f"   - {key}: {repr(value)} (类型: {type(value)})")
            else:
                print(f"   - ⚠️  返回的不是字典: {type(config)}")
                
        except Exception as e:
            print(f"❌ get_config() 失败: {e}")
            import traceback
            traceback.print_exc()
        
        # 4. 测试插件实例
        print("\n=== 插件实例测试 ===")
        try:
            from app.services.plugin_manager import plugin_manager
            plugin_instance = plugin_manager.get_plugin('ai_summary')
            
            if plugin_instance:
                print(f"✅ 插件实例存在: {plugin_instance}")
                
                # 测试 get_config 方法
                try:
                    instance_config = plugin_instance.get_config()
                    print(f"✅ 插件实例 get_config(): {instance_config}")
                    print(f"   - 类型: {type(instance_config)}")
                    
                    if isinstance(instance_config, dict):
                        for key, value in instance_config.items():
                            print(f"   - {key}: {repr(value)} (类型: {type(value)})")
                            
                except Exception as e:
                    print(f"❌ 插件实例 get_config() 失败: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("❌ 插件实例不存在")
                
        except Exception as e:
            print(f"❌ 获取插件实例失败: {e}")
            import traceback
            traceback.print_exc()
        
        # 5. 测试 admin_page 函数逻辑
        print("\n=== admin_page 逻辑测试 ===")
        try:
            from plugins.ai_summary import DEFAULT_ENDPOINT, DEFAULT_MODEL
            
            config = plugin.get_config() or {}
            print(f"config: {config}")
            
            base_defaults = {
                'model': DEFAULT_MODEL,
                'endpoint': DEFAULT_ENDPOINT,
                'temperature': 0.7,
                'max_tokens': 300,
            }
            print(f"base_defaults: {base_defaults}")
            
            # 测试原来的方式
            safe_config_old = {**base_defaults, **{k: v for k, v in config.items() if k != 'api_key'}}
            print(f"safe_config_old: {safe_config_old}")
            
            # 测试新的方式
            safe_config_new = {
                'model': config.get('model') or base_defaults['model'],
                'endpoint': config.get('endpoint') or base_defaults['endpoint'],
                'temperature': config.get('temperature') or base_defaults['temperature'],
                'max_tokens': config.get('max_tokens') or base_defaults['max_tokens'],
            }
            print(f"safe_config_new: {safe_config_new}")
            
            # 测试 JSON 序列化
            try:
                json_str = json.dumps(safe_config_new)
                print(f"✅ JSON 序列化成功: {json_str}")
            except Exception as e:
                print(f"❌ JSON 序列化失败: {e}")
                import traceback
                traceback.print_exc()
                
        except Exception as e:
            print(f"❌ admin_page 逻辑测试失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    debug_ai_summary_config()
