from django.conf import settings
import yaml


def get_export_string():
    with open(settings.ENVIRONMENT_FILE) as f:
        auth_params = {**yaml.load(f)}

    params = []
    for k, v in auth_params.items():
        params.append(f"export {k}={v};")
    return " ".join(params)
