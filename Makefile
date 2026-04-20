ifneq (,$(wildcard .env))
    include .env
    export
endif

.PHONY: install lint \
        terraform-deploy terraform-destroy

PATH_INFRA	=	infra

install:
	uv sync --all-groups

lint:
	uv run pre-commit autoupdate
	cmd /C "set PYTHONIOENCODING=utf-8 && uv run pre-commit run --all-files"

run-pipeline:
	scripts\run_bruin.bat

run-app:
	uv run streamlit run app/main.py

infra-deploy:
	terraform -chdir=$(PATH_INFRA)/ init
	terraform -chdir=$(PATH_INFRA)/ validate
	terraform -chdir=$(PATH_INFRA)/ apply -auto-approve

infra-destroy:
	terraform -chdir=$(PATH_INFRA)/ destroy -auto-approve
