from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from config import Settings, get_settings

# Type alias used on every endpoint that needs access to app settings.
SettingsDep = Annotated[Settings, Depends(get_settings)]

# CurrentUser and TenantScope dependencies are added in Batch 5 once the
# identity context exists.
