test:
	pytest tests

release:
ifndef VERSION
	$(error "Usage: make release VERSION=0.1.9")
endif
	git checkout main
	git pull
	echo "__version__ = '$(VERSION)'" > sapiens/__version__.py
	git add sapiens/__version__.py
	git commit -m "Set version to $(VERSION)"
	git push
	make dist
	twine upload dist/sapiens-$(VERSION)*
	@echo "Create a new release version on: https://github.com/Merck/Sapiens/releases"

dist:
	python setup.py sdist bdist_wheel	

