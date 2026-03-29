from __future__ import annotations

import signal
import sys
import time
from datetime import datetime

from macmon import MacmonError, Sampler, soc_info


_running = True


def _stop(_signum, _frame) -> None:
    global _running
    _running = False


def _format_bytes_gib(value: int) -> str:
    return f"{value / (1024 ** 3):.2f} GiB"


def _print_chip_info() -> None:
    info = soc_info()
    print("Chip info")
    print(f"  Model: {info.mac_model}")
    print(f"  Chip: {info.chip_name}")
    print(f"  Memory: {info.memory_gb} GB")
    for domain in info.cpu_domains:
        freqs = ", ".join(f"{freq} MHz" for freq in domain.frequencies_mhz)
        print(f"  CPU domain {domain.name}: {domain.units} cores [{freqs}]")
    gpu_freqs = ", ".join(f"{freq} MHz" for freq in info.gpu_frequencies_mhz)
    print(f"  GPU cores: {info.gpu_cores}")
    print(f"  GPU frequencies: [{gpu_freqs}]")


def _print_metrics(sampler: Sampler) -> None:
    metrics = sampler.metrics()
    timestamp = datetime.now().strftime("%H:%M:%S")
    print()
    print(f"[{timestamp}] Metrics")
    for cpu in metrics.cpu_usage:
        print(
            f"  {cpu.name}: {cpu.frequency_mhz} MHz, {cpu.usage * 100:.1f}%"
        )
    for gpu in metrics.gpu_usage:
        print(f"  {gpu.name}: {gpu.frequency_mhz} MHz, {gpu.usage * 100:.1f}%")
    print(
        "  Power:"
        f" board={metrics.power.board:.2f}W"
        f" package={metrics.power.package:.2f}W"
        f" cpu={metrics.power.cpu:.2f}W"
        f" gpu={metrics.power.gpu:.2f}W"
        f" ram={metrics.power.ram:.2f}W"
    )
    print(
        "  Memory:"
        f" ram={_format_bytes_gib(metrics.memory.ram_usage)}"
        f"/{_format_bytes_gib(metrics.memory.ram_total)}"
        f" swap={_format_bytes_gib(metrics.memory.swap_usage)}"
        f"/{_format_bytes_gib(metrics.memory.swap_total)}"
    )
    print(
        "  Temperature:"
        f" cpu={metrics.temperature.cpu_average:.1f}C"
        f" gpu={metrics.temperature.gpu_average:.1f}C"
    )


def main() -> int:
    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    try:
        _print_chip_info()
        print()
        print("Streaming metrics. Press Ctrl-C to stop.")
        sys.stdout.flush()

        with Sampler() as sampler:
            while _running:
                _print_metrics(sampler)
                time.sleep(1.0)
    except MacmonError as exc:
        print(f"macmon error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
