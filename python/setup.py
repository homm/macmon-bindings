from setuptools import setup


setup(
    cffi_modules=["build_ffi.py:ffi"],
    options={"bdist_wheel": {"py_limited_api": "cp39"}},
)
