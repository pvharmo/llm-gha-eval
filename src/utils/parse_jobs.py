import streamlit as st
from typing import Dict, Any, Union


def parse_permissions(permissions: Union[str, Dict[str, str]]) -> str:
    if isinstance(permissions, str):
        return f" sets permissions to '{permissions}'."
    elif isinstance(permissions, dict):
        perm_list = [f"'{key}': {value}" for key, value in permissions.items()]
        if len(perm_list) == 1:
            return f" sets the following permission: {perm_list[0]}."
        elif len(perm_list) == 2:
            return f" sets the following permissions: {perm_list[0]} and {perm_list[1]}."
        else:
            return f" sets the following permissions: {', '.join(perm_list[:-1])}, and {perm_list[-1]}."
    else:
        return ""

def parse_defaults(defaults: Dict[str, Any]) -> str:
    result = ""
    if 'run' in defaults:
        run_defaults = defaults['run']
        if 'shell' in run_defaults:
            result += f" The default shell is '{run_defaults['shell']}'."
        if 'working-directory' in run_defaults:
            result += f" The default working directory is '{run_defaults['working-directory']}'."
    return result

def parse_strategy(strategy: Dict[str, Any]) -> str:
    result = " uses a matrix strategy"
    if 'matrix' in strategy:
        matrix = strategy['matrix']
        matrix_items = [f"'{key}': {value}" for key, value in matrix.items()]
        result += f" with the following dimensions: {', '.join(matrix_items)}."

        if 'include' in matrix:
            include_items = [f"{{{', '.join(f'{k}: {v}' for k, v in item.items())}}}" for item in matrix['include']]
            result += f" The strategy includes additional combinations: {', '.join(include_items)}."

        if 'exclude' in matrix:
            exclude_items = [f"{{{', '.join(f'{k}: {v}' for k, v in item.items())}}}" for item in matrix['exclude']]
            result += f" The strategy excludes the following combinations: {', '.join(exclude_items)}."

    if 'fail-fast' in strategy:
        result += f" Fail-fast is set to {strategy['fail-fast']}."

    if 'max-parallel' in strategy:
        result += f" The maximum number of parallel jobs is {strategy['max-parallel']}."

    return result

def parse_container(container: Union[str, Dict[str, Any]]) -> str:
    if isinstance(container, str):
        return f" runs in a container using the '{container}' image."
    elif isinstance(container, dict):
        result = f" runs in a container using the '{container['image']}' image."
        if 'env' in container:
            env_list = [f"'{key}': '{value}'" for key, value in container['env'].items()]
            result += f" The container environment includes: {', '.join(env_list)}."
        if 'ports' in container:
            result += f" The container exposes the following ports: {', '.join(map(str, container['ports']))}."
        if 'volumes' in container:
            result += f" The container mounts the following volumes: {', '.join(container['volumes'])}."
        return result
    else:
        return ""

def parse_services(services: Dict[str, Dict[str, Any]]) -> str:
    result = " uses the following service containers:"
    for service_name, service_config in services.items():
        result += f"\n- '{service_name}' (image: '{service_config.get('image', 'Not specified')}')"

        if 'credentials' in service_config:
            creds = service_config['credentials']
            result += f"\n  Credentials: username: '{creds.get('username', 'Not specified')}', password: '{'*' * len(creds.get('password', ''))}'"

        if 'env' in service_config:
            env_vars = [f"{k}: '{v}'" for k, v in service_config['env'].items()]
            result += f"\n  Environment variables: {', '.join(env_vars)}"

        if 'ports' in service_config:
            ports = service_config['ports']
            result += f"\n  Ports: {', '.join(map(str, ports))}"

        if 'volumes' in service_config:
            volumes = service_config['volumes']
            result += f"\n  Volumes: {', '.join(volumes)}"

        if 'options' in service_config:
            options = service_config['options']
            if isinstance(options, str):
                result += f"\n  Options: {options}"
            elif isinstance(options, list):
                result += f"\n  Options: {' '.join(options)}"
            elif isinstance(options, dict):
                option_items = [f"{k}: '{v}'" for k, v in options.items()]
                result += f"\n  Options: {', '.join(option_items)}"

    return result

def parse_secrets(job_config: Dict[str, Any]) -> str:
    result = ""
    secret_list = None
    if 'secrets' in job_config:
        secrets = job_config['secrets']
        if isinstance(secrets, list):
            secret_list = secrets
        elif isinstance(secrets, dict):
            if 'inherit' in secrets:
                inherit = secrets['inherit']
                if isinstance(inherit, bool) and inherit:
                    return " inherits all secrets."
                elif isinstance(inherit, list):
                    secret_list = inherit
                else:
                    secret_list = list(secrets.keys())
                    if 'inherit' in secret_list:
                        secret_list.remove('inherit')
            else:
                secret_list = list(secrets.keys())

        if secret_list is not None:
            if len(secret_list) == 1:
                result += f" uses the '{secret_list[0]}' secret."
            elif len(secret_list) == 2:
                result += f" uses the '{secret_list[0]}' and '{secret_list[1]}' secrets."
            else:
                result += f" uses the following secrets: {', '.join(secret_list[:-1])}, and {secret_list[-1]}."

    return result

