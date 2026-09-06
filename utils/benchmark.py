"""Runtime / memory / API-latency measurements for the CLI footer."""

from __future__ import annotations

import time
from typing import Dict, Optional

from utils.market_data import api_response_seconds


def _rss_mb() -> Optional[float]:
    try:
        import resource

        usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        # Linux reports KB; macOS reports bytes.
        if usage > 10_000_000:
            return usage / (1024 * 1024)
        return usage / 1024.0
    except Exception:
        return None


class Benchmark:
    """Stopwatch for a single analysis run."""

    def __init__(self) -> None:
        self._start = time.perf_counter()
        self._tracemalloc_started = False
        try:
            import tracemalloc

            tracemalloc.start()
            self._tracemalloc_started = True
        except Exception:
            self._tracemalloc_started = False

    def snapshot(self) -> Dict[str, float]:
        """Return runtime seconds, peak memory MB, and API seconds."""
        runtime = time.perf_counter() - self._start
        peak_mb = _rss_mb() or 0.0
        if self._tracemalloc_started:
            try:
                import tracemalloc

                _, traced_peak = tracemalloc.get_traced_memory()
                traced_mb = traced_peak / (1024 * 1024)
                peak_mb = max(peak_mb, traced_mb)
            except Exception:
                pass
        return {
            "runtime_s": runtime,
            "memory_mb": peak_mb,
            "api_s": api_response_seconds(),
        }
