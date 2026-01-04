#!/usr/bin/env python3
"""翻訳システムのテスト"""

import sys

try:
    from translations import __, set_language, get_language
    
    print("✅ 翻訳モジュールが正常にインポートされました")
    
    # 日本語テスト
    set_language("ja")
    print(f"日本語: {__('window_title')}")
    print(f"日本語: {__('fetch_btn')}")
    
    # 英語テスト  
    set_language("en")
    print(f"English: {__('window_title')}")
    print(f"English: {__('fetch_btn')}")
    
    # フォーマットテスト
    set_language("ja")
    print(f"フォーマット: {__('fetched_success', count=8)}")
    
    set_language("en")
    print(f"Format: {__('fetched_success', count=8)}")
    
    print("\n✅ すべての翻訳テストが成功しました！")
    
except Exception as e:
    print(f"❌ エラー: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)
