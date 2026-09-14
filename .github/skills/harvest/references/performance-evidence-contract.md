# Performance Evidence Contract

A performance claim must identify workload, data size and shape, hardware/runtime configuration, baseline, candidate, measurement method, repetitions, observed distribution, resource use, and source commit. Record unmeasured claims as `UNVERIFIED`; never convert architectural preference into a benchmark result.

Cython is eligible only for a measured Python CPU hotspot. Ray is eligible only for a workload that benefits from Python-native distributed tasks or actors. PySpark is eligible only when distributed data requirements and platform constraints justify it. LP Emulator evidence must distinguish semantic behavior, module composition, partition execution, and cluster operations.
