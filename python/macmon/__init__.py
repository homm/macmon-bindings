from __future__ import annotations

from dataclasses import dataclass

from ._api import ffi as _ffi
from ._api import lib as _lib


class MacmonError(RuntimeError):
    pass


class InvalidArgumentError(MacmonError):
    pass


class InitializationFailedError(MacmonError):
    pass


class SamplingFailedError(MacmonError):
    pass


class PanicError(MacmonError):
    pass


def _last_error_message() -> str:
    ptr = _lib.macmon_last_error_message()
    if ptr == _ffi.NULL:
        return "macmon returned an unknown error"
    return _ffi.string(ptr).decode("utf-8")


def _check_status(status: int) -> None:
    if status == _lib.MACMON_STATUS_OK:
        return

    message = _last_error_message()
    if status == _lib.MACMON_STATUS_INVALID_ARGUMENT:
        raise InvalidArgumentError(message)
    if status == _lib.MACMON_STATUS_INIT_FAILED:
        raise InitializationFailedError(message)
    if status == _lib.MACMON_STATUS_SAMPLE_FAILED:
        raise SamplingFailedError(message)
    if status == _lib.MACMON_STATUS_PANIC:
        raise PanicError(message)
    raise MacmonError(f"status {int(status)}: {message}")


def _decode_string(ptr) -> str:
    if ptr == _ffi.NULL:
        return ""
    return _ffi.string(ptr).decode("utf-8")


def _uint32_list(ptr, length: int) -> list[int]:
    return [int(ptr[index]) for index in range(length)] if ptr != _ffi.NULL else []


@dataclass(frozen=True)
class CpuCoreMetrics:
    die_id: int
    core_id: int
    freq_mhz: int
    scaled_ratio: float
    active_ratio: float


@dataclass(frozen=True)
class CpuTierMetrics:
    label: str
    freq_mhz: int
    scaled_ratio: float
    active_ratio: float
    cores: list[CpuCoreMetrics]


@dataclass(frozen=True)
class FanMetric:
    name: str
    rpm: int
    max_rpm: int


@dataclass(frozen=True)
class MemMetrics:
    ram_total: int
    ram_usage: int
    swap_total: int
    swap_usage: int


@dataclass(frozen=True)
class TempMetrics:
    cpu_temp_avg: float
    gpu_temp_avg: float


@dataclass(frozen=True)
class Metrics:
    temp: TempMetrics
    memory: MemMetrics
    fans: list[FanMetric]
    cpu_scaled_ratio: float
    cpu_active_ratio: float
    cpu_tiers: list[CpuTierMetrics]
    gpu_freq_mhz: int
    gpu_scaled_ratio: float
    gpu_active_ratio: float
    cpu_power: float
    gpu_power: float
    ane_power: float
    chip_power: float
    sys_power: float
    ram_power: float
    gpu_ram_power: float
    media_power: float
    display_power: float
    battery_power: float
    dc_in_power: float


@dataclass(frozen=True)
class CpuTierInfo:
    label: str
    cores: int
    freqs: list[int]


@dataclass(frozen=True)
class SocInfo:
    mac_model: str
    chip_name: str
    memory_gb: int
    cpu_tiers: list[CpuTierInfo]
    gpu_cores: int
    gpu_freqs: list[int]
    vm: bool


def _cpu_tier_from_raw(raw) -> CpuTierMetrics:
    return CpuTierMetrics(
        label=_decode_string(raw.label),
        freq_mhz=int(raw.freq_mhz),
        scaled_ratio=float(raw.scaled_ratio),
        active_ratio=float(raw.active_ratio),
        cores=[
            CpuCoreMetrics(
                die_id=int(core.die_id),
                core_id=int(core.core_id),
                freq_mhz=int(core.freq_mhz),
                scaled_ratio=float(core.scaled_ratio),
                active_ratio=float(core.active_ratio),
            )
            for core in (raw.cores[index] for index in range(int(raw.cores_len)))
        ],
    )


def _memory_metrics_from_raw(raw) -> MemMetrics:
    return MemMetrics(
        ram_total=int(raw.ram_total),
        ram_usage=int(raw.ram_usage),
        swap_total=int(raw.swap_total),
        swap_usage=int(raw.swap_usage),
    )


