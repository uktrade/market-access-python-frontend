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
	docker-compose exec web bash -c "./manage.py runserver 0:9001"

.PHONY: django-run-detached
django-run-detached: ## Run django's dev server (silently).
	docker-compose exec -d web bash -c "./manage.py runserver 0:9001"

.PHONY: django-shell
django-shell: ## Drop into django's shell (with iphython).
	docker-compose exec web bash -c "./manage.py shell_plus"

.PHONY: django-collectstatic
django-collectstatic: ## Collect static files.
	docker-compose exec web bash -c "./manage.py collectstatic --no-input"

.PHONY: django-static
django-static: ## Compress SCSS and collect static files, clears staticfiles folder.
	docker-compose exec web ./manage.py collectstatic --no-input -i *.scss --clear

.PHONY: django-test
django-test: ## Run django tests. (Use path=appname/filename::class::test) to narrow down
	docker-compose exec web pytest -n 6 tests/$(path)

.PHONY: test-frontend
test-frontend: ## Run django ui tests.
	docker-compose exec web bash -c "pytest test_frontend/$(path)"

.PHONY: django-tests-coverage
django-tests-coverage: ## Run django tests and generate coverage report.
	docker-compose exec web bash -c "pytest tests --cov-report term"

.PHONY: git-hooks
git-hooks: ## Set up hooks for git.
	# === Setting up pre-commit hooks ========
	docker-compose exec web bash -c "cp tools/git_hooks/pre-commit.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit"
# ==================================================


# MIGRATION COMMANDS
# ==================================================
.PHONY: django-makemigrations
django-makemigrations: ## Create django migrations
	docker-compose exec web bash -c "./manage.py makemigrations"

.PHONY: django-migrate
django-migrate: ## Apply django migrations.
	docker-compose exec web bash -c "./manage.py migrate"

.PHONY: django-showmigrations
django-showmigrations: ## Show django migrations.
	docker-compose exec web bash -c "./manage.py showmigrations"
# ==================================================


# UTIL COMMANDS
# ==================================================
.PHONY: flake8
flake8: ## Run pep8 checks on the project
	@echo "$$(tput setaf 3)🙈  Running flake8  🙈"
	@docker-compose exec web flake8 --count

__timestamp = $(shell date +%F_%H-%M)
.PHONY: pip-install
pip-install: ## Install pip requirements inside the container.
	@echo "$$(tput setaf 3)🙈  Installing Pip Packages  🙈$$(tput sgr 0)"
	@docker-compose exec web poetry lock
	@docker-compose exec web poetry install
	@docker-compose exec web sed -i '1i# ======\n# DO NOT EDIT - use pyproject.toml instead!\n# Generated: $(__timestamp)\n# ======' requirements.txt
	@docker-compose exec web sed -i '1i# ======\n# DO NOT EDIT - use pyproject.toml instead!\n# Generated: $(__timestamp)\n# ======' requirements-dev.txt

.PHONY: pip-deptree
pip-deptree: ## Output pip dependecy tree.
	@echo "$$(tput setaf 0)$$(tput setab 2)  🌳  Pip Dependency Tree  🌳   $$(tput sgr 0)"
	@docker-compose exec web bash -c "poetry show --tree"

.PHONY: pip-updates
pip-updates: ## Output available updates for packages.
	@echo "$$(tput setaf 2)  📦  Available Updates  📦   $$(tput sgr 0)"
	@docker-compose exec web bash -c "poetry show -o"

.PHONY: gen-secretkey
gen-secretkey: ## Generates a secret key (using django's util function)
	@docker-compose exec web bash -c "./tools/secret_keygen.py"

.PHONY: dev
dev: django-debug ## Runs the ssh server on docker and gulp dev
	@echo "$$(tput setaf 3)🙈  Dev dev...  🙈$$(tput sgr 0)"
	@echo "$$(tput setaf 10)=========="
	@echo "$$(tput setaf 10)Hints:"
	@echo "$$(tput setaf 10)  - you may need to run [npm install] prior to this command"
	@echo "$$(tput setaf 10)==========$$(tput sgr 0)"
	@npm run dev



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
