@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
python -c "import os; os.environ['KEYWORDS']='女生眼镜'; os.environ['TARGET_COUNT']='5'; from crawler_v4 import main; main()"
