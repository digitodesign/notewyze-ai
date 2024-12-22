@echo off
python -m pip install --upgrade pip
python -m pip install setuptools wheel
python -m pip install distutils-precedence
python -m venv venv
call venv\Scripts\activate
pip install numpy==1.25.2
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
