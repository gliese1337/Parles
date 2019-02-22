from os import listdir, path
from subprocess import Popen, PIPE

for fname in listdir("tests"):
  print("Running", fname)
  with open(path.join("tests", fname), "r") as f:
    cproc = Popen(["python", "ParlesCompiler.py"], stdin=f, stdout=PIPE)
    vmproc = Popen(["python", "ParlesVM.py"], stdin=cproc.stdout, stdout=PIPE)
    output = vmproc.communicate()[0]
    print(output)