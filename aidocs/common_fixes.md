# Common AI Hallucinations & Fixes

| Error Found | Required Correction |
| :--- | :--- |
| `OnClick: ...` | Change to `OnSelect: ...` |
| `Items: ["A", "B"]` | Change to `Items: =["A", "B"]` (Add prefix) |
| `Color: "Blue"` | Change to `Color: =Color.Blue` |
| `Variable = 10` | Change to `Set(Variable, 10)` or `UpdateContext({Variable: 10})` |
| `If(x, y, z)` | Ensure it starts with `=If(x, y, z)` |
| `Navigate("Screen2")` | Change to `Navigate(Screen2)` (No quotes for screen objects) |
| `Variant` missing in Gallery | Add `Variant: BrowseLayout_Flexible_SocialFeed_ver5.0` to the Gallery |

## Logic Check:
If the AI uses `UpdateContext` for a global variable (needed across screens), suggest `Set` instead.
If the AI uses `Set` for a screen-specific variable, suggest `UpdateContext`.