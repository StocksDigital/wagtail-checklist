# Wagtail Checklist Demo Website

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

Now you can visit `localhost:8000/cms/pages/` to see the Wagtail admin. Username and password are `admin` / `z`

See `models.py` for the rules implementation. There are some rules already set up:

###BlogPage

- title
    - must not be blank
    - must be less than 20 characters
    - should be more than 10 characters
- body
    - must not be blank
    

####NewsPage

- title
    - must not be blank
    - must be less than 20 characters
    - should be more than 10 characters
- body
    - must not be blank
    - must not contain the word 'mongoose'
    - should contain the word 'news'
