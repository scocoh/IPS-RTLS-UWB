# Name: check_syntax.py
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

print("🔍 Checking for syntax issues...")

try:
    with open('routes/trigger.py', 'r') as f:
        lines = f.readlines()
    
    print(f"📄 File has {len(lines)} lines")
    
    # Look for problematic lines
    issues = []
    for i, line in enumerate(lines, 1):
        line_strip = line.strip()
        
        # Check for comments on decorator lines
        if line_strip.startswith('@router.') and '#' in line:
            issues.append(f"Line {i}: Comment on decorator line: {line.strip()}")
        
        # Check for other potential syntax issues
        if line_strip.startswith('@') and not line_strip.startswith('@router'):
            issues.append(f"Line {i}: Unexpected decorator: {line.strip()}")
    
    if issues:
        print(f"❌ Found {len(issues)} potential syntax issues:")
        for issue in issues[:10]:  # Show first 10
            print(f"   {issue}")
    else:
        print("✅ No obvious syntax issues found")
    
    # Try to parse just the first few functions
    print("\n🔍 Attempting to parse file...")
    with open('routes/trigger.py', 'r') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
        print("✅ File parses successfully")
        
        # Count nodes
        funcs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        print(f"📊 Found {len(funcs)} function definitions")
        
        if len(funcs) > 0:
            print(f"   First function: {funcs[0].name} at line {funcs[0].lineno}")
        
    except SyntaxError as e:
        print(f"❌ Syntax Error at line {e.lineno}: {e.text}")
        print(f"   {e.msg}")
        
        # Show context around the error
        if e.lineno and e.lineno <= len(lines):
            start = max(0, e.lineno - 3)
            end = min(len(lines), e.lineno + 2)
            print(f"\n📝 Context around line {e.lineno}:")
            for i in range(start, end):
                marker = ">>> " if i + 1 == e.lineno else "    "
                print(f"{marker}{i+1:4d}: {lines[i].rstrip()}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()