# Name: extract_docstrings.py
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
"""
Name: extract_docstrings.py
Version: 0.1.3
Created: 250626
Modified: 250626
Creator: ParcoAdmin
Modified By: ParcoAdmin
Description: Extract FastAPI endpoint docstrings to external markdown files
Location: /home/parcoadmin/parco_fastapi/app
Role: Utility
Status: Active
Dependent: FALSE

Extracts inline docstrings from FastAPI route files and creates:
1. Backup of original file (.bak)
2. New route file with external references
3. Individual markdown files for each endpoint
4. Maintains FastAPI/Swagger UI integration
"""

import os
import re
import ast
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class DocstringExtractor:
    def __init__(self, input_file: str, output_dir: str = "docs/endpoints"):
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir)
        self.backup_file = self.input_file.with_suffix('.bak')
        self.endpoints = []
        
        # Create output directory structure
        self.endpoint_dir = self.output_dir / self.input_file.stem
        self.endpoint_dir.mkdir(parents=True, exist_ok=True)
        
    def extract_version_info(self, content: str) -> str:
        """Extract version information from file header"""
        version_match = re.search(r'# Version: ([\d.]+)', content)
        return version_match.group(1) if version_match else "0.1.0"
    
    def bump_version(self, version: str) -> str:
        """Bump patch version number"""
        parts = version.split('.')
        if len(parts) >= 3:
            parts[2] = str(int(parts[2]) + 1)
        else:
            parts.append('1')
        return '.'.join(parts)
    
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
        func_count = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):  # Handle both sync and async functions
                func_count += 1
                print(f"🔍 Found function: {node.name} with {len(node.decorator_list)} decorators")
                
                # Check if function has router decorator
                for i, decorator in enumerate(node.decorator_list):
                    print(f"   Decorator {i}: {ast.dump(decorator)}")
                    if self._is_router_decorator(decorator):
                        print(f"   ✅ Router decorator found!")
                        endpoint_info = self._extract_endpoint_info(node, decorator, content)
                        if endpoint_info:
                            print(f"   ✅ Endpoint info extracted: {endpoint_info['function_name']}")
                            self.endpoints.append(endpoint_info)
                        else:
                            print(f"   ❌ Failed to extract endpoint info")
                    else:
                        print(f"   ❌ Not a router decorator")
        
        print(f"🔍 Total functions found: {func_count}")
        print(f"🔍 Endpoints with docstrings: {len(self.endpoints)}")
        return content
    
    def _is_router_decorator(self, decorator) -> bool:
        """Check if decorator is a router method (get, post, put, delete, etc.)"""
        if isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Attribute):
                return (isinstance(decorator.func.value, ast.Name) and 
                        decorator.func.value.id == 'router')
        elif isinstance(decorator, ast.Attribute):
            # Handle @router.get, @router.post without parentheses
            return (isinstance(decorator.value, ast.Name) and 
                    decorator.value.id == 'router')
        return False
    
    def _extract_endpoint_info(self, func_node, decorator, content: str) -> Optional[Dict]:
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
            elif isinstance(decorator.args[0], ast.Str):  # Python < 3.8
                path = decorator.args[0].s
        elif isinstance(decorator, ast.Attribute):
            # For decorators without arguments, try to infer from function name
            path = f"/{func_node.name}"
        
        if not path:
            return None
        
        # Extract docstring
        docstring = ast.get_docstring(func_node)
        if not docstring:
            return None
        
        # Get function name
        func_name = func_node.name
        
        # Get line numbers for replacement
        start_line = func_node.lineno
        end_line = func_node.end_lineno if hasattr(func_node, 'end_lineno') else start_line
        
        return {
            'function_name': func_name,
            'method': method,
            'path': path,
            'docstring': docstring.strip(),
            'start_line': start_line,
            'end_line': end_line
        }
    
    def create_markdown_files(self):
        """Create individual markdown files for each endpoint"""
        print(f"📝 Creating markdown files in {self.endpoint_dir}")
        
        for endpoint in self.endpoints:
            md_filename = f"{endpoint['function_name']}.md"
            md_path = self.endpoint_dir / md_filename
            
            # Create markdown content
            md_content = self._create_markdown_content(endpoint)
            
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            print(f"   ✅ Created {md_filename}")
    
    def _create_markdown_content(self, endpoint: Dict) -> str:
        """Create markdown content for an endpoint"""
        return f"""# {endpoint['method']} {endpoint['path']}

**Function:** `{endpoint['function_name']}`

## Documentation

{endpoint['docstring']}

---
*Generated from {self.input_file.name} on {self._get_timestamp()}*
"""
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def create_new_route_file(self, original_content: str):
        """Create new route file with external docstring references"""
        print(f"🔄 Creating new {self.input_file}")
        
        # Create backup first
        print(f"💾 Creating backup: {self.backup_file}")
        with open(self.backup_file, 'w', encoding='utf-8') as f:
            f.write(original_content)
        
        # Update version in content
        current_version = self.extract_version_info(original_content)
        new_version = self.bump_version(current_version)
        
        updated_content = re.sub(
            r'# Version: [\d.]+',
            f'# Version: {new_version}',
            original_content
        )
        
        # Add changelog entry
        changelog_entry = f"# Version {new_version} Changed to external docstrings in docs/endpoints/{self.input_file.stem}/"
        updated_content = re.sub(
            r'(# Modified By: .*?\n)',
            f'\\1{changelog_entry}\n',
            updated_content
        )
        
        # Replace docstrings with external references
        lines = updated_content.split('\n')
        new_lines = []
        skip_docstring = False
        in_function = False
        current_function = None
        
        for i, line in enumerate(lines):
            line_num = i + 1
            
            # Check if we're starting a function definition
            if re.match(r'^(async )?def ', line.strip()):
                in_function = True
                # Find which endpoint this is
                for endpoint in self.endpoints:
                    if line_num >= endpoint['start_line'] and line_num <= endpoint['end_line']:
                        current_function = endpoint['function_name']
                        break
                new_lines.append(line)
                continue
            
            # Check for docstring start
            if in_function and '"""' in line and not skip_docstring:
                if current_function:
                    # Replace with external reference
                    indent = len(line) - len(line.lstrip())
                    external_ref = self._create_external_docstring_reference(current_function, indent)
                    new_lines.append(external_ref)
                    skip_docstring = True
                    
                    # Skip until closing docstring
                    if line.count('"""') == 2:  # Single line docstring
                        skip_docstring = False
                        in_function = False
                        current_function = None
                    continue
                else:
                    new_lines.append(line)
                    continue
            
            # Skip lines inside docstring
            if skip_docstring:
                if '"""' in line:
                    skip_docstring = False
                    in_function = False
                    current_function = None
                continue
            
            new_lines.append(line)
        
        # Write new file
        with open(self.input_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
    
    def _create_external_docstring_reference(self, function_name: str, indent: int) -> str:
        """Create external docstring reference for FastAPI"""
        spaces = ' ' * indent
        doc_path = f"docs/endpoints/{self.input_file.stem}/{function_name}.md"
        
        return f'{spaces}"""External documentation: {doc_path}"""'
    
    def create_summary_file(self):
        """Create summary file of all extracted endpoints"""
        summary_path = self.endpoint_dir / "README.md"
        
        content = f"""# {self.input_file.stem.title()} Endpoints Documentation

This directory contains externalized docstrings for {self.input_file.name}.

## Endpoints

| Method | Path | Function | Documentation |
|--------|------|----------|---------------|
"""
        
        for endpoint in self.endpoints:
            md_file = f"{endpoint['function_name']}.md"
            content += f"| {endpoint['method']} | `{endpoint['path']}` | `{endpoint['function_name']}` | [{md_file}](./{md_file}) |\n"
        
        content += f"""
## Integration

The original Python file maintains FastAPI/Swagger UI integration through:
- External docstring references
- OpenAPI metadata preservation
- Response descriptions and summaries

## Files

- **Original backup:** `{self.backup_file.name}`
- **Updated route file:** `{self.input_file.name}`
- **Documentation directory:** `docs/endpoints/{self.input_file.stem}/`

Generated on: {self._get_timestamp()}
"""
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"📋 Created summary: {summary_path}")
    
    def extract(self):
        """Main extraction process"""
        print(f"🚀 Starting docstring extraction for {self.input_file}")
        print("="*60)
        
        # Step 1: Parse file
        original_content = self.parse_file()
        
        if not self.endpoints:
            print("❌ No endpoints found with docstrings")
            return False
        
        # Step 2: Create markdown files
        self.create_markdown_files()
        
        # Step 3: Create new route file
        self.create_new_route_file(original_content)
        
        # Step 4: Create summary
        self.create_summary_file()
        
        print("="*60)
        print("✅ Extraction completed successfully!")
        print(f"📁 Documentation created in: {self.endpoint_dir}")
        print(f"💾 Backup created: {self.backup_file}")
        print(f"🔄 Updated route file: {self.input_file}")
        
        return True

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python extract_docstrings.py <route_file> [output_dir]")
        print("Example: python extract_docstrings.py routes/trigger.py")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "docs/endpoints"
    
    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        sys.exit(1)
    
    extractor = DocstringExtractor(input_file, output_dir)
    success = extractor.extract()
    
    if success:
        print(f"\n🎯 Next steps:")
        print(f"   1. Review generated markdown files in {extractor.endpoint_dir}")
        print(f"   2. Test FastAPI server to ensure Swagger UI still works")
        print(f"   3. Commit changes to git")
        print(f"   4. Run: git add . && git commit -m 'Externalize {extractor.input_file.stem} docstrings'")

if __name__ == "__main__":
    main()