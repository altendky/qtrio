import sys
import typing


def main(
    input_file: typing.TextIO = sys.stdin, output_file: typing.TextIO = sys.stdout
) -> None:
    try:
        output_file.write("What is your name? ")
        output_file.flush()
        name = input_file.readline()[:-1]
        output_file.write(f"Hi {name}, welcome to the team!\n")
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":  # pragma: no cover
    main()
