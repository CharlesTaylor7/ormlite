cd docs/
rm -rf _build/
pip install -r requirements.txt
make html
open -a "Google Chrome" _build/html/index.html
cd -
