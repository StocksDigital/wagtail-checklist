# Wagtail Checlist Demo Website

Example app used to showcase a checklist app for Wagtail.

Setup requires `virtualenv` and Python 3

```
# Setup virtualenv, load demo data
./scripts/setup.sh
. env/bin/activate

# Run the server on localhost
cd demo
./manage.py runserver
```

No youvisit `localhost:8000/cms/pages/` to see the Wagtail admin. Username and password are `admin` / `z`
