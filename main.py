import os
from core.agent_config import config_agent
from core.config_config import config_model
from core.modelfile_writer import write_modelfile
from scripts.create_model import create_model


def main():
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    print("*** CONFIG TOOL")
    config_agent()
    config_model()
    write_modelfile()
    create_model()
    print("*** CONFIG IS COMPLETE")


if __name__ == "__main__":
    main()