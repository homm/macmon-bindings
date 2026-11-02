import CMacmon
import Foundation

public enum Macmon {
  public static func socInfo() throws -> SocInfo {
    var raw = macmon_soc_info_t()
    let status = macmon_get_soc_info(&raw)
    try MacmonError.check(status)
    defer {
      macmon_soc_info_free(&raw)
    }
    return SocInfo(raw)
  }
}

public enum MacmonError: Error, CustomStringConvertible, Sendable {
  case invalidArgument(String)
  case initializationFailed(String)
  case samplingFailed(String)
  case panic(String)
  case unknown(Int32, String)

  public var description: String {
    switch self {
    case .invalidArgument(let message):
      return message
    case .initializationFailed(let message):
      return message
    case .samplingFailed(let message):
      return message
    case .panic(let message):
      return message
    case .unknown(let status, let message):
      return "status \(status): \(message)"
    }
  }

  fileprivate static func check(_ status: macmon_status_t) throws {
    guard status == MACMON_STATUS_OK else {
      let message = lastErrorMessage()
      switch status {
      case MACMON_STATUS_INVALID_ARGUMENT:
        throw MacmonError.invalidArgument(message)
      case MACMON_STATUS_INIT_FAILED:
        throw MacmonError.initializationFailed(message)
      case MACMON_STATUS_SAMPLE_FAILED:
        throw MacmonError.samplingFailed(message)
      case MACMON_STATUS_PANIC:
        throw MacmonError.panic(message)
      default:
        throw MacmonError.unknown(Int32(status.rawValue), message)
      }
    }
  }

  private static func lastErrorMessage() -> String {
    guard let ptr = macmon_last_error_message() else {
      return "macmon returned an unknown error"
    }
    return String(cString: ptr)
  }
}

public final class Sampler {
  private var raw: OpaquePointer?

  public init() throws {
    var sampler: OpaquePointer?
    let status = macmon_sampler_new(&sampler)
    try MacmonError.check(status)
    guard let sampler else {
      throw MacmonError.initializationFailed("macmon returned success without a sampler handle")
    }
    self.raw = sampler
  }

  deinit {
    close()
  }

  public func close() {
    guard let raw else {
      return
    }
    macmon_sampler_free(raw)
    self.raw = nil
  }

  public func metrics() throws -> Metrics {
    guard let raw else {
      throw MacmonError.invalidArgument("sampler has already been released")
    }

    var result = macmon_metrics_t()
    let status = macmon_sampler_get_metrics(raw, &result)
    try MacmonError.check(status)
    defer {
      macmon_metrics_free(&result)
    }
    return Metrics(result)
  }
}

public struct Metrics: Sendable {
  public var temp: TempMetrics
  public var memory: MemMetrics
  public var fans: [FanMetric]
  public var cpuScaledRatio: Float
  public var cpuActiveRatio: Float
  public var cpuTiers: [CpuTierMetrics]
  public var gpuFreqMHz: UInt32
  public var gpuScaledRatio: Float
  public var gpuActiveRatio: Float
  public var cpuPower: Float
  public var gpuPower: Float
  public var anePower: Float
  public var chipPower: Float
  public var sysPower: Float
  public var ramPower: Float
  public var gpuRamPower: Float
  public var mediaPower: Float
  public var displayPower: Float
  public var batteryPower: Float
  public var dcInPower: Float

  fileprivate init(_ raw: macmon_metrics_t) {
    temp = TempMetrics(raw.temp)
    memory = MemMetrics(raw.memory)
    fans = buffer(from: raw.fans, count: raw.fans_len).map(FanMetric.init)
    cpuScaledRatio = raw.cpu_scaled_ratio
    cpuActiveRatio = raw.cpu_active_ratio
    cpuTiers = buffer(from: raw.cpu_tiers, count: raw.cpu_tiers_len).map(CpuTierMetrics.init)
    gpuFreqMHz = raw.gpu_freq_mhz
    gpuScaledRatio = raw.gpu_scaled_ratio
    gpuActiveRatio = raw.gpu_active_ratio
    cpuPower = raw.cpu_power
    gpuPower = raw.gpu_power
    anePower = raw.ane_power
    chipPower = raw.chip_power
    sysPower = raw.sys_power
    ramPower = raw.ram_power
    gpuRamPower = raw.gpu_ram_power
    mediaPower = raw.media_power
    displayPower = raw.display_power
    batteryPower = raw.battery_power
    dcInPower = raw.dc_in_power
  }
}

