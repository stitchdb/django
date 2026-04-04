# StitchDB for Django

## Install

```bash
pip install stitchdb
```

## Configure

In `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'stitchdb_django',
        'URL': os.environ.get('STITCHDB_URL', 'https://db.stitchdb.com'),
        'API_KEY': os.environ.get('STITCHDB_API_KEY', ''),
    }
}
```

No other setup needed. Run `python manage.py migrate` and use Django ORM as usual.
