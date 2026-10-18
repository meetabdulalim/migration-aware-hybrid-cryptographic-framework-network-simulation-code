from dataclasses import dataclass
import random
from config import CONFIG


@dataclass
class QKDRequestResult:
    used: bool
    wait_ms: float
    success: bool
    reason: str
    consumed_bits: int
    generated_bits: float


class QKDResourcePool:
    def __init__(self, generation_rate_kbps=None, availability=None, initial_fill_ratio=None):
        self.capacity_bits = CONFIG['qkd_pool_capacity_bits']
        self.generation_rate_kbps = generation_rate_kbps if generation_rate_kbps is not None else CONFIG['qkd_generation_rate_kbps']
        self.availability = availability if availability is not None else CONFIG['qkd_availability']
        self.pool_bits = self.capacity_bits * (initial_fill_ratio if initial_fill_ratio is not None else CONFIG['qkd_initial_fill_ratio'])
        self.total_generated_bits = 0.0
        self.total_consumed_bits = 0

    @property
    def generation_rate_bits_per_ms(self):
        return (self.generation_rate_kbps * 1000.0) / 1000.0

    def replenish(self, elapsed_ms):
        if elapsed_ms <= 0:
            return 0.0
        generated = min(self.capacity_bits - self.pool_bits, self.generation_rate_bits_per_ms * elapsed_ms)
        self.pool_bits += generated
        self.total_generated_bits += generated
        return generated

    def try_acquire(self, key_bits, qkd_path_available, qkd_prob=None, allow_wait=True):
        availability = self.availability if qkd_prob is None else qkd_prob

        if not qkd_path_available:
            return QKDRequestResult(False, 0.0, False, 'no_qkd_path', 0, 0.0)

        if availability <= 0.0 or random.random() > availability:
            return QKDRequestResult(False, 0.0, False, 'qkd_outage', 0, 0.0)

        if self.pool_bits >= key_bits:
            self.pool_bits -= key_bits
            self.total_consumed_bits += int(key_bits)
            return QKDRequestResult(True, 0.0, True, 'pool_hit', int(key_bits), 0.0)

        deficit = key_bits - self.pool_bits
        if not allow_wait:
            return QKDRequestResult(False, 0.0, False, 'insufficient_pool', 0, 0.0)

        wait_ms = deficit / max(self.generation_rate_bits_per_ms * availability, 1e-9)
        if wait_ms > CONFIG['qkd_max_wait_ms']:
            return QKDRequestResult(False, wait_ms, False, 'wait_exceeds_threshold', 0, 0.0)

        generated = self.replenish(wait_ms)
        if self.pool_bits >= key_bits:
            self.pool_bits -= key_bits
            self.total_consumed_bits += int(key_bits)
            return QKDRequestResult(True, wait_ms, True, 'wait_then_use', int(key_bits), generated)

        return QKDRequestResult(False, wait_ms, False, 'still_insufficient', 0, generated)


def qkd_utilization_ratio(pool):
    denominator = max(pool.total_generated_bits + (CONFIG['qkd_pool_capacity_bits'] * CONFIG['qkd_initial_fill_ratio']), 1.0)
    return min(1.0, pool.total_consumed_bits / denominator)
