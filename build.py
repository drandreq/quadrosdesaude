from __future__ import annotations
import os
import shutil
from pathlib import Path
from setuptools import Distribution, Extension
from setuptools.command.build_ext import build_ext

def build() -> None:
    extensions = [
        Extension(
            name="quadrosdesaude.datasus", 
            sources=[
                "src/quadrosdesaude/c_src/decompress.c",
                "src/quadrosdesaude/c_src/blast.c"
            ],
            language="c",
        )
    ]

    distribution = Distribution({
        "name": "quadrosdesaude",
        "ext_modules": extensions
    })

    cmd = build_ext(distribution)
    cmd.ensure_finalized()
    cmd.run()

    # Move os binários compilados de volta para a pasta src para funcionarem transparentemente
    for output in cmd.get_outputs():
        output = Path(output)
        relative_extension = Path("src") / output.relative_to(cmd.build_lib)
        
        # Garante que as pastas da árvore existam
        relative_extension.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copyfile(output, relative_extension)
        mode = os.stat(relative_extension).st_mode
        mode |= (mode & 0o444) >> 2
        os.chmod(relative_extension, mode)

if __name__ == "__main__":
    build()
