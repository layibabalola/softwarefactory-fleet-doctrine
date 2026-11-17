using System;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Text;

// Native helpers for MachineLoadSampler.ps1. Compiled once per sampler start.
public static class MachineLoadNative
{
    [StructLayout(LayoutKind.Sequential)]
    private struct ProcessBasicInformation
    {
        public IntPtr ExitStatus;
        public IntPtr PebBaseAddress;
        public IntPtr AffinityMask;
        public IntPtr BasePriority;
        public IntPtr UniqueProcessId;
        public IntPtr InheritedFromUniqueProcessId;
    }

    [DllImport("ntdll.dll")]
    private static extern int NtQueryInformationProcess(IntPtr handle, int infoClass, ref ProcessBasicInformation info, int length, out int returned);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern IntPtr OpenProcess(int access, bool inherit, int pid);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool ReadProcessMemory(IntPtr handle, IntPtr address, byte[] buffer, IntPtr size, out IntPtr read);

    [DllImport("kernel32.dll")]
    private static extern bool CloseHandle(IntPtr handle);

    [DllImport("kernel32.dll")]
    private static extern bool IsWow64Process(IntPtr handle, out bool wow64);

    private const int ProcessQueryInformation = 0x0400;
    private const int ProcessVmRead = 0x0010;

    // Current directory of another 64-bit process of the same user, read from its PEB
    // (RTL_USER_PROCESS_PARAMETERS.CurrentDirectory). Null when it cannot be read: protected or
    // other-user processes, 32-bit processes, a process that exited, or any read failure.
    public static string GetCurrentDirectory(int pid)
    {
        IntPtr handle = OpenProcess(ProcessQueryInformation | ProcessVmRead, false, pid);
        if (handle == IntPtr.Zero) return null;
        try
        {
            bool wow64;
            if (IsWow64Process(handle, out wow64) && wow64) return null;
            var info = new ProcessBasicInformation();
            int returned;
            if (NtQueryInformationProcess(handle, 0, ref info, Marshal.SizeOf(info), out returned) != 0) return null;
            IntPtr read;
            var pointer = new byte[8];
            if (!ReadProcessMemory(handle, info.PebBaseAddress + 0x20, pointer, (IntPtr)8, out read)) return null;
            IntPtr parameters = (IntPtr)BitConverter.ToInt64(pointer, 0);
            var unicodeString = new byte[16];
            if (!ReadProcessMemory(handle, parameters + 0x38, unicodeString, (IntPtr)16, out read)) return null;
            int length = BitConverter.ToUInt16(unicodeString, 0);
            IntPtr buffer = (IntPtr)BitConverter.ToInt64(unicodeString, 8);
            if (length <= 0 || length > 8192) return null;
            var text = new byte[length];
            if (!ReadProcessMemory(handle, buffer, text, (IntPtr)length, out read)) return null;
            return Encoding.Unicode.GetString(text);
        }
        catch
        {
            return null;
        }
        finally
        {
            CloseHandle(handle);
        }
    }

}
