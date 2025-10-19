"""
{% if cookiecutter.use_subdirectory.lower() == "y" or cookiecutter.use_subdirectory.lower() == "yes" %}
{{ cookiecutter.update({ "build_directory": cookiecutter.build_directory + "/build-" + cookiecutter.project_slug }) }}
{% endif %}
"""