# Name: ast_deep_dive.py
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

print("🔍 Deep AST analysis...")

with open('routes/trigger.py', 'r') as f:
    content = f.read()

tree = ast.parse(content)

print("📊 AST node types found:")
node_types = {}
for node in ast.walk(tree):
    node_type = type(node).__name__
    node_types[node_type] = node_types.get(node_type, 0) + 1

for node_type, count in sorted(node_types.items()):
    print(f"   {node_type}: {count}")

print("\n🔍 Looking for 'async def' in raw text:")
lines = content.split('\n')
async_def_lines = []
for i, line in enumerate(lines, 1):
    if 'async def' in line:
        async_def_lines.append((i, line.strip()))

print(f"Found {len(async_def_lines)} 'async def' lines:")
for line_num, line in async_def_lines[:5]:  # Show first 5
    print(f"   Line {line_num}: {line}")

print("\n🔍 Looking for '@router' in raw text:")
router_lines = []
for i, line in enumerate(lines, 1):
    if '@router' in line:
        router_lines.append((i, line.strip()))

print(f"Found {len(router_lines)} '@router' lines:")
for line_num, line in router_lines[:5]:  # Show first 5
    print(f"   Line {line_num}: {line}")

print("\n🔍 Manual AST traversal:")
def traverse_node(node, depth=0):
    indent = "  " * depth
    print(f"{indent}{type(node).__name__}", end="")
    
    if hasattr(node, 'name'):
        print(f" (name: {node.name})", end="")
    if hasattr(node, 'lineno'):
        print(f" (line: {node.lineno})", end="")
    
    print()
    
    if isinstance(node, ast.FunctionDef):
        print(f"{indent}  -> FUNCTION FOUND: {node.name}")
        return True
    
    found_func = False
    for child in ast.iter_child_nodes(node):
        if traverse_node(child, depth + 1):
            found_func = True
    
    return found_func

print("Starting traversal...")
found = traverse_node(tree)
print(f"Functions found during manual traversal: {found}")