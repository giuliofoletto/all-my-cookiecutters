import argparse
import json
from pathlib import Path

from pydantic import BaseModel, Field

from {{cookiecutter.project_slug}}.fileio import process_existing_file_name, read_config_file


class Arguments(BaseModel):
    config: str = Field(default = "./data/config.json", description="File containing all arguments")
    # EXAMPLE FIELDS
    data_file: str = Field(
        default="./data/data.npy", description="File containing input data to analyze"
    )
    name: str = Field(default="", description="Name to give to the analysis")
    final: bool = Field(default=False, description="Final execution")
    output_dir: str = Field(
        default="./results", description="Folder where to save the results"
    )


def add_model(parser, model):
    """
    Add Pydantic model to an ArgumentParser.
    Taken from https://stackoverflow.com/questions/72741663/argument-parser-from-a-pydantic-model and modified.
    """
    fields = model.model_fields
    for name, field in fields.items():
        command_string = "--" + name.replace("_", "-")
        # handle flags
        if field.annotation == bool:
            if field.default:
                action = "store_false"
            else:
                action = "store_true"
            parser.add_argument(
                command_string,
                dest=name,
                default=argparse.SUPPRESS,
                action=action,
                help=field.description,
            )
        else:
            parser.add_argument(
                command_string,
                dest=name,
                type=field.annotation,
                default=argparse.SUPPRESS,
                help=field.description,
            )


def arguments():
    parser = argparse.ArgumentParser()
    add_model(parser, Arguments)
    kwargs = parser.parse_args()

    # Create an object of user settings
    if hasattr(kwargs, "config"):
        path = process_existing_file_name(kwargs.config, folders=["data"], formats=[".json"])
        config = read_config_file(path)
    else:
        config = dict()

    # KW overwrites file
    config.update(kwargs.__dict__)

    # Validate user settings against the model
    args = Arguments(**config)
    return args


def get_label(string):
    return string.replace("_", " ").capitalize()


def pretty_string_from_dict(dictionary):
    res = ""
    for key, value in dictionary.items():
        if isinstance(value, dict):
            res += "\n" + get_label(key) + ":\n"
            res += pretty_string_from_dict(value)
        elif "sigma_" in key:
            continue
        elif "sigma_" + key in dictionary:
            res += (
                get_label(key)
                + ":\t"
                + str(value)
                + " +- "
                + str(dictionary["sigma_" + key])
                + "\n"
            )
        else:
            res += get_label(key) + ":\t" + str(value) + "\n"
    return res