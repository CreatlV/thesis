!/bin/bash
# Start JupyterLab

nohup jupyter-lab \
  --no-browser \
  --port=8888 \
  --ip=0.0.0.0 \
  --LabApp.token=Alex12345678! \
  --LabApp.password='' \
  --allow-root \
  &
