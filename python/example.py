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
    for tier in info.cpu_tiers:
        freqs = ", ".join(f"{freq} MHz" for freq in tier.freqs)
        print(f"  CPU tier {tier.label}: {tier.cores} cores [{freqs}]")
    gpu_freqs = ", ".join(f"{freq} MHz" for freq in info.gpu_freqs)
    print(f"  GPU cores: {info.gpu_cores}")
    print(f"  GPU frequencies: [{gpu_freqs}]")


def _print_metrics(sampler: Sampler) -> None:
    metrics = sampler.metrics()
    timestamp = datetime.now().strftime("%H:%M:%S")
    print()
    print(f"[{timestamp}] Metrics")
    for cpu in metrics.cpu_tiers:
        print(
            f"  {cpu.label}: {cpu.freq_mhz} MHz,"
            f" scaled={cpu.scaled_ratio * 100:.1f}%, active={cpu.active_ratio * 100:.1f}%"
        )
    print(
        f"  GPU: {metrics.gpu_freq_mhz} MHz,"
        f" scaled={metrics.gpu_scaled_ratio * 100:.1f}%, active={metrics.gpu_active_ratio * 100:.1f}%"
    )
    print(
        "  Power:"
        f" system={metrics.sys_power:.2f}W"
        f" chip={metrics.chip_power:.2f}W"
        f" cpu={metrics.cpu_power:.2f}W"
        f" gpu={metrics.gpu_power:.2f}W"
        f" ram={metrics.ram_power:.2f}W"
        f" media={metrics.media_power:.2f}W"
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
        f" cpu={metrics.temp.cpu_temp_avg}C"
        f" gpu={metrics.temp.gpu_temp_avg}C"
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
                time.sleep(1.0)
                _print_metrics(sampler)
    except MacmonError as exc:
        print(f"macmon error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
