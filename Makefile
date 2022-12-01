.PHONY: clean

VERSION := $(shell python setup.py --version)

version:
	@echo "$(VERSION)"

do-in-tests = @cd tests && poetry run

install:
	@poetry install --no-interaction --no-root
	@poetry run python setup.py develop

create_super_user:
	$(do-in-tests) python manage.py shell -c "from django.contrib.auth import get_user_model; get_user_model().objects.create_superuser(username='admin', password='password')"

migrate:
	$(do-in-tests) python manage.py makemigrations
	$(do-in-tests) python manage.py migrate

runserver:
	$(do-in-tests) python manage.py runserver

test:
	$(do-in-tests) pytest --ds=settings

shell:
	$(do-in-tests) python manage.py shell

pre-commit:
	@pre-commit run --all-files

clean-db:
	@rm -f tests/db.sqlite3

example: clean-db install migrate create_super_user runserver
