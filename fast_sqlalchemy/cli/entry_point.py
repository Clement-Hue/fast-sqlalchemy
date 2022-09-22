import argparse

from fast_sqlalchemy.cli.commands import GenerateProject

def handle_args(args):
    if args.commands == "new":
        generator = GenerateProject(args.project_name)
        generator.generate()


def main():
    parser = argparse.ArgumentParser(
        description="Create Fastapi application with SQLAlchemy with ease"
    )
    subparsers = parser.add_subparsers(dest="commands", help="List of command")
    new_project = subparsers.add_parser("new", help="Create a new project")
    new_project.add_argument("project_name", metavar="name",  type=str, help="Name of the new project")
    args = parser.parse_args()
    handle_args(args)


if __name__ == "__main__":
    main()
