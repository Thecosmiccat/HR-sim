"""
Build script for HR Management Simulator
Run: python build_exe.py
Requires: pip install pyinstaller
"""
import subprocess
import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
main_script = os.path.join(script_dir, "new_sim.py")

cmd = [
    sys.executable, "-m", "PyInstaller",
    "--onefile",           # Single exe file
    "--windowed",          # No console window (GUI app)
    "--name", "HR_Simulator",
    "--noconfirm",         # Overwrite without asking
    main_script,
]

print("Building with command:")
print(" ".join(cmd))
print()

result = subprocess.run(cmd, cwd=script_dir)
if result.returncode == 0:
    print("\n✓ Build successful!")
    print(f"  EXE is at: {os.path.join(script_dir, 'dist', 'HR_Simulator.exe')}")
    print(f"  Save files will be stored next to the .exe in a 'saves' folder.")
else:
    print(f"\n✗ Build failed with code {result.returncode}")
    sys.exit(1)
