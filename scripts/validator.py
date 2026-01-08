import yaml
import re
import sys
import os
from yaml.loader import SafeLoader

# FIX: Tell PyYAML to treat the '=' sign as a string instead of a special 'value' tag
SafeLoader.add_constructor('tag:yaml.org,2002:value', lambda loader, node: "=")

class PowerAppsValidator:
    def __init__(self, file_path):
        self.file_path = file_path
        self.errors = []
        
        # Keywords that indicate a value should be a Power Fx formula
        self.formula_indicators = [
            r'Filter\(', r'Navigate\(', r'Lookup\(', r'Set\(', r'UpdateContext\(',
            r'Patch\(', r'Collect\(', r'Color\.', r'DisplayMode\.', r'ThisItem\.',
            r'Parent\.', r'RGBA\(', r'If\(', r'CountRows\(', r'SortByColumns\(',
            r'\btrue\b', r'\bfalse\b'
        ]

        # Properties that changed names or are commonly hallucinated from other languages
        self.bad_properties = {
            'OnClick': 'OnSelect',
            'Value': 'Default',
            'OnPress': 'OnSelect'
        }

        # Properties that DO NOT EXIST in the Power Apps Source Schema
        # ZIndex is the most common AI hallucination.
        self.forbidden_properties = {
            'ZIndex': "Power Apps YAML uses the order of declaration for layering. Remove 'ZIndex' and move the control up/down in the file instead."
        }

    def validate(self):
        if not os.path.exists(self.file_path):
            return f"Error: File {self.file_path} not found."

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = yaml.load(f, Loader=SafeLoader)
                if data is None:
                    return "Error: YAML file is empty or invalid."
                
                # Start recursive check
                self._recursive_check(data)
                
        except yaml.YAMLError as exc:
            self.errors.append(f"Invalid YAML Structure: {exc}")
        except Exception as e:
            self.errors.append(f"Unexpected Script Error: {e}")

        return self._format_report()

    def _recursive_check(self, node, current_path="Root"):
        if isinstance(node, dict):
            for key, value in node.items():
                new_path = f"{current_path} -> {key}"
                
                # 1. Check Key Names (Control Names)
                if " " in str(key):
                    self.errors.append(f"Control Name Error: '{key}' contains spaces at {current_path}")

                # 2. Check for Hallucinated/Deprecated Property Names
                if key in self.bad_properties:
                    self.errors.append(f"Property Name Error: Found '{key}' at {current_path}. Use '{self.bad_properties[key]}' instead.")

                # 3. Check for Forbidden Properties (like ZIndex)
                if key in self.forbidden_properties:
                    self.errors.append(f"Schema Error: Found forbidden property '{key}' at {current_path}. {self.forbidden_properties[key]}")

                # 4. Check Values
                if isinstance(value, str):
                    self._validate_value(key, value, current_path)
                
                # 5. Special Gallery Check
                if key == "Control" and value == "Gallery":
                    if isinstance(node, dict) and "Properties" in node:
                        if "Variant" not in node["Properties"]:
                            self.errors.append(f"Gallery Error: Control at {current_path} is missing 'Variant'.")

                # Recurse
                self._recursive_check(value, new_path)
        
        elif isinstance(node, list):
            for i, item in enumerate(node):
                self._recursive_check(item, f"{current_path}[{i}]")

    def _validate_value(self, prop_name, val, path):
        val_str = val.strip()
        
        if not val_str or val_str == "=":
            return

        if val_str.startswith('"') and not val_str.startswith('="'):
            self.errors.append(
                f"Syntax Error at {path}: Property '{prop_name}' starts with double quotes but is missing the '=' prefix. "
                f"Found: {val_str} | Expected: ={val_str}"
            )
            return

        if not val_str.startswith('='):
            for indicator in self.formula_indicators:
                if re.search(indicator, val_str, re.IGNORECASE):
                    self.errors.append(
                        f"Formula Error at {path}: Property '{prop_name}' contains a Power Fx function but missing '=' prefix. Found: '{val_str}'"
                    )
                    break

    def _format_report(self):
        if not self.errors:
            return "✅ Validation Passed: The code is ready for Power Apps."
        
        report = [f"❌ Validation Failed! Found {len(self.errors)} errors:"]
        for err in self.errors:
            report.append(f" - {err}")
        return "\n".join(report)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validator.py <path_to_yaml>")
    else:
        print(PowerAppsValidator(sys.argv[1]).validate())