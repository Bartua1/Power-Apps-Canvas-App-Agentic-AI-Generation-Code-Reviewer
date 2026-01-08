import yaml
import re
import sys
import os
from yaml.loader import SafeLoader

# 1. Custom Loader to capture both Line and Column numbers
class SafeLineLoader(SafeLoader):
    def construct_mapping(self, node, deep=False):
        mapping = super(SafeLineLoader, self).construct_mapping(node, deep=deep)
        # Add 1 because PyYAML marks are 0-indexed
        mapping['__line__'] = node.start_mark.line + 1
        mapping['__col__'] = node.start_mark.column + 1
        return mapping

# Preserve the fix for the '=' sign
SafeLineLoader.add_constructor('tag:yaml.org,2002:value', lambda loader, node: "=")

class PowerAppsValidator:
    def __init__(self, file_path):
        self.file_path = file_path
        self.errors = []
        self.warnings = []
        
        self.formula_indicators = [
            r'Filter\(', r'Navigate\(', r'Lookup\(', r'Set\(', r'UpdateContext\(',
            r'Patch\(', r'Collect\(', r'Color\.', r'DisplayMode\.', r'ThisItem\.',
            r'Parent\.', r'RGBA\(', r'If\(', r'CountRows\(', r'SortByColumns\(',
            r'\btrue\b', r'\bfalse\b'
        ]

        self.bad_properties = {
            'OnClick': 'OnSelect',
            'Value': 'Default',
            'OnPress': 'OnSelect'
        }

        self.forbidden_properties = {
            'ZIndex': "Power Apps YAML uses layering order. Move the control up/down in the file instead."
        }

    def _get_loc_prefix(self, node):
        """Helper to format the clickable file string."""
        line = node.get('__line__', 1)
        col = node.get('__col__', 1)
        # Format: File "path", line X, col Y
        return f'File "{self.file_path}", line {line}, col {col}'

    def validate(self):
        if not os.path.exists(self.file_path):
            return f"Error: File {self.file_path} not found."

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = yaml.load(f, Loader=SafeLineLoader)
                if data is None:
                    return "Error: YAML file is empty or invalid."
                
                self._recursive_check(data)
                
        except yaml.YAMLError as exc:
            # Handle syntax errors during parsing
            mark = exc.problem_mark
            self.errors.append(f'File "{self.file_path}", line {mark.line+1}, col {mark.column+1}: Invalid YAML Structure: {exc.problem}')
        except Exception as e:
            self.errors.append(f"Unexpected Script Error: {e}")

        return self._format_report()

    def _recursive_check(self, node, current_path="Root"):
        if isinstance(node, dict):
            loc = self._get_loc_prefix(node)
            
            # Check for Container Properties
            if node.get("Control") == "GroupContainer@1.4.0":
                self._check_container_styling(node, loc)

            for key, value in node.items():
                if key in ['__line__', '__col__']: continue 
                
                # 1. Check Key Names
                if " " in str(key):
                    self.errors.append(f"{loc}: Control Name Error: '{key}' contains spaces.")

                # 2. Check for Hallucinated/Deprecated Property Names
                if key in self.bad_properties:
                    self.errors.append(f"{loc}: Property Name Error: Found '{key}'. Use '{self.bad_properties[key]}' instead.")

                # 3. Check for Forbidden Properties
                if key in self.forbidden_properties:
                    self.errors.append(f"{loc}: Schema Error: Found forbidden property '{key}'. {self.forbidden_properties[key]}")

                # 4. Check Values
                if isinstance(value, str):
                    self._validate_value(key, value, loc)
                
                # 5. Gallery Check
                if key == "Control" and value == "Gallery":
                    if "Properties" in node and "Variant" not in node["Properties"]:
                        self.errors.append(f"{loc}: Gallery Error: Missing 'Variant' property.")

                # Recurse
                self._recursive_check(value, f"{current_path} -> {key}")
        
        elif isinstance(node, list):
            for i, item in enumerate(node):
                self._recursive_check(item, f"{current_path}[{i}]")

    def _check_container_styling(self, node, loc):
        props = node.get("Properties", {})
        required = ["RadiusBottomLeft", "RadiusBottomRight", "RadiusTopLeft", "RadiusTopRight", "DropShadow"]
        missing = [p for p in required if p not in props]
        
        if missing:
            self.warnings.append(
                f"{loc}: Warning: By default all containers have shadow light and a border radius of 4. "
                f"(Missing explicit: {', '.join(missing)})"
            )

    def _validate_value(self, prop_name, val, loc):
        val_str = val.strip()
        if not val_str or val_str == "=": return

        if val_str.startswith('"') and not val_str.startswith('="'):
            self.errors.append(f"{loc}: Syntax Error: Property '{prop_name}' starts with quotes but missing '=' prefix.")
            return

        if not val_str.startswith('='):
            for indicator in self.formula_indicators:
                if re.search(indicator, val_str, re.IGNORECASE):
                    self.errors.append(f"{loc}: Formula Error: Property '{prop_name}' contains a Power Fx function but missing '=' prefix.")
                    break

    def _format_report(self):
        if not self.errors and not self.warnings:
            return "✅ Validation Passed: The code is ready for Power Apps."
        
        report = []
        if self.errors:
            report.append(f"❌ Validation Failed! Found {len(self.errors)} errors:")
            for err in self.errors:
                report.append(f"  {err}") # Format ensures this is a clickable line
        
        if self.warnings:
            if self.errors: report.append("") 
            report.append(f"⚠️  Warnings ({len(self.warnings)}):")
            for warn in self.warnings:
                report.append(f"  {warn}") # Format ensures this is a clickable line
                
        return "\n".join(report)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validator.py <path_to_yaml>")
    else:
        print(PowerAppsValidator(sys.argv[1]).validate())