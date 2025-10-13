import argparse
import json
from pathlib import Path

from pydantic import BaseModel, Field

from {{cookiecutter.project_slug}}.fileio import process_existing_file_name, read_config_file


class Arguments(BaseModel):
    config: str = Field(
        default="./data/config.json", description="File containing all arguments"
    )
    name: str = Field(
        default="alice",
        description="Name of the node of the current instance of {{cookiecutter.project_slug}}",
    )
    port: int = Field(
        default=5555, description="Port to bind the ZeroMQ socket to"
    )
    peer_ip: str = Field(
        default="127.0.0.1", description="IP address of the peer to connect to"
    )
    peer_port: int = Field(
        default=5555, description="Port of the peer to connect to"
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
        path = process_existing_file_name(
            kwargs.config, folders=["data"], formats=[".json"]
        )
        config = read_config_file(path)
    else:
        config = dict()

    # KW overwrites file
    config.update(kwargs.__dict__)

    # Validate user settings against the model
    args = Arguments(**config)
    return args

