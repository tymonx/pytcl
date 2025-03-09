---
SPDX-FileCopyrightText: 2025 Tymoteusz Blazejczyk <tymoteusz.blazejczyk@tymonx.com>
SPDX-License-Identifier: Apache-2.0
---

# PyTCL

**PyTCL** allows control EDA tools directly from **Python** that use **TCL**.

## Examples

Creating new Vivado project:

```python
from pathlib import Path
from pytcl import Vivado

def main() -> None:
    """Create new Vivado project."""
    project_dir: Path = Path.cwd() / "my-awesome-project"

    with Vivado() as vivado:
        vivado.create_project(project_dir.name, project_dir)
        vivado.close_project()

if __name__ == "__main__":
    main()
```
