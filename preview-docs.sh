cd docs/
rm -rf _build/
make html
open -a "Google Chrome" _build/html/index.html
cd -
