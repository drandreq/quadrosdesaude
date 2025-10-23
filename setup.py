from setuptools import setup, Extension
import sys

try:
  ext_modules_list = [
    Extension(
      name="quadrosdesaude.datasus", 
      sources=[
        "src/quadrosdesaude/c_src/decompress.c",
        "src/quadrosdesaude/c_src/blast.c"
      ],
      language="c",
    )
  ]

  setup(ext_modules=ext_modules_list)

except Exception as e:
  print(f"--- ERRO DENTRO DO build.py: {e} ---", file=sys.stderr)
  raise