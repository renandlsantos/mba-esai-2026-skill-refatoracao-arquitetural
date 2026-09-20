"""Reproduce the original fixture evidence without importing modified applications."""
import json,os,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1]
revision=json.loads((root/'reports/baseline-inventory.json').read_text())['revision']
for name,project,python in [('shop','code-smells-project','venv-shop'),('tasks','task-manager-api','venv-tasks'),('lms','ecommerce-api-legacy',None)]:
    target=root/'.work/baseline'/project;target.mkdir(parents=True,exist_ok=True)
    for filename in subprocess.check_output(['git','ls-tree','-r','--name-only',revision,project],cwd=root,text=True).splitlines():
        dest=target/Path(filename).relative_to(project);dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(subprocess.check_output(['git','show',revision+':'+filename],cwd=root))
    # Databases are created in a fresh disposable directory by copying sources there.
    import tempfile,shutil
    with tempfile.TemporaryDirectory(dir=root/'.work') as directory:
        isolated=Path(directory)/project;shutil.copytree(target,isolated,ignore=shutil.ignore_patterns('*.db','instance','__pycache__','node_modules'))
        output=root/'.work'/f'reproduced-baseline-{name}.json'
        if python:
            command=[str(root/'.work'/python/'bin/python'),str(root/'tests/baseline.py'),name,str(isolated),str(output)];env=None
        else:
            command=['node',str(root/'tests/baseline_node.cjs'),str(output),str(isolated/'src/AppManager.js')]
            env={**os.environ,'NODE_PATH':str(root/project/'node_modules')}
        subprocess.run(command,cwd=root,env=env,check=True)
print('Baseline reproduced in .work/reproduced-baseline-*.json; current application sources unchanged.')