def _temperature_metrics_from_raw(raw) -> TempMetrics:
    return TempMetrics(
        cpu_temp_avg=float(raw.cpu_temp_avg),
        gpu_temp_avg=float(raw.gpu_temp_avg),
    )


def _metrics_from_raw(raw) -> Metrics:
    return Metrics(
        temp=_temperature_metrics_from_raw(raw.temp),
        memory=_memory_metrics_from_raw(raw.memory),
        fans=[
            FanMetric(
                name=_decode_string(fan.name),
                rpm=int(fan.rpm),
                max_rpm=int(fan.max_rpm),
            )
            for fan in (raw.fans[index] for index in range(int(raw.fans_len)))
        ],
        cpu_scaled_ratio=float(raw.cpu_scaled_ratio),
        cpu_active_ratio=float(raw.cpu_active_ratio),
        cpu_tiers=[_cpu_tier_from_raw(raw.cpu_tiers[index]) for index in range(int(raw.cpu_tiers_len))],
        gpu_freq_mhz=int(raw.gpu_freq_mhz),
        gpu_scaled_ratio=float(raw.gpu_scaled_ratio),
        gpu_active_ratio=float(raw.gpu_active_ratio),
        cpu_power=float(raw.cpu_power),
        gpu_power=float(raw.gpu_power),
        ane_power=float(raw.ane_power),
        chip_power=float(raw.chip_power),
        sys_power=float(raw.sys_power),
        ram_power=float(raw.ram_power),
        gpu_ram_power=float(raw.gpu_ram_power),
        media_power=float(raw.media_power),
        display_power=float(raw.display_power),
        battery_power=float(raw.battery_power),
        dc_in_power=float(raw.dc_in_power),
    )


def _cpu_tier_info_from_raw(raw) -> CpuTierInfo:
    return CpuTierInfo(
        label=_decode_string(raw.label),
        cores=int(raw.cores),
        freqs=_uint32_list(raw.freqs, int(raw.freqs_len)),
    )


def _soc_info_from_raw(raw) -> SocInfo:
    return SocInfo(
        mac_model=_decode_string(raw.mac_model),
        chip_name=_decode_string(raw.chip_name),
        memory_gb=int(raw.memory_gb),
        cpu_tiers=[
            _cpu_tier_info_from_raw(raw.cpu_tiers[index])
            for index in range(int(raw.cpu_tiers_len))
        ],
        gpu_cores=int(raw.gpu_cores),
        gpu_freqs=_uint32_list(raw.gpu_freqs, int(raw.gpu_freqs_len)),
        vm=bool(raw.vm),
    )


class Sampler:
    def __init__(self) -> None:
        handle = _ffi.new("macmon_sampler_t **")
        status = _lib.macmon_sampler_new(handle)
        _check_status(status)
        if handle[0] == _ffi.NULL:
            raise InitializationFailedError(
                "macmon returned success without a sampler handle"
            )
        self._handle = handle[0]

    def close(self) -> None:
        if self._handle != _ffi.NULL:
            _lib.macmon_sampler_free(self._handle)
            self._handle = _ffi.NULL

    def metrics(self) -> Metrics:
        if self._handle == _ffi.NULL:
            raise InvalidArgumentError("sampler has already been released")

        raw = _ffi.new("macmon_metrics_t *")
        status = _lib.macmon_sampler_get_metrics(self._handle, raw)
        _check_status(status)
        try:
            return _metrics_from_raw(raw[0])
        finally:
            _lib.macmon_metrics_free(raw)

    def __enter__(self) -> Sampler:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self) -> None:
        handle = getattr(self, "_handle", _ffi.NULL)
        if handle != _ffi.NULL:
            _lib.macmon_sampler_free(handle)


def soc_info() -> SocInfo:
    raw = _ffi.new("macmon_soc_info_t *")
    status = _lib.macmon_get_soc_info(raw)
    _check_status(status)
    try:
        return _soc_info_from_raw(raw[0])
    finally:
        _lib.macmon_soc_info_free(raw)


__all__ = [
    "CpuCoreMetrics",
    "CpuTierInfo",
    "CpuTierMetrics",
    "FanMetric",
    "InitializationFailedError",
    "InvalidArgumentError",
    "MacmonError",
    "MemMetrics",
    "Metrics",
    "PanicError",
    "Sampler",
    "SamplingFailedError",
    "SocInfo",
    "TempMetrics",
    "soc_info",
]
