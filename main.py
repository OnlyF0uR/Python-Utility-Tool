from cmd import Cmd
from tabulate import tabulate


# Some colours, yes with a 'u'
RESET = '\u001b[0m'
RED = '\u001b[31m'
GREEN = '\u001b[32m'
BLUE = '\u001b[34m'
CYAN = '\u001b[36m'


class MainPrompt(Cmd):
    # Specify the line cursor
    prompt = '{blue}program {cyan}➥ {reset}'.format(blue=BLUE, cyan=CYAN, reset=RESET)

    def do_help(self, arg: str):
        print('\nAll commands for this prompt can be found below: ')
        cmd_list = [
            ['encryption', 'Encrypt & Decrypt text'],
            ['hashing', 'Hash some text'],
            ['passgen', 'Create a rock(you) solid password'],
            ['collatz', 'Plot a collatz conjecture'],
            ['quit', 'Quit the prompt']
        ]
        print(tabulate(cmd_list, stralign="center", tablefmt="fancy_grid", headers=[BLUE + "Command" + RESET, BLUE + "Description" + RESET]))

    def default(self, ln):
        if ln == 'quit' or ln == 'q':
            print('Goodbye! :)')
            return True

        if ln in ['encryption', 'hashing', 'passgen', 'collatz']:
            # First we import the appropiate module/file
            mod = __import__(ln)
            # Then we get the main class and start the command loop
            getattr(mod, 'Prompt')(self).cmdloop()
            return True
        else:
            print(RED + 'That\'s not a valid command. Use \'help\' for a list of commands.' + RESET)


if __name__ == '__main__':
    # Start the main prompt loop
    MainPrompt().cmdloop('Welcome! Type \'help\' to obtain a list of commands.')
