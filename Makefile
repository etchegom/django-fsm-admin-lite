.PHONY: clean

VERSION := $(shell python setup.py --version)

version:
	@echo "$(VERSION)"

#
# Dev
#
install:
	@poetry install
	@poetry run python setup.py develop

create_super_user:
	@cd tests && poetry run python manage.py shell -c "from django.contrib.auth import get_user_model; get_user_model().objects.create_superuser(username='admin', password='password')"

runserver:
	@cd tests && poetry run python manage.py migrate && poetry run python manage.py runserver

test:
	@pytest

pre-commit:
	@pre-commit run --all-files

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
# 	@twine upload dist/django-fsm-admin-lite-$(VERSION).tar.gz
