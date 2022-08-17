import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Create Fastapi application with SQLAlchemy with ease"
    )
    parser.add_argument("--env", help="Specify the environment configuration to use")
    parser.parse_args()


if __name__ == "__main__":
    main()
