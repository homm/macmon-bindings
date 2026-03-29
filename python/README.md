Fast Python bindings for `macmon`.

The wheel bundles the native library, so it installs and runs without separate external binaries.

# Usage

`Sampler.metrics()` returns the current cumulative sample immediately.
The caller is responsible for timing and timeout policy, so the library does not need its own async API.

```python
import asyncio

from macmon import Sampler, soc_info


async def main() -> None:
    info = soc_info()
    print(info.chip_name)

    with Sampler() as sampler:
        while True:
            metrics = sampler.metrics()
            print(
                "board_w=%.2f cpu_usage=%.3f gpu_usage=%.3f"
                % (
                    metrics.power.board,
                    metrics.cpu_usage[0].usage if metrics.cpu_usage else 0.0,
                    metrics.gpu_usage[0].usage if metrics.gpu_usage else 0.0,
                )
            )
            await asyncio.sleep(1.0)


asyncio.run(main())
```

For a more complete example, see [example.py](example.py).

# Develop

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

The repaired wheel is written to `python/wheelhouse/`.