public struct CpuTierMetrics: Sendable {
  public var label: String
  public var freqMHz: UInt32
  public var scaledRatio: Float
  public var activeRatio: Float
  public var cores: [CpuCoreMetrics]

  fileprivate init(_ raw: macmon_cpu_tier_t) {
    label = string(from: raw.label)
    freqMHz = raw.freq_mhz
    scaledRatio = raw.scaled_ratio
    activeRatio = raw.active_ratio
    cores = buffer(from: raw.cores, count: raw.cores_len).map(CpuCoreMetrics.init)
  }
}

public struct CpuCoreMetrics: Sendable {
  public var dieID: Int
  public var coreID: Int
  public var freqMHz: UInt32
  public var scaledRatio: Float
  public var activeRatio: Float

  fileprivate init(_ raw: macmon_cpu_core_t) {
    dieID = raw.die_id
    coreID = raw.core_id
    freqMHz = raw.freq_mhz
    scaledRatio = raw.scaled_ratio
    activeRatio = raw.active_ratio
  }
}

public struct FanMetric: Sendable {
  public var name: String
  public var rpm: UInt32
  public var maxRpm: UInt32

  fileprivate init(_ raw: macmon_fan_t) {
    name = string(from: raw.name)
    rpm = raw.rpm
    maxRpm = raw.max_rpm
  }
}

public struct MemMetrics: Sendable {
  public var ramTotal: UInt64
  public var ramUsage: UInt64
  public var swapTotal: UInt64
  public var swapUsage: UInt64

  fileprivate init(_ raw: macmon_mem_metrics_t) {
    ramTotal = raw.ram_total
    ramUsage = raw.ram_usage
    swapTotal = raw.swap_total
    swapUsage = raw.swap_usage
  }
}

public struct TempMetrics: Sendable {
  public var cpuTempAvg: Float
  public var gpuTempAvg: Float

  fileprivate init(_ raw: macmon_temp_metrics_t) {
    cpuTempAvg = raw.cpu_temp_avg
    gpuTempAvg = raw.gpu_temp_avg
  }
}

public struct SocInfo: Sendable {
  public var macModel: String
  public var chipName: String
  public var memoryGB: UInt16
  public var cpuTiers: [CpuTierInfo]
  public var gpuCores: UInt8
  public var gpuFreqs: [UInt32]
  public var vm: Bool

  fileprivate init(_ raw: macmon_soc_info_t) {
    macModel = string(from: raw.mac_model)
    chipName = string(from: raw.chip_name)
    memoryGB = raw.memory_gb
    cpuTiers = buffer(from: raw.cpu_tiers, count: raw.cpu_tiers_len).map(CpuTierInfo.init)
    gpuCores = raw.gpu_cores
    gpuFreqs = buffer(from: raw.gpu_freqs, count: raw.gpu_freqs_len)
    vm = raw.vm
  }
}

public struct CpuTierInfo: Sendable {
  public var label: String
  public var cores: UInt8
  public var freqs: [UInt32]

  fileprivate init(_ raw: macmon_cpu_tier_info_t) {
    label = string(from: raw.label)
    cores = raw.cores
    freqs = buffer(from: raw.freqs, count: raw.freqs_len)
  }
}

private func string(from ptr: UnsafePointer<CChar>?) -> String {
  guard let ptr else {
    return ""
  }
  return String(cString: ptr)
}

private func buffer<T>(from ptr: UnsafeMutablePointer<T>?, count: Int) -> [T] {
  guard let ptr, count > 0 else {
    return []
  }
  return Array(UnsafeBufferPointer(start: UnsafePointer(ptr), count: count))
}

private func buffer<T>(from ptr: UnsafeMutablePointer<T>?, count: Int32) -> [T] {
  buffer(from: ptr, count: Int(count))
}

private func buffer<T>(from ptr: UnsafeMutablePointer<T>?, count: UInt) -> [T] {
  buffer(from: ptr, count: Int(count))
}
