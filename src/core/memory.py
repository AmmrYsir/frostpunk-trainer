"""Memory manipulation module for Frostpunk Trainer."""

import ctypes
from ctypes import wintypes
from typing import Optional, List, Tuple

PROCESS_ALL_ACCESS = 0x1F0FFF
MEM_COMMIT = 0x1000
PAGE_READWRITE = 0x04
PAGE_EXECUTE_READWRITE = 0x40

kernel32 = ctypes.windll.kernel32

OpenProcess = kernel32.OpenProcess
OpenProcess.restype = wintypes.HANDLE
OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]

CloseHandle = kernel32.CloseHandle
CloseHandle.restype = wintypes.BOOL
CloseHandle.argtypes = [wintypes.HANDLE]

ReadProcessMemory = kernel32.ReadProcessMemory
ReadProcessMemory.restype = wintypes.BOOL
ReadProcessMemory.argtypes = [wintypes.HANDLE, wintypes.LPCVOID, wintypes.LPVOID, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]

WriteProcessMemory = kernel32.WriteProcessMemory
WriteProcessMemory.restype = wintypes.BOOL
WriteProcessMemory.argtypes = [wintypes.HANDLE, wintypes.LPVOID, wintypes.LPCVOID, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]

VirtualProtectEx = kernel32.VirtualProtectEx
VirtualProtectEx.restype = wintypes.BOOL
VirtualProtectEx.argtypes = [wintypes.HANDLE, wintypes.LPVOID, ctypes.c_size_t, wintypes.DWORD, wintypes.PDWORD]


class MODULEENTRY32(ctypes.Structure):
    _fields_ = [
        ('dwSize', wintypes.DWORD),
        ('th32ModuleID', wintypes.DWORD),
        ('th32ProcessID', wintypes.DWORD),
        ('GlblcntUsage', wintypes.DWORD),
        ('ProccntUsage', wintypes.DWORD),
        ('modBaseAddr', ctypes.c_void_p),
        ('modBaseSize', wintypes.DWORD),
        ('hModule', wintypes.HMODULE),
        ('szModule', ctypes.c_char * 260),
        ('szExePath', ctypes.c_char * 260)
    ]


class PROCESSENTRY32(ctypes.Structure):
    _fields_ = [
        ('dwSize', wintypes.DWORD),
        ('cntUsage', wintypes.DWORD),
        ('th32ProcessID', wintypes.DWORD),
        ('th32DefaultHeapID', ctypes.POINTER(wintypes.ULONG)),
        ('th32ModuleID', wintypes.DWORD),
        ('cntThreads', wintypes.DWORD),
        ('th32ParentProcessID', wintypes.DWORD),
        ('pcPriClassBase', wintypes.LONG),
        ('dwFlags', wintypes.DWORD),
        ('szExeFile', ctypes.c_char * 260)
    ]


