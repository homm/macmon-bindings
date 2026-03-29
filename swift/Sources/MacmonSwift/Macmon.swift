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
  public let cpu_usage: [CpuUsage]
  public let gpu_usage: [GpuUsage]
  public let power: PowerMetrics
  public let memory: MemoryMetrics
  public let temperature: TemperatureMetrics

  fileprivate init(_ raw: macmon_metrics_t) {
    cpu_usage = buffer(from: raw.cpu_usage.ptr, count: raw.cpu_usage.len).map(CpuUsage.init)
    gpu_usage = buffer(from: raw.gpu_usage.ptr, count: raw.gpu_usage.len).map(GpuUsage.init)
    power = PowerMetrics(raw.power)
    memory = MemoryMetrics(raw.memory)
    temperature = TemperatureMetrics(raw.temp)
  }
}

public struct CpuUsage: Sendable {
  public let name: String
  public let units: UInt32
  public let frequencyMHz: UInt32
  public let usage: Float
  public let cores: [CoreUsage]

  fileprivate init(_ raw: macmon_cpu_usage_t) {
    let frequencies = buffer(from: raw.cores_freq_mhz, count: Int(raw.units))
    let usages = buffer(from: raw.cores_usage, count: Int(raw.units))

    name = string(from: raw.name)
    units = raw.units
    frequencyMHz = raw.freq_mhz
    usage = raw.usage
    cores = zip(frequencies, usages).map { CoreUsage(frequencyMHz: $0.0, usage: $0.1) }
  }
}

public struct CoreUsage: Sendable {
  public let frequencyMHz: UInt32
  public let usage: Float
}

public struct GpuUsage: Sendable {
  public let name: String
  public let units: UInt32
  public let frequencyMHz: UInt32
  public let usage: Float

  fileprivate init(_ raw: macmon_gpu_usage_t) {
    name = string(from: raw.name)
    units = raw.units
    frequencyMHz = raw.freq_mhz
    usage = raw.usage
  }
}

public struct PowerMetrics: Sendable {
  public let package: Float
  public let cpu: Float
  public let gpu: Float
  public let ram: Float
  public let gpuRAM: Float
  public let ane: Float
  public let board: Float
  public let battery: Float
  public let dcIn: Float

  fileprivate init(_ raw: macmon_power_metrics_t) {
    package = raw.package
    cpu = raw.cpu
    gpu = raw.gpu
    ram = raw.ram
    gpuRAM = raw.gpu_ram
    ane = raw.ane
    board = raw.board
    battery = raw.battery
    dcIn = raw.dc_in
  }
}

public struct MemoryMetrics: Sendable {
  public let ramTotal: UInt64
  public let ramUsage: UInt64
  public let swapTotal: UInt64
  public let swapUsage: UInt64

  fileprivate init(_ raw: macmon_mem_metrics_t) {
    ramTotal = raw.ram_total
    ramUsage = raw.ram_usage
    swapTotal = raw.swap_total
    swapUsage = raw.swap_usage
  }
}

public struct TemperatureMetrics: Sendable {
  public let cpuAverage: Float
  public let gpuAverage: Float

  fileprivate init(_ raw: macmon_temp_metrics_t) {
    cpuAverage = raw.cpu_avg
    gpuAverage = raw.gpu_avg
  }
}

public struct SocInfo: Sendable {
  public let macModel: String
  public let chipName: String
  public let memoryGB: UInt8
  public let cpuDomains: [CpuDomain]
  public let gpuCores: UInt8
  public let gpuFrequenciesMHz: [UInt32]

  fileprivate init(_ raw: macmon_soc_info_t) {
    macModel = string(from: raw.mac_model)
    chipName = string(from: raw.chip_name)
    memoryGB = raw.memory_gb
    cpuDomains = buffer(from: raw.cpu_domains, count: raw.cpu_domains_len).map(CpuDomain.init)
    gpuCores = raw.gpu_cores
    gpuFrequenciesMHz = buffer(from: raw.gpu_freqs_mhz, count: raw.gpu_freqs_len)
  }
}

public struct CpuDomain: Sendable {
  public let name: String
  public let units: UInt32
  public let frequenciesMHz: [UInt32]

  fileprivate init(_ raw: macmon_cpu_domain_t) {
    name = string(from: raw.name)
    units = raw.units
    frequenciesMHz = buffer(from: raw.freqs_mhz, count: raw.freqs_len)
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
