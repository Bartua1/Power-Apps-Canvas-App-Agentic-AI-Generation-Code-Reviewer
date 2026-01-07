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
        self.warnings = []

        # Keywords that indicate a value should be a Power Fx formula
        self.formula_indicators = [
            r'Filter\(', r'Navigate\(', r'Lookup\(', r'Set\(', r'UpdateContext\(',
            r'Patch\(', r'Collect\(', r'Color\.', r'DisplayMode\.', r'ThisItem\.',
            r'Parent\.', r'RGBA\(', r'If\(', r'CountRows\(', r'SortByColumns\(',
            r'\btrue\b', r'\bfalse\b'
        ]

        # Common hallucinations
        self.bad_properties = {
            'OnClick': 'OnSelect',
            'Value': 'Default',
            'OnPress': 'OnSelect'
        }

    def validate(self):
        if not os.path.exists(self.file_path):
            return f"Error: File {self.file_path} not found."

        try:
            with open(self.file_path, 'r') as f:
                # Use the patched SafeLoader
                data = yaml.load(f, Loader=SafeLoader)
                if not data:
                    return "Error: YAML file is empty."
                self._check_node(data)
        except yaml.YAMLError as exc:
            self.errors.append(f"Invalid YAML Structure: {exc}")
        except Exception as e:
            self.errors.append(f"Unexpected Script Error: {e}")

        return self._format_report()

    def _check_node(self, node, parent_name="Root"):
        if not isinstance(node, dict):
            return

        for key, value in node.items():
            if " " in key:
                self.errors.append(f"Control Name Error: '{key}' contains spaces.")

            if isinstance(value, dict):
                control_type = value.get("Control") or value.get("Type")
                
                # Gallery Check: Ensure Variant exists
                if control_type == "Gallery":
                    # Safer check for None or missing Properties
                    properties = value.get("Properties") or {}
                    if "Variant" not in properties:
                        self.errors.append(f"Gallery Error: '{key}' is missing 'Variant'. Suggestion: Add 'Variant: BrowseLayout_Flexible_SocialFeed_ver5.0'")

                # Check Properties block
                if "Properties" in value:
                    self._check_properties(key, value["Properties"])

                # Recursively check children
                self._check_node(value, key)

    def _check_properties(self, control_name, props):
        if not isinstance(props, dict):
            return

        for p_name, p_val in props.items():
            # If the property is empty (None), skip or treat as empty string
            if p_val is None:
                continue
                
            val_str = str(p_val)

            # Property Name Check
            if p_name in self.bad_properties:
                self.errors.append(f"Property Name Error: '{control_name}' uses '{p_name}'. Use '{self.bad_properties[p_name]}' instead.")

            # Formula Prefix Check
            # If the value is just "=", it's an empty formula, which is valid.
            if val_str == "=":
                continue

            for indicator in self.formula_indicators:
                if re.search(indicator, val_str, re.IGNORECASE):
                    if not val_str.startswith("="):
                        self.errors.append(f"Formula Error: Property '{p_name}' in '{control_name}' missing '=' prefix. Found: '{val_str}'")
                        break

    def _format_report(self):
        if not self.errors:
            return "✅ Validation Passed: The code is ready for Power Apps."
        
        report = ["❌ Validation Failed! Please fix these errors:"]
        for err in self.errors:
            report.append(f" - {err}")
        return "\n".join(report)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validator.py <path_to_yaml>")
    else:
        file_to_check = sys.argv[1]
        validator = PowerAppsValidator(file_to_check)
        print(validator.validate())