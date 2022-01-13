import os


class Bcolors:
    """Enum of color chars."""
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


class Logger():
    """Class used to log in console."""

    def __init__(self, name: str) -> None:
        self.__name = name

        sep = 20 - len(name)
        self.__sep_beg = ' ' * (sep // 2)
        self.__sep_end = ' ' * (sep - len(self.__sep_beg))

    def __print(self, msg: str, color: str) -> None:
        print(f"{color}[{self.__sep_beg}{self.__name}{self.__sep_end}] " +
              f"{msg}{Bcolors.ENDC}")

    @staticmethod
    def title(msg: str) -> None:
        """Print with title format."""
        def print_line(line):
            print(Bcolors.OKCYAN + Bcolors.BOLD + line + Bcolors.ENDC)

        def padding(line, term_size):
            return " " * int((term_size - len(line)) / 2)

        try:
            term_size, _ = os.get_terminal_size()
        except OSError:
            term_size = 80

        print_line("=" * term_size)

        for line in msg.split('\n'):
            print_line(padding(line, term_size) + line)

        print_line("=" * term_size)

    def info(self, msg: str) -> None:
        """Log common information."""
        self.__print(msg, Bcolors.OKBLUE)

    def error(self, msg: str) -> None:
        """Log error msg."""
        self.__print(msg, Bcolors.FAIL)

    def success(self, msg: str) -> None:
        """Log success msg."""
        self.__print(msg, Bcolors.OKGREEN)

    def log(self, msg: str) -> None:
        """Log without type."""
        self.__print(msg, '')
