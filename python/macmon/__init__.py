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


def _float_list(ptr, length: int) -> list[float]:
    return [float(ptr[index]) for index in range(length)] if ptr != _ffi.NULL else []


@dataclass(frozen=True)
class CoreUsage:
    frequency_mhz: int
    usage: float


@dataclass(frozen=True)
class CpuUsage:
    name: str
    units: int
    frequency_mhz: int
    usage: float
    cores: list[CoreUsage]


@dataclass(frozen=True)
class GpuUsage:
    name: str
    units: int
    frequency_mhz: int
    usage: float


@dataclass(frozen=True)
class PowerMetrics:
    package: float
    cpu: float
    gpu: float
    ram: float
    gpu_ram: float
    ane: float
    board: float
    battery: float
    dc_in: float


@dataclass(frozen=True)
class MemoryMetrics:
    ram_total: int
    ram_usage: int
    swap_total: int
    swap_usage: int


@dataclass(frozen=True)
class TemperatureMetrics:
    cpu_average: float
    gpu_average: float


@dataclass(frozen=True)
class Metrics:
    cpu_usage: list[CpuUsage]
    gpu_usage: list[GpuUsage]
    power: PowerMetrics
    memory: MemoryMetrics
    temperature: TemperatureMetrics


@dataclass(frozen=True)
class CpuDomain:
    name: str
    units: int
    frequencies_mhz: list[int]


@dataclass(frozen=True)
class SocInfo:
    mac_model: str
    chip_name: str
    memory_gb: int
    cpu_domains: list[CpuDomain]
    gpu_cores: int
    gpu_frequencies_mhz: list[int]


def _cpu_usage_from_raw(raw) -> CpuUsage:
    frequencies = _uint32_list(raw.cores_freq_mhz, int(raw.units))
    usages = _float_list(raw.cores_usage, int(raw.units))
    return CpuUsage(
        name=_decode_string(raw.name),
        units=int(raw.units),
        frequency_mhz=int(raw.freq_mhz),
        usage=float(raw.usage),
        cores=[
            CoreUsage(frequency_mhz=frequency, usage=usage)
            for frequency, usage in zip(frequencies, usages)
        ],
    )


def _gpu_usage_from_raw(raw) -> GpuUsage:
    return GpuUsage(
        name=_decode_string(raw.name),
        units=int(raw.units),
        frequency_mhz=int(raw.freq_mhz),
        usage=float(raw.usage),
    )


def _power_metrics_from_raw(raw) -> PowerMetrics:
    return PowerMetrics(
        package=float(raw.package),
        cpu=float(raw.cpu),
        gpu=float(raw.gpu),
        ram=float(raw.ram),
        gpu_ram=float(raw.gpu_ram),
        ane=float(raw.ane),
        board=float(raw.board),
        battery=float(raw.battery),
        dc_in=float(raw.dc_in),
    )


def _memory_metrics_from_raw(raw) -> MemoryMetrics:
    return MemoryMetrics(
        ram_total=int(raw.ram_total),
        ram_usage=int(raw.ram_usage),
        swap_total=int(raw.swap_total),
        swap_usage=int(raw.swap_usage),
    )


def _temperature_metrics_from_raw(raw) -> TemperatureMetrics:
    return TemperatureMetrics(
        cpu_average=float(raw.cpu_avg),
        gpu_average=float(raw.gpu_avg),
    )


def _metrics_from_raw(raw) -> Metrics:
    return Metrics(
        cpu_usage=[
            _cpu_usage_from_raw(raw.cpu_usage.ptr[index])
            for index in range(int(raw.cpu_usage.len))
        ],
        gpu_usage=[
            _gpu_usage_from_raw(raw.gpu_usage.ptr[index])
            for index in range(int(raw.gpu_usage.len))
        ],
        power=_power_metrics_from_raw(raw.power),
        memory=_memory_metrics_from_raw(raw.memory),
        temperature=_temperature_metrics_from_raw(raw.temp),
    )


def _cpu_domain_from_raw(raw) -> CpuDomain:
    return CpuDomain(
        name=_decode_string(raw.name),
        units=int(raw.units),
        frequencies_mhz=_uint32_list(raw.freqs_mhz, int(raw.freqs_len)),
    )


def _soc_info_from_raw(raw) -> SocInfo:
    return SocInfo(
        mac_model=_decode_string(raw.mac_model),
        chip_name=_decode_string(raw.chip_name),
        memory_gb=int(raw.memory_gb),
        cpu_domains=[
            _cpu_domain_from_raw(raw.cpu_domains[index])
            for index in range(int(raw.cpu_domains_len))
        ],
        gpu_cores=int(raw.gpu_cores),
        gpu_frequencies_mhz=_uint32_list(raw.gpu_freqs_mhz, int(raw.gpu_freqs_len)),
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
    "CoreUsage",
    "CpuDomain",
    "CpuUsage",
    "GpuUsage",
    "InitializationFailedError",
    "InvalidArgumentError",
    "MacmonError",
    "MemoryMetrics",
    "Metrics",
    "PanicError",
    "PowerMetrics",
    "Sampler",
    "SamplingFailedError",
    "SocInfo",
    "TemperatureMetrics",
    "soc_info",
]
