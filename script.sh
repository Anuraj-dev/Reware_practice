rm -rf instance migrations
flask db init
flask db migrate
flask db upgrade
python3 ./sample_data.py