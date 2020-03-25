# ==================================================
# IMPORTANT - do NOT add anything above 'help'
# It should always be the first command.
# ==================================================

.PHONY: help
help: ## This help.
	@echo "$$(tput setaf 6)$$(tput setab 0)═══════════════════════════════$$(tput sgr 0)"
	@echo "$$(tput setaf 6)$$(tput setab 0)  🤜  Make commands help  🤛   $$(tput sgr 0)"
	@echo "$$(tput setaf 6)$$(tput setab 0)═══════════════════════════════$$(tput sgr 0)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
	@echo "$$(tput setaf 6)$$(tput setab 0)═══════════════════════════════$$(tput sgr 0)"


# DEV COMMANDS
# ==================================================
.PHONY: django-run
django-run: ## Run django's dev server (tailing).
	docker-compose exec web bash -c "pipenv run python /usr/src/app/manage.py runserver 0:9000"

.PHONY: django-run-detached
django-run-detached: ## Run django's dev server (silently).
	docker-compose exec -d web bash -c "pipenv run python /usr/src/app/manage.py runserver 0:9000"

.PHONY: django-shell
django-shell: ## Drop into django's shell (with iphython).
	docker-compose exec web bash -c "pipenv run python /usr/src/app/manage.py shell_plus"

.PHONY: django-collectstatic
django-collectstatic: ## Collect static files.
	docker-compose exec web bash -c "pipenv run python /usr/src/app/manage.py collectstatic --no-input"

.PHONY: django-static
django-static: ## Compress SCSS and collect static files, clears staticfiles folder.
	docker-compose exec web bash -c "pipenv run python manage.py compress -f && pipenv run python manage.py collectstatic --no-input -i *.scss --clear"

.PHONY: django-test
django-test: ## Run django tests. (Use path=appname/filename::class::test) to narrow down
	docker-compose exec web pipenv run pytest -n 6 tests/$(path)

.PHONY: django-ui-test
django-run-test-server: ## Run django ui test server
	docker-compose -f docker-compose.test.yml -p market-access-test exec web-test bash -c "pipenv run python /usr/src/app/manage.py runserver 0:9000"

.PHONY: django-ui-test
django-ui-test: ## Run django ui tests.
	docker-compose -f docker-compose.test.yml -p market-access-test exec web-test bash -c "pipenv run pytest ui_tests"

.PHONY: django-ui-test
django-ui-test-with-server: ## Run locla server and run django ui tests against it.
	docker-compose -f docker-compose.test.yml -p market-access-test exec -d web-test bash -c "pipenv run python /usr/src/app/manage.py runserver 0:9000"
	docker-compose -f docker-compose.test.yml -p market-access-test exec web-test bash -c "pipenv run pytest ui_tests || pkill -f runserver"
	docker-compose -f docker-compose.test.yml -p market-access-test exec web-test bash -c "pkill -f runserver"

.PHONY: django-tests-coverage
django-tests-coverage: ## Run django tests and generate coverage report.
	docker-compose exec web bash -c "pipenv run pytest tests --cov=. --cov-report html"

.PHONY: git-hooks
git-hooks: ## Set up hooks for git.
	# === Setting up pre-commit hooks ========
	docker-compose exec web bash -c "cp tools/git_hooks/pre-commit.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit"
# ==================================================


# MIGRATION COMMANDS
# ==================================================
.PHONY: django-makemigrations
django-makemigrations: ## Create django migrations
	docker-compose exec web bash -c "pipenv run python /usr/src/app/manage.py makemigrations"

.PHONY: django-migrate
django-migrate: ## Apply django migrations.
	docker-compose exec web bash -c "pipenv run python /usr/src/app/manage.py migrate"

.PHONY: django-showmigrations
django-showmigrations: ## Show django migrations.
	docker-compose exec web bash -c "pipenv run python /usr/src/app/manage.py showmigrations"
# ==================================================


# UTIL COMMANDS
# ==================================================
.PHONY: flake8
flake8: ## Run pep8 checks on the project
	@echo "$$(tput setaf 3)🙈  Running flake8  🙈"
	@docker-compose exec web bash -c "pipenv run flake8 . --exclude=./.venv --count --max-line-length=120"

.PHONY: pip-install
pip-install: ## Install pip requirements inside the container.
	@echo "$$(tput setaf 3)🙈  Installing Pip Packages  🙈"
	@docker-compose exec web bash -c "pipenv sync --dev"

.PHONY: pip-deptree
pip-deptree: ## Output pip dependecy tree.
	@echo "$$(tput setaf 0)$$(tput setab 2)  🌳  Pip Dependency Tree  🌳   $$(tput sgr 0)"
	@docker-compose exec web bash -c "pipenv graph"

.PHONY: gen-secretkey
gen-secretkey: ## Generates a secret key (using django's util function)
	@docker-compose exec web bash -c "pipenv run python tools/secret_keygen.py"


# SSH COMMANDS (to debug via ssh)
# ==================================================
.PHONY: django-debug
django-debug: ## Run the SSH server on `web` - mainly use to expose python interpreter.
	ssh-keygen -R '[market-access.local]:9882'
	docker-compose exec -d web bash -c "/usr/bin/ssh-keygen -A; /usr/sbin/sshd -D"

.PHONY: django-ssh
django-ssh: ## Connect to `web` over SSH.
	ssh -p9882 root@market-access.local -t 'cd /usr/src/app; bash -l'
# ==================================================
