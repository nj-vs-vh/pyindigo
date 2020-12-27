pip uninstall pyindigo -y
sudo rm -rf ./build ./dist ./src/pyindigo.egg-info

cd src/pyindigo_client
make reinstall
cd ../..

python setup.py install