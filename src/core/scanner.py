"""Pattern scanner and memory signature utility."""

import re
from typing import Optional, List, Tuple
from .memory import MemoryManager


class PatternScanner:
    """Scans process memory modules for byte patterns and IDA-style signatures."""

    def __init__(self, memory_manager: MemoryManager):
        self.mem = memory_manager

    def parse_ida_pattern(self, pattern: str) -> Tuple[bytes, bytes]:
        """
        Converts an IDA pattern string (e.g. '48 8B 05 ? ? ? ? 48 85 C0')
        into (pattern_bytes, mask_bytes).
        """
        tokens = pattern.strip().split()
        pattern_bytes = bytearray()
        mask_bytes = bytearray()
        for tok in tokens:
            if tok in ('?', '??'):
                pattern_bytes.append(0)
                mask_bytes.append(0)
            else:
                pattern_bytes.append(int(tok, 16))
                mask_bytes.append(0xFF)
        return bytes(pattern_bytes), bytes(mask_bytes)

    def scan_module(self, pattern: str) -> Optional[int]:
        """Scans the entire game module for the first occurrence of the pattern."""
        if not self.mem.handle or not self.mem.base_address:
            return None

        data = self.mem.read_bytes(self.mem.base_address, self.mem.module_size)
        if not data:
            return None

        pat_bytes, mask_bytes = self.parse_ida_pattern(pattern)
        match_idx = self._boyer_moore_search(data, pat_bytes, mask_bytes)
        if match_idx is not None:
            return self.mem.base_address + match_idx
        return None

    @staticmethod
    def _boyer_moore_search(data: bytes, pat: bytes, mask: bytes) -> Optional[int]:
        plen = len(pat)
        dlen = len(data)
        if plen > dlen:
            return None

        # Build regex for wildcards
        regex_parts = []
        for p, m in zip(pat, mask):
            if m == 0xFF:
                regex_parts.append(re.escape(bytes([p])))
            else:
                regex_parts.append(b'.')
        regex = re.compile(b''.join(regex_parts), re.DOTALL)
        m = regex.search(data)
        return m.start() if m else None
