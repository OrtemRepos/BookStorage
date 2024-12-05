from dishka import make_container

from src.config import Config
from src.providers import CLIAdapter, CLIAdapterProvider

config = Config()

container = make_container(CLIAdapterProvider(), context={Config: config})

def main(*args, **kwargs):
    app = container.get(CLIAdapter)
    app.run()

if __name__ == "__main__":
    main()
