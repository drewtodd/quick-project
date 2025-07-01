import argparse

def main():
    parser = argparse.ArgumentParser(description="CLI Entry Point")
    args = parser.parse_args()
    print("CLI is working!")

if __name__ == "__main__":
    main()
