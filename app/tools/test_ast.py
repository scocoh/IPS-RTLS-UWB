# Name: test_ast.py
# Version: 0.1.0
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: ParcoRTLS backend script
# Location: /home/parcoadmin/parco_fastapi/app/tools
# Role: Backend
# Status: Active
# Dependent: TRUE

#!/usr/bin/env python3
import ast
import sys

print("🔍 Starting AST analysis...")

try:
    # Quick test to see the AST structure
    with open('routes/trigger.py', 'r') as f:
        content = f.read()
    
    print(f"📄 File read successfully, length: {len(content)} characters")
    
    tree = ast.parse(content)
    print("✅ AST parsed successfully")
    
    func_count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_count += 1
            print(f"\n🔧 Function #{func_count}: {node.name}")
            print(f"   Line: {node.lineno}")
            print(f"   Decorators: {len(node.decorator_list)}")
            
            for i, decorator in enumerate(node.decorator_list):
                print(f"  🎯 Decorator {i}: {type(decorator).__name__}")
                print(f"      AST dump: {ast.dump(decorator)}")
            
            docstring = ast.get_docstring(node)
            print(f"  📝 Has docstring: {docstring is not None}")
            if docstring:
                print(f"      Docstring preview: {docstring[:100]}...")
    
    print(f"\n📊 Total functions found: {func_count}")
    
except FileNotFoundError:
    print("❌ File routes/trigger.py not found")
except SyntaxError as e:
    print(f"❌ Syntax error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()