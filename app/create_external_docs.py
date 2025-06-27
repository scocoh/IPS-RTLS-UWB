# Name: create_external_docs.py
# Version: 0.1.0
# Created: 971201
# Modified: 250502
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: ParcoRTLS backend script
# Location: /home/parcoadmin/parco_fastapi/app
# Role: Backend
# Status: Active
# Dependent: TRUE

#!/usr/bin/env python3
"""
Name: create_external_docs.py
Version: 0.1.0
Created: 250627
Modified: 250627
Creator: ParcoAdmin
Modified By: ParcoAdmin
Description: Create external documentation while preserving FastAPI docstrings
Location: /home/parcoadmin/parco_fastapi/app
Role: Utility
Status: Active
Dependent: FALSE

Creates external markdown documentation from FastAPI route files while:
1. Preserving original docstrings in Python files (for Swagger UI)
2. Creating external markdown files for documentation purposes
3. Adding cross-references between Python and markdown files
"""

import os
import re
import ast
import sys
from pathlib import Path
from typing import Dict, List, Optional

class ExternalDocsCreator:
    def __init__(self, input_file: str, output_dir: str = "docs/endpoints"):
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir)
        self.endpoints = []
        
        # Create output directory structure
        self.endpoint_dir = self.output_dir / self.input_file.stem
        self.endpoint_dir.mkdir(parents=True, exist_ok=True)
        
    def parse_file(self) -> str:
        """Parse Python file and extract endpoint information"""
        print(f"📖 Reading {self.input_file}")
        
        with open(self.input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse AST to find function definitions
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            print(f"❌ Syntax error in {self.input_file}: {e}")
            return content
        
        # Find all function definitions with decorators
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Check if function has router decorator
                for decorator in node.decorator_list:
                    if self._is_router_decorator(decorator):
                        endpoint_info = self._extract_endpoint_info(node, decorator)
                        if endpoint_info:
                            self.endpoints.append(endpoint_info)
        
        print(f"🔍 Found {len(self.endpoints)} endpoints with docstrings")
        return content
    
    def _is_router_decorator(self, decorator) -> bool:
        """Check if decorator is a router method"""
        if isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Attribute):
                return (isinstance(decorator.func.value, ast.Name) and 
                        decorator.func.value.id == 'router')
        elif isinstance(decorator, ast.Attribute):
            return (isinstance(decorator.value, ast.Name) and 
                    decorator.value.id == 'router')
        return False
    
    def _extract_endpoint_info(self, func_node, decorator) -> Optional[Dict]:
        """Extract endpoint information from AST node"""
        # Get HTTP method
        if isinstance(decorator, ast.Call):
            method = decorator.func.attr.upper() # type: ignore
        elif isinstance(decorator, ast.Attribute):
            method = decorator.attr.upper()
        else:
            return None
        
        # Get path from decorator
        path = None
        if isinstance(decorator, ast.Call) and decorator.args:
            if isinstance(decorator.args[0], ast.Constant):
                path = decorator.args[0].value
            elif isinstance(decorator.args[0], ast.Str):
                path = decorator.args[0].s
        elif isinstance(decorator, ast.Attribute):
            path = f"/{func_node.name}"
        
        if not path:
            return None
        
        # Extract docstring
        docstring = ast.get_docstring(func_node)
        if not docstring:
            return None
        
        return {
            'function_name': func_node.name,
            'method': method,
            'path': path,
            'docstring': docstring.strip(),
            'line_number': func_node.lineno
        }
    
    def create_markdown_files(self):
        """Create individual markdown files for each endpoint"""
        print(f"📝 Creating markdown files in {self.endpoint_dir}")
        
        for endpoint in self.endpoints:
            md_filename = f"{endpoint['function_name']}.md"
            md_path = self.endpoint_dir / md_filename
            
            # Create enhanced markdown content
            md_content = self._create_enhanced_markdown_content(endpoint)
            
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            print(f"   ✅ Created {md_filename}")
    
    def _create_enhanced_markdown_content(self, endpoint: Dict) -> str:
        """Create enhanced markdown content for an endpoint"""
        return f"""# {endpoint['method']} {endpoint['path']}

**Function:** `{endpoint['function_name']}`  
**Source:** `{self.input_file}` (line {endpoint['line_number']})  
**Swagger UI:** [View in API docs](http://192.168.210.226:8000/docs#{endpoint['method'].lower()}-{endpoint['path'].replace('/', '-').replace('{', '').replace('}', '')})

---

## Full Documentation

{endpoint['docstring']}

---

## Integration Notes

- **FastAPI Integration:** This endpoint maintains full docstring in the Python source file for Swagger UI
- **External Reference:** This markdown file provides a standalone documentation reference
- **Live API:** Test this endpoint at the Swagger UI link above

## Quick Reference

- **HTTP Method:** `{endpoint['method']}`
- **Endpoint Path:** `{endpoint['path']}`
- **Function Name:** `{endpoint['function_name']}`
- **Source Location:** Line {endpoint['line_number']} in `{self.input_file}`

---
*Generated from {self.input_file.name} on {self._get_timestamp()}*  
*Original docstring preserved in Python source for FastAPI/Swagger UI integration*
"""
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def create_summary_file(self):
        """Create comprehensive summary file"""
        summary_path = self.endpoint_dir / "README.md"
        
        content = f"""# {self.input_file.stem.title()} API Documentation

External documentation for `{self.input_file.name}` endpoints.

> **Note:** Full docstrings are preserved in the Python source file to maintain FastAPI/Swagger UI integration.
> This documentation provides standalone reference materials.

## Quick Links

- **Live API Documentation:** [Swagger UI](http://192.168.210.226:8000/docs)
- **Source File:** `{self.input_file}`
- **Total Endpoints:** {len(self.endpoints)}

## Endpoints Overview

| Method | Path | Function | Documentation | Swagger |
|--------|------|----------|---------------|---------|
"""
        
        for endpoint in self.endpoints:
            md_file = f"{endpoint['function_name']}.md"
            swagger_link = f"http://192.168.210.226:8000/docs#{endpoint['method'].lower()}-{endpoint['path'].replace('/', '-').replace('{', '').replace('}', '')}"
            content += f"| {endpoint['method']} | `{endpoint['path']}` | `{endpoint['function_name']}` | [{md_file}](./{md_file}) | [Try it]({swagger_link}) |\n"
        
        content += f"""

## Documentation Structure

This external documentation approach provides:

### ✅ Preserved Integration
- **FastAPI/Swagger UI:** Full docstrings remain in Python source
- **Interactive Documentation:** Complete API testing interface maintained
- **OpenAPI Schema:** All metadata preserved for client generation

### ✅ External Documentation
- **Standalone Files:** Individual markdown files for each endpoint
- **Cross-References:** Links between markdown and live API documentation
- **Version Control:** Documentation changes tracked separately from code

### ✅ Best of Both Worlds
- **Developers:** Full Swagger UI experience with detailed docstrings
- **Documentation:** Standalone markdown files for wikis, PDFs, etc.
- **Maintenance:** Single source of truth (Python docstrings)

## Usage Examples

### For API Development
Use the [Swagger UI](http://192.168.210.226:8000/docs) for:
- Interactive API testing
- Request/response examples
- Parameter validation
- Authentication testing

### For Documentation
Use these markdown files for:
- Technical documentation
- API reference guides
- Integration planning
- Offline documentation

## Files

- **Python Source:** `{self.input_file}` (original docstrings preserved)
- **Documentation Directory:** `docs/endpoints/{self.input_file.stem}/`
- **Total Documentation Files:** {len(self.endpoints)} endpoint files + this README

---
Generated on: {self._get_timestamp()}  
**Approach:** External documentation with preserved FastAPI integration
"""
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"📋 Created enhanced summary: {summary_path}")
    
    def create_cross_reference_comment(self):
        """Add a comment to the Python file pointing to external docs"""
        print(f"📎 Adding cross-reference comment to {self.input_file}")
        
        with open(self.input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add comment after the existing header
        cross_ref_comment = f"""
# External Documentation: docs/endpoints/{self.input_file.stem}/
# This file maintains full docstrings for FastAPI/Swagger UI integration.
# External markdown documentation available in docs/endpoints/{self.input_file.stem}/README.md
"""
        
        # Insert after the last header comment line
        lines = content.split('\n')
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.startswith('#') and ('ParcoRTLS' in line or 'Licensed under' in line):
                insert_pos = i + 1
                break
        
        lines.insert(insert_pos, cross_ref_comment.strip())
        
        with open(self.input_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
    
    def create_docs(self):
        """Main documentation creation process"""
        print(f"🚀 Creating external documentation for {self.input_file}")
        print("="*60)
        
        # Step 1: Parse file
        self.parse_file()
        
        if not self.endpoints:
            print("❌ No endpoints found with docstrings")
            return False
        
        # Step 2: Create markdown files
        self.create_markdown_files()
        
        # Step 3: Create enhanced summary
        self.create_summary_file()
        
        # Step 4: Add cross-reference to Python file
        self.create_cross_reference_comment()
        
        print("="*60)
        print("✅ External documentation created successfully!")
        print(f"📁 Documentation: {self.endpoint_dir}")
        print(f"🔗 Python file: {self.input_file} (docstrings preserved)")
        print(f"📊 Swagger UI: http://192.168.210.226:8000/docs (fully functional)")
        
        return True

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python create_external_docs.py <route_file> [output_dir]")
        print("Example: python create_external_docs.py routes/trigger.py")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "docs/endpoints"
    
    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        sys.exit(1)
    
    creator = ExternalDocsCreator(input_file, output_dir)
    success = creator.create_docs()
    
    if success:
        print(f"\n🎯 Result:")
        print(f"   ✅ FastAPI/Swagger UI: Fully functional with complete docstrings")
        print(f"   ✅ External docs: Available in {creator.endpoint_dir}")
        print(f"   ✅ Cross-references: Added to both Python and markdown files")
        print(f"\n📋 Next steps:")
        print(f"   1. Test Swagger UI: http://192.168.210.226:8000/docs")
        print(f"   2. Review external docs: {creator.endpoint_dir}/README.md")
        print(f"   3. Commit to git if satisfied")

if __name__ == "__main__":
    main()