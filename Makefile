.PHONY: clean

VERSION := $(shell python setup.py --version)

version:
	@echo "$(VERSION)"

do-in-tests = @cd tests && poetry run

#
# Dev
#
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

pre-commit:
	@pre-commit run --all-files

clean-db:
	@rm -f tests/db.sqlite3

example: clean-db install migrate create_super_user runserver

#
# Release
#
clean:
	@rm -fr build/
	@rm -fr dist/
	@rm -fr *.egg-info
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +

dist: clean
	@python setup.py -q sdist
	@twine check dist/django-fsm-admin-lite-${VERSION}.tar.gz

# release: dist
# 	@twine upload -r testpypi dist/django-fsm-admin-lite-$(VERSION).tar.gz
# 	@twine upload dist/django-fsm-admin-lite-$(VERSION).tar.gz
