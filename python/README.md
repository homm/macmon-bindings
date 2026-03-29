# macmon-python

Python wrapper for the Rust `macmon` library via `cffi`.

## Editable install

From the repository root:

```sh
make cmacmon
cd python
pip install -e .
```

## Wheel

From the repository root:

```sh
make python_wheel
```

The raw wheel is written to `python/dist/`.
The repaired wheel is written to `python/wheelhouse/`.

## Example

```sh
cd python
python example.py
```

The example prints `soc_info()` once and then streams metrics to the console until `Ctrl-C`.
If sampler initialization fails on the current host, it exits with the underlying `macmon` error message.
