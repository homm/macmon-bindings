import unittest
from unittest.mock import patch

import macmon


class ConversionTests(unittest.TestCase):
    def test_metrics_copy_core_identity_ratios_fans_and_zero_values(self):
        ffi = macmon._ffi
        raw = ffi.new("macmon_metrics_t *")
        label = ffi.new("char[]", b"P")
        cores = ffi.new("macmon_cpu_core_t[]", [
            {"die_id": 1, "core_id": 3, "freq_mhz": 3200,
             "scaled_ratio": 0.25, "active_ratio": 0.5},
        ])
        tiers = ffi.new("macmon_cpu_tier_t[]", [
            {"label": label, "freq_mhz": 3200, "scaled_ratio": 0.25,
             "active_ratio": 0.5, "cores_len": 1, "cores": cores},
        ])
        name = ffi.new("char[]", b"fan0")
        fans = ffi.new("macmon_fan_t[]", [
            {"name": name, "rpm": 1200, "max_rpm": 3000},
            {"name": name, "rpm": 0, "max_rpm": 0},
        ])
        raw.cpu_tiers, raw.cpu_tiers_len = tiers, 1
        raw.fans, raw.fans_len = fans, 2
        raw.temp.cpu_temp_avg = 42
        raw.temp.gpu_temp_avg = 0
        raw.cpu_scaled_ratio, raw.cpu_active_ratio = 0.25, 0.5
        raw.gpu_freq_mhz = 900
        raw.gpu_scaled_ratio, raw.gpu_active_ratio = 0.125, 0.75
        raw.cpu_power, raw.gpu_power, raw.ane_power = 1, 2, 3
        raw.chip_power, raw.sys_power = 6, 9
        raw.ram_power, raw.gpu_ram_power = 0.5, 0.25
        raw.media_power = 0.75
        raw.display_power, raw.battery_power, raw.dc_in_power = 4, 5, 6
        raw.memory.ram_total = 2**34

        def initialize(out):
            out[0] = ffi.cast("macmon_sampler_t *", 1)
            return 0

        def sample(handle, out):
            out[0] = raw[0]
            return 0

        def release(out):
            out[0] = ffi.new("macmon_metrics_t *")[0]
            cores[0].core_id = 0
            label[0] = b"X"

        with patch.object(macmon, "_lib") as lib:
            lib.MACMON_STATUS_OK = 0
            lib.macmon_sampler_new.side_effect = initialize
            lib.macmon_sampler_get_metrics.side_effect = sample
            lib.macmon_metrics_free.side_effect = release
            with macmon.Sampler() as sampler:
                metrics = sampler.metrics()
            lib.macmon_metrics_free.assert_called_once()
            lib.macmon_sampler_free.assert_called_once()

        self.assertEqual(metrics.cpu_tiers, [
            macmon.CpuTierMetrics("P", 3200, 0.25, 0.5, [
                macmon.CpuCoreMetrics(1, 3, 3200, 0.25, 0.5),
            ]),
        ])
        self.assertEqual((metrics.cpu_scaled_ratio, metrics.cpu_active_ratio), (0.25, 0.5))
        self.assertEqual((metrics.gpu_freq_mhz, metrics.gpu_scaled_ratio, metrics.gpu_active_ratio),
                         (900, 0.125, 0.75))
        self.assertEqual((metrics.cpu_power, metrics.gpu_power, metrics.ane_power,
                          metrics.chip_power, metrics.sys_power, metrics.ram_power,
                          metrics.gpu_ram_power, metrics.media_power), (1, 2, 3, 6, 9, 0.5, 0.25, 0.75))
        self.assertEqual((metrics.display_power, metrics.battery_power, metrics.dc_in_power),
                         (4, 5, 6))
        self.assertEqual(metrics.memory.ram_total, 2**34)
        self.assertEqual(metrics.temp, macmon.TempMetrics(42.0, 0.0))
        self.assertEqual(metrics.fans, [macmon.FanMetric("fan0", 1200, 3000),
                                       macmon.FanMetric("fan0", 0, 0)])

    def test_soc_info_copies_tiers_frequencies_and_vm_flag(self):
        ffi = macmon._ffi
        model = ffi.new("char[]", b"VirtualMac")
        chip = ffi.new("char[]", b"Apple Silicon")
        label = ffi.new("char[]", b"CPU")
        freqs = ffi.new("uint32_t[]", [600, 3200])
        gpu_freqs = ffi.new("uint32_t[]", [400, 900])
        tiers = ffi.new("macmon_cpu_tier_info_t[]", [
            {"label": label, "cores": 8, "freqs_len": 2, "freqs": freqs},
        ])

        def fill(out):
            out.mac_model, out.chip_name, out.memory_gb = model, chip, 16
            out.cpu_tiers, out.cpu_tiers_len = tiers, 1
            out.gpu_cores, out.gpu_freqs, out.gpu_freqs_len = 10, gpu_freqs, 2
            out.vm = True
            return 0

        def release(out):
            out[0] = ffi.new("macmon_soc_info_t *")[0]
            freqs[0] = 0
            gpu_freqs[0] = 0

        with patch.object(macmon, "_lib") as lib:
            lib.MACMON_STATUS_OK = 0
            lib.macmon_get_soc_info.side_effect = fill
            lib.macmon_soc_info_free.side_effect = release
            info = macmon.soc_info()
            lib.macmon_soc_info_free.assert_called_once()

        self.assertEqual(info, macmon.SocInfo("VirtualMac", "Apple Silicon", 16,
                                            [macmon.CpuTierInfo("CPU", 8, [600, 3200])],
                                            10, [400, 900], True))


if __name__ == "__main__":
    unittest.main()
