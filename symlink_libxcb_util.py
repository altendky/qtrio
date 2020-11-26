import pathlib
import subprocess


completed_process = subprocess.run(
    ['ldconfig', '-p'],
    check=True,
    stdout=subprocess.PIPE,
)

print(completed_process.stdout)

[xcb_util_line] = [
    line
    for line in completed_process.stdout.decode('utf-8').splitlines()
    if 'libxcb-util' in line
]

existing = pathlib.Path(xcb_util_line.split('=>')[1].strip())
new = existing.with_suffix('.1')
new.symlink_to(existing)