def parse_job(job_name: str, job_config: Dict[str, Any]) -> str:
    result = f"The job '{job_name}'"
    first_sentece_complete = False

    if 'needs' in job_config:
        first_sentece_complete = True
        needs = job_config['needs']
        if isinstance(needs, str):
            result += f" needs the '{needs}' job to complete first."
        elif isinstance(needs, list):
            if len(needs) == 1:
                result += f" needs the '{needs[0]}' job to complete first."
            elif len(needs) == 2:
                result += f" needs the '{needs[0]}' and '{needs[1]}' jobs to complete first."
            else:
                result += f" needs the following jobs to complete first: {', '.join(needs[:-1])}, and {needs[-1]}."

    if 'if' in job_config:
        if first_sentece_complete:
            result += " This job"
        first_sentece_complete = True
        result += f" runs only if the condition '{job_config['if']}' is met."

    if 'runs-on' in job_config:
        if first_sentece_complete:
            result += " It"
        first_sentece_complete = True
        result += f" runs on '{job_config['runs-on']}'."

    if 'environment' in job_config:
        if first_sentece_complete:
            result += " It"
        first_sentece_complete = True
        env = job_config['environment']
        if isinstance(env, str):
            result += f" uses the '{env}' environment."
        elif isinstance(env, dict):
            result += f" uses the '{env.get('name')}' environment"
            if 'url' in env:
                result += f" with URL '{env['url']}'."
            else:
                result += "."

    if 'concurrency' in job_config:
        if first_sentece_complete:
            result += " It"
        first_sentece_complete = True
        concurrency = job_config['concurrency']
        if isinstance(concurrency, str):
            result += f" uses concurrency group '{concurrency}'."
        elif isinstance(concurrency, dict):
            result += f" uses concurrency group '{concurrency.get('group')}'"
            if 'cancel-in-progress' in concurrency:
                result += f" with cancel-in-progress set to {concurrency['cancel-in-progress']}."
            else:
                result += "."

    if 'outputs' in job_config:
        if first_sentece_complete:
            result += " It"
        first_sentece_complete = True
        outputs = job_config['outputs']
        output_list = [f"'{key}': {value}" for key, value in outputs.items()]
        if len(output_list) == 1:
            result += f" produces the following output: {output_list[0]}."
        elif len(output_list) == 2:
            result += f" produces the following outputs: {output_list[0]} and {output_list[1]}."
        else:
            result += f" produces the following outputs: {', '.join(output_list[:-1])}, and {output_list[-1]}."

    if 'env' in job_config:
        if first_sentece_complete:
            result += " It"
        first_sentece_complete = True
        env = job_config['env']
        env_list = [f"'{key}': '{value}'" for key, value in env.items()]
        if len(env_list) == 1:
            result += f" sets the following environment variable: {env_list[0]}."
        elif len(env_list) == 2:
            result += f" sets the following environment variables: {env_list[0]} and {env_list[1]}."
        else:
            result += f" sets the following environment variables: {', '.join(env_list[:-1])}, and {env_list[-1]}."

    if 'defaults' in job_config:
        if first_sentece_complete:
            result += " It"
        first_sentece_complete = True
        result += parse_defaults(job_config['defaults'])

    if 'timeout-minutes' in job_config:
        if first_sentece_complete:
            result += " It"
        first_sentece_complete = True
        result += f" times out after {job_config['timeout-minutes']} minutes."

    if 'strategy' in job_config:
        if first_sentece_complete:
            result += " It"
        first_sentece_complete = True
        result += parse_strategy(job_config['strategy'])

    if 'continue-on-error' in job_config:
        if first_sentece_complete:
            result += " It"
        first_sentece_complete = True
        result += f" is set to continue on error: {job_config['continue-on-error']}."

    if 'container' in job_config:
        if first_sentece_complete:
            result += " It"
        first_sentece_complete = True
        result += parse_container(job_config['container'])

    if 'services' in job_config:
        if first_sentece_complete:
            result += " It"
        first_sentece_complete = True
        result += parse_services(job_config['services'])

    if 'secrets' in job_config:
        if first_sentece_complete:
            result += " It"
        first_sentece_complete = True
        result += parse_secrets(job_config['secrets'])

    if 'with' in job_config:
        if first_sentece_complete:
            result += " It"
        first_sentece_complete = True
        with_params = job_config['with']
        param_list = [f"'{key}': '{value}'" for key, value in with_params.items()]
        if len(param_list) == 1:
            result += f" uses the following parameter: {param_list[0]}."
        elif len(param_list) == 2:
            result += f" uses the following parameters: {param_list[0]} and {param_list[1]}."
        else:
            result += f" uses the following parameters: {', '.join(param_list[:-1])}, and {param_list[-1]}."

    if 'permissions' in job_config:
        if first_sentece_complete:
            result += " It"
        first_sentece_complete = True
        result += parse_permissions(job_config['permissions'])

    return result if result[-1] == "." else result + "."

def parse_workflow_jobs(workflow_jobs: Dict[str, Dict[str, Any]]) -> str:
    parsed_jobs = [parse_job(job_name, job_config) for job_name, job_config in workflow_jobs.items()]
    return " ".join(parsed_jobs)
