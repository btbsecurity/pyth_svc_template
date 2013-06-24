README.md

*** Note - the python scripts use win32 DLL calls. It has no idea how to find them, and apparently doesn't even look.
If you execute them outside of %windir% it will not work correctly. If you deploy them via PSEXEC, it won't matter, but it will if you
are testing it and debugging. ***

The script expects shellcode to be placed in the shellcode varible that is created from the msfpayload or msfvenom command.
It is expected to be used via deployment via PSEXEC in metasploit using the Custom::EXE parameter.
The reason why is that it is a piece of code that runs as a service. 

Requirements for building to EXE

Python (Tested on python 2.7 - standard python, not activestate - it might work)
PyWin32 Extensions for Python 2.7
Py2exe

Run: setup.py py2exe -c -b1

-c compresses the exe
-b1 makes it into a bundled exe

setup.py is built to drive the python script into the EXE. It will be in the .\dist\ directory built
Change the setup.py to point to a new source code if you want. It should be pretty easy.


