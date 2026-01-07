# Power Apps YAML Coding Standards

## 1. The Formula Prefix (=)
**RULE:** Every property that contains a Power Fx function, variable, or calculation MUST start with the `=` symbol.
*   ❌ `Text: "Welcome " & User().FullName`
*   ✅ `Text: ="Welcome " & User().FullName`
*   ❌ `DisplayMode: DisplayMode.View`
*   ✅ `DisplayMode: =DisplayMode.View`

## 2. Control Naming Conventions
**RULE:** Control names must be alphanumeric. No spaces allowed.
*   **Format:** `[Prefix]_[Description]_[Instance]`
*   **Examples:** `btn_Submit_Main`, `gal_Orders_List`, `lbl_Header_Title`.
*   **Case:** Use PascalCase or snake_case consistently. Never use `Screen 1`.

## 3. String Escaping
**RULE:** Inside a formula (starting with `=`), literal strings must be wrapped in double quotes `"`.
*   ✅ `Text: ="Status: " & ThisItem.Status`

## 4. Property Assignment
**RULE:** Properties are assigned using a colon and a single space `: `.
*   ✅ `Visible: =true`
*   ❌ `Visible:=true`