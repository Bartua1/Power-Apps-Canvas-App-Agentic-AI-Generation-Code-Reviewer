# Valid Control Properties Reference

## Screen
- **Properties:** `OnVisible`, `OnHidden`, `Fill`, `LoadingSpinner`.

## Button
- **Properties:** `OnSelect`, `Text`, `DisplayMode`, `Visible`, `Fill`, `HoverFill`.
- **Note:** Never use `OnClick`. Use `OnSelect`.

## Label
- **Properties:** `Text`, `Color`, `Font`, `Size`, `FontWeight`, `Align`.

## Gallery
- **Properties:** `Items`, `OnSelect`, `TemplateSize`, `Transition`, `DelayItemLoading`, `Variant`.
- **Important:** References inside the gallery must use `ThisItem`, `Variant` should be: `BrowseLayout_Flexible_SocialFeed_ver5.0`

## Text Input
- **Properties:** `Default`, `OnChange`, `DelayOutput`, `Format`, `Mode`, `HintText`.
- **Note:** `Value` is not a property; use `Default`.