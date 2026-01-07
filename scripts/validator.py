import yaml
import re
import sys
import os

class PowerAppsValidator:
    def __init__(self, file_path):
        self.file_path = file_path
        self.errors = []
        self.warnings = []

        # Keywords that indicate a value should be a Power Fx formula (starting with =)
        self.formula_indicators = [
            r'Filter\(', r'Navigate\(', r'Lookup\(', r'Set\(', r'UpdateContext\(',
            r'Patch\(', r'Collect\(', r'Color\.', r'DisplayMode\.', r'ThisItem\.',
            r'Parent\.', r'RGBA\(', r'If\(', r'CountRows\(', r'SortByColumns\(',
            r'\btrue\b', r'\bfalse\b'
        ]

        # Hallucinated properties mapping
        self.bad_properties = {
            'OnClick': 'OnSelect',
            'Value': 'Default (usually)',
            'OnPress': 'OnSelect'
        }

    def validate(self):
        if not os.path.exists(self.file_path):
            return f"Error: File {self.file_path} not found."

        try:
            with open(self.file_path, 'r') as f:
                data = yaml.safe_load(f)
                if not data:
                    return "Error: YAML file is empty."
                self._check_node(data)
        except yaml.YAMLError as exc:
            self.errors.append(f"Invalid YAML Structure: {exc}")
        except Exception as e:
            self.errors.append(f"Unexpected Error: {e}")

        return self._format_report()

    def _check_node(self, node, parent_name="Root"):
        """Recursively check controls and properties."""
        if not isinstance(node, dict):
            return

        for key, value in node.items():
            # 1. Check Control Naming (No spaces)
            if " " in key:
                self.errors.append(f"Control Name Error: '{key}' contains spaces. Power Apps names must be alphanumeric.")

            if isinstance(value, dict):
                # 2. Gallery Specific Check: Variant Missing
                control_type = value.get("Control") or value.get("Type")
                if control_type == "Gallery":
                    properties = value.get("Properties", {})
                    if "Variant" not in properties:
                        self.errors.append(f"Gallery Error: '{key}' is missing the 'Variant' property. Suggestion: Add 'Variant: BrowseLayout_Flexible_SocialFeed_ver5.0'")

                # 3. Check Properties block
                if "Properties" in value:
                    self._check_properties(key, value["Properties"])

                # Recursive call for children/nested controls
                self._check_node(value, key)

    def _check_properties(self, control_name, props):
        if not isinstance(props, dict):
            return

        for p_name, p_val in props.items():
            val_str = str(p_val)

            # 4. Check for Hallucinated Property Names
            if p_name in self.bad_properties:
                self.errors.append(f"Property Name Error: '{control_name}' uses '{p_name}'. Did you mean '{self.bad_properties[p_name]}建?")

            # 5. The Formula Prefix Rule (=)
            # If it looks like a formula but doesn't start with =
            for indicator in self.formula_indicators:
                if re.search(indicator, val_str, re.IGNORECASE):
                    if not val_str.startswith("="):
                        self.errors.append(f"Formula Error: Property '{p_name}' in '{control_name}' contains logic but is missing the '=' prefix. Found: '{val_str}'")
                        break

    def _format_report(self):
        if not self.errors and not self.warnings:
            return "✅ Validation Passed: The code is ready for Power Apps."

        report = ["❌ Validation Failed! Please fix the following errors:"]
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