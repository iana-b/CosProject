pip install -r requirements.txt

python3 ./cosproject/manage.py migrate
python3 ./cosproject/manage.py collectstatic