class MemoryManager:
    """Manages process attachment, reading, and writing for game memory."""

    def __init__(self, process_name: str = "Frostpunk.exe"):
        self.process_name = process_name
        self.process_id: Optional[int] = None
        self.handle: Optional[wintypes.HANDLE] = None
        self.base_address: int = 0
        self.module_size: int = 0

    def attach(self) -> bool:
        """Finds process by name and acquires a full access process handle."""
        self.process_id = self._find_process_id(self.process_name)
        if not self.process_id:
            return False

        self.handle = OpenProcess(PROCESS_ALL_ACCESS, False, self.process_id)
        if not self.handle:
            return False

        self.base_address, self.module_size = self._get_module_info(self.process_id, self.process_name)
        return True

    def detach(self) -> None:
        """Closes open process handles."""
        if self.handle:
            CloseHandle(self.handle)
            self.handle = None
            self.process_id = None
            self.base_address = 0
            self.module_size = 0

    def read_bytes(self, address: int, size: int) -> Optional[bytes]:
        """Reads raw bytes from process memory."""
        if not self.handle:
            return None
        buffer = ctypes.create_string_buffer(size)
        bytes_read = ctypes.c_size_t()
        success = ReadProcessMemory(self.handle, ctypes.c_void_p(address), buffer, size, ctypes.byref(bytes_read))
        if success and bytes_read.value == size:
            return buffer.raw
        return None

    def write_bytes(self, address: int, data: bytes) -> bool:
        """Writes raw bytes to process memory with page protection restoration."""
        if not self.handle:
            return False
        old_protect = wintypes.DWORD()
        VirtualProtectEx(self.handle, ctypes.c_void_p(address), len(data), PAGE_EXECUTE_READWRITE, ctypes.byref(old_protect))
        
        bytes_written = ctypes.c_size_t()
        success = WriteProcessMemory(self.handle, ctypes.c_void_p(address), data, len(data), ctypes.byref(bytes_written))
        
        VirtualProtectEx(self.handle, ctypes.c_void_p(address), len(data), old_protect.value, ctypes.byref(old_protect))
        return bool(success and bytes_written.value == len(data))

    def read_int32(self, address: int) -> Optional[int]:
        raw = self.read_bytes(address, 4)
        return int.from_bytes(raw, byteorder='little', signed=True) if raw else None

    def read_int64(self, address: int) -> Optional[int]:
        raw = self.read_bytes(address, 8)
        return int.from_bytes(raw, byteorder='little', signed=True) if raw else None

    def read_float(self, address: int) -> Optional[float]:
        import struct
        raw = self.read_bytes(address, 4)
        return struct.unpack('<f', raw)[0] if raw else None

    def read_double(self, address: int) -> Optional[float]:
        import struct
        raw = self.read_bytes(address, 8)
        return struct.unpack('<d', raw)[0] if raw else None

    def write_int32(self, address: int, val: int) -> bool:
        return self.write_bytes(address, val.to_bytes(4, byteorder='little', signed=True))

    def write_int64(self, address: int, val: int) -> bool:
        return self.write_bytes(address, val.to_bytes(8, byteorder='little', signed=True))

    def write_float(self, address: int, val: float) -> bool:
        import struct
        return self.write_bytes(address, struct.pack('<f', val))

    def resolve_pointer_chain(self, base: int, offsets: List[int]) -> Optional[int]:
        """Resolves multi-level pointer chains."""
        current = base
        for offset in offsets:
            ptr = self.read_int64(current)
            if not ptr or ptr == 0:
                return None
            current = ptr + offset
        return current

    @staticmethod
    def _find_process_id(target_name: str) -> Optional[int]:
        snap = kernel32.CreateToolhelp32Snapshot(0x00000002, 0)
        entry = PROCESSENTRY32()
        entry.dwSize = ctypes.sizeof(PROCESSENTRY32)
        if kernel32.Process32First(snap, ctypes.byref(entry)):
            while True:
                name = entry.szExeFile.decode(errors='ignore')
                if name.lower() == target_name.lower():
                    kernel32.CloseHandle(snap)
                    return entry.th32ProcessID
                if not kernel32.Process32Next(snap, ctypes.byref(entry)):
                    break
        kernel32.CloseHandle(snap)
        return None

    @staticmethod
    def _get_module_info(pid: int, module_name: str) -> Tuple[int, int]:
        snap = kernel32.CreateToolhelp32Snapshot(0x00000008 | 0x00000010, pid)
        me = MODULEENTRY32()
        me.dwSize = ctypes.sizeof(MODULEENTRY32)
        if kernel32.Module32First(snap, ctypes.byref(me)):
            while True:
                if me.szModule.decode(errors='ignore').lower() == module_name.lower():
                    base = me.modBaseAddr if isinstance(me.modBaseAddr, int) else (me.modBaseAddr or 0)
                    size = me.modBaseSize
                    kernel32.CloseHandle(snap)
                    return base, size
                if not kernel32.Module32Next(snap, ctypes.byref(me)):
                    break
        kernel32.CloseHandle(snap)
        return 0, 0
