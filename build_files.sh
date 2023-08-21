pip install -r requirements.txt

python cosproject/manage.py migrate
python cosproject/manage.py collectstatic
