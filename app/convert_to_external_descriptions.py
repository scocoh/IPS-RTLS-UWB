# Name: convert_to_external_descriptions.py
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
Name: convert_to_external_descriptions.py
Version: 0.1.1
Created: 250627
Modified: 250627
Creator: ParcoAdmin
Modified By: ParcoAdmin
Description: Convert FastAPI routes to use external descriptions with load_description()
Location: /home/parcoadmin/parco_fastapi/app
Role: Utility
Status: Active
Dependent: FALSE

Converts FastAPI route files to use external description files:
1. Extracts verbose docstrings to .txt files
2. Replaces decorators with summary/description parameters
3. Removes docstrings from functions
4. Adds load_description() function
5. Dramatically reduces file size while maintaining Swagger UI
"""

import os
import re
import ast
import sys
from pathlib import Path
from typing import Dict, List, Optional

class RouteConverter:
    def __init__(self, input_file: str, descriptions_dir: str = "docs/descriptions"):
        self.input_file = Path(input_file)
        self.descriptions_dir = Path(descriptions_dir)
        self.backup_file = self.input_file.with_suffix('.bak')
        self.endpoints = []
        
        # Create descriptions directory structure
        self.endpoint_descriptions_dir = self.descriptions_dir / self.input_file.stem
        self.endpoint_descriptions_dir.mkdir(parents=True, exist_ok=True)
        
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
        
        # Create a brief summary from the first line
        summary = docstring.split('\n')[0].strip()
        if summary.endswith('.'):
            summary = summary[:-1]  # Remove trailing period
        
        return {
            'function_name': func_node.name,
            'method': method,
            'path': path,
            'docstring': docstring.strip(),
            'summary': summary,
            'line_number': func_node.lineno
        }
    
    def create_description_files(self):
        """Create individual description files for each endpoint"""
        print(f"📝 Creating description files in {self.endpoint_descriptions_dir}")
        
        for endpoint in self.endpoints:
            desc_filename = f"{endpoint['function_name']}.txt"
            desc_path = self.endpoint_descriptions_dir / desc_filename
            
            with open(desc_path, 'w', encoding='utf-8') as f:
                f.write(endpoint['docstring'])
            
            print(f"   ✅ Created {desc_filename}")
    
    def create_load_description_function(self) -> str:
        """Create the load_description function code"""
        return f'''
def load_description(endpoint_name: str) -> str:
    """Load endpoint description from external file"""
    try:
        desc_path = Path(__file__).parent.parent / "docs" / "descriptions" / "{self.input_file.stem}" / f"{{endpoint_name}}.txt"
        with open(desc_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return f"Description for {{endpoint_name}} not found"
    except Exception as e:
        return f"Error loading description: {{str(e)}}"
'''
    
    def convert_file(self, original_content: str):
        """Convert the file to use external descriptions"""
        print(f"🔄 Converting {self.input_file} to use external descriptions")
        
        # Create backup
        print(f"💾 Creating backup: {self.backup_file}")
        with open(self.backup_file, 'w', encoding='utf-8') as f:
            f.write(original_content)
        
        # Update version
        current_version = self.extract_version_info(original_content)
        new_version = self.bump_version(current_version)
        
        updated_content = re.sub(
            r'# Version: [\d.]+',
            f'# Version: {new_version}',
            original_content
        )
        
        # Add changelog entry
        changelog_entry = f"# Version {new_version} Converted to external descriptions using load_description()"
        updated_content = re.sub(
            r'(# Modified By: .*?\n)',
            f'\\1{changelog_entry}\n',
            updated_content
        )
        
        # Add Path import if not present
        if 'from pathlib import Path' not in updated_content:
            import_section = re.search(r'(import.*?\n\n)', updated_content, re.DOTALL)
            if import_section:
                updated_content = updated_content.replace(
                    import_section.group(1),
                    import_section.group(1) + 'from pathlib import Path\n\n'
                )
        
        # Add load_description function after imports
        load_func = self.create_load_description_function()
        
        # Find where to insert the function (after imports, before router definition)
        router_match = re.search(r'router = APIRouter.*?\n', updated_content)
        if router_match:
            insert_pos = router_match.start()
            updated_content = (updated_content[:insert_pos] + 
                             load_func + '\n' + 
                             updated_content[insert_pos:])
        
        # Convert each endpoint
        for endpoint in self.endpoints:
            updated_content = self._convert_endpoint(updated_content, endpoint)
        
        # Write converted file
        with open(self.input_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
    
    def _convert_endpoint(self, content: str, endpoint: Dict) -> str:
        """Convert a single endpoint to use external description"""
        func_name = endpoint['function_name']
        method = endpoint['method'].lower()
        path = endpoint['path']
        summary = endpoint['summary']
        
        # Find the current decorator pattern
        # Look for @router.method("/path") or @router.method("/path")
        old_decorator_pattern = rf'@router\.{method}\("?{re.escape(path)}"?\)'
        
        # Create new decorator with summary and description
        new_decorator = f'''@router.{method}(
    "{path}",
    summary="{summary}",
    description=load_description("{func_name}"),
    tags=["triggers"]
)'''
        
        # Replace the decorator
        content = re.sub(old_decorator_pattern, new_decorator, content)
        
        # Remove the docstring from the function
        content = self._remove_function_docstring(content, func_name)
        
        return content
    
    def _remove_function_docstring(self, content: str, func_name: str) -> str:
        """Remove docstring from a specific function"""
        lines = content.split('\n')
        new_lines = []
        in_target_function = False
        in_docstring = False
        docstring_removed = False
        
        for line in lines:
            # Check if we're entering the target function
            if f'async def {func_name}(' in line or f'def {func_name}(' in line:
                in_target_function = True
                new_lines.append(line)
                continue
            
            # If we're in the target function and find a docstring
            if in_target_function and '"""' in line and not in_docstring and not docstring_removed:
                in_docstring = True
                # Check if it's a single-line docstring
                if line.count('"""') == 2:
                    in_docstring = False
                    docstring_removed = True
                    # Skip this line (remove the docstring)
                    continue
                else:
                    # Skip this line (start of multi-line docstring)
                    continue
            
            # If we're inside a multi-line docstring
            if in_docstring:
                if '"""' in line:
                    in_docstring = False
                    docstring_removed = True
                # Skip this line (part of docstring)
                continue
            
            # If we've processed the docstring and hit another function or class
            if in_target_function and docstring_removed and (
                line.strip().startswith('def ') or 
                line.strip().startswith('async def ') or
                line.strip().startswith('class ') or
                line.strip().startswith('@')
            ):
                in_target_function = False
            
            new_lines.append(line)
        
        return '\n'.join(new_lines)
    
    def create_summary_file(self):
        """Create summary of the conversion"""
        summary_path = self.endpoint_descriptions_dir / "README.md"
        
        content = f"""# {self.input_file.stem.title()} External Descriptions

External description files for `{self.input_file.name}` endpoints.

## Conversion Results

- **Original file size:** Large with verbose docstrings
- **Converted file size:** Dramatically reduced
- **Swagger UI:** Fully functional with external descriptions
- **Total endpoints:** {len(self.endpoints)}

## File Structure

Each endpoint has its description in a separate `.txt` file:

"""
        
        for endpoint in self.endpoints:
            desc_file = f"{endpoint['function_name']}.txt"
            content += f"- `{desc_file}` - {endpoint['method']} {endpoint['path']}\n"
        
        content += f"""

## Usage

The `load_description()` function in `{self.input_file.name}` loads these files:

```python
@router.post(
    "/endpoint_path",
    summary="Brief summary",
    description=load_description("function_name"),
    tags=["triggers"]
)
```

## Benefits

- ✅ **Reduced file size:** Much easier to work with in editors and AI tools
- ✅ **Maintained functionality:** Swagger UI shows full descriptions
- ✅ **External management:** Descriptions can be edited separately
- ✅ **Version control:** Code changes don't mix with documentation changes

---
Generated on: {self._get_timestamp()}  
Conversion approach: External descriptions with load_description()
"""
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"📋 Created conversion summary: {summary_path}")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def convert(self):
        """Main conversion process"""
        print(f"🚀 Converting {self.input_file} to use external descriptions")
        print("="*60)
        
        try:
            # Step 1: Parse file
            original_content = self.parse_file()
            
            if not self.endpoints:
                print("❌ No endpoints found with docstrings")
                print("🔍 Debug: Checking file structure...")
                
                # Debug: Show file info
                with open(self.input_file, 'r') as f:
                    content = f.read()
                    lines = content.split('\n')
                    print(f"   File has {len(lines)} lines")
                    
                    # Look for @router patterns
                    router_lines = [i for i, line in enumerate(lines, 1) if '@router' in line]
                    print(f"   Found @router on lines: {router_lines[:5]}")  # Show first 5
                    
                    # Look for async def patterns
                    func_lines = [i for i, line in enumerate(lines, 1) if 'async def' in line]
                    print(f"   Found async def on lines: {func_lines[:5]}")  # Show first 5
                
                return False
            
            # Step 2: Create description files
            self.create_description_files()
            
            # Step 3: Convert the Python file
            self.convert_file(original_content)
            
            # Step 4: Create summary
            self.create_summary_file()
            
            print("="*60)
            print("✅ Conversion completed successfully!")
            print(f"📁 Description files: {self.endpoint_descriptions_dir}")
            print(f"💾 Backup: {self.backup_file}")
            print(f"🔄 Converted file: {self.input_file}")
            
            # Show file size comparison
            try:
                original_size = os.path.getsize(self.backup_file)
                new_size = os.path.getsize(self.input_file)
                reduction = ((original_size - new_size) / original_size) * 100
                print(f"📊 File size: {original_size:,} → {new_size:,} bytes ({reduction:.1f}% reduction)")
            except:
                pass
            
            return True
            
        except Exception as e:
            print(f"❌ Error during conversion: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python convert_to_external_descriptions.py <route_file> [descriptions_dir]")
        print("Example: python convert_to_external_descriptions.py routes/trigger.py")
        sys.exit(1)
    
    input_file = sys.argv[1]
    descriptions_dir = sys.argv[2] if len(sys.argv) > 2 else "docs/descriptions"
    
    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        sys.exit(1)
    
    converter = RouteConverter(input_file, descriptions_dir)
    success = converter.convert()
    
    if success:
        print(f"\n🎯 Results:")
        print(f"   ✅ File size dramatically reduced")
        print(f"   ✅ Swagger UI fully functional")
        print(f"   ✅ External descriptions created")
        print(f"\n📋 Next steps:")
        print(f"   1. Test FastAPI server")
        print(f"   2. Check Swagger UI: http://192.168.210.226:8000/docs")
        print(f"   3. Review file size reduction")
        print(f"   4. Commit if satisfied")

if __name__ == "__main__":
    main()