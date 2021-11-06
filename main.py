from cmd import Cmd
from tabulate import tabulate
from distutils import util


# Command class for the main prompt
class MainPrompt(Cmd):
    # Constructor
    def __init__(self, cls):
        super(MainPrompt, self).__init__()
        # Set the prompt
        self.prompt = '{blue}program {cyan}➥ {reset}'.format(blue=cls['BLUE'], cyan=cls['CYAN'], reset=cls['RESET'])
        # Define the colours for this class
        self.cls = cls

    # Help command
    def do_help(self, _ln):
        print('\nAll commands for this prompt can be found below: ')
        cmd_list = [
            ['encryption', 'Encrypt & Decrypt text'],
            ['hashing', 'Hash some text'],
            ['passgen', 'Create a rock(you) solid password'],
            ['collatz', 'Plot a collatz conjecture'],
            ['quit', 'Quit the prompt']
        ]
        # Print the command list in the form of a fancy table
        print(tabulate(cmd_list, stralign="center", tablefmt="fancy_grid",
                       headers=[self.cls['BLUE'] + "Command" + self.cls['RESET'],
                                self.cls['BLUE'] + "Description" + self.cls['RESET']]))

    # Function for non-registered commands
    def default(self, ln):
        if ln == 'quit' or ln == 'q':
            print('Goodbye! :)')
            return True

        # Check whether the command line is equal to one of our modules
        if ln in ['encryption', 'hashing', 'passgen', 'collatz']:
            # First we import the appropiate module/file
            mod = __import__(ln)
            # Then we get the main class and start the command loop
            getattr(mod, 'Prompt')(self.cls).cmdloop()
            return True
        else:
            print(self.cls['RED'] + 'That\'s not a valid command. Use \'help\' for a list of commands.' + self.cls['RESET'])


# Main function used to prevent unnecessary global scope variables
def main():
    print('Does your prompt support ANSI colours?')

    allow_colours = None
    while allow_colours is None:
        try:
            allow_colours = bool(util.strtobool(input('Enter \'yes\' or \'no\': ')))
        except ValueError:
            print('You must enter either \'yes\' or \'no\'.')

    colours = {'RESET': '', 'RED': '', 'GREEN': '', 'BLUE': '', 'CYAN': ''}

    # Check if colours are allowed
    if allow_colours:
        # Set the colours
        colours['RESET'] = '\u001b[0m'
        colours['RED'] = '\u001b[31m'
        colours['GREEN'] = '\u001b[32m'
        colours['BLUE'] = '\u001b[34m'
        colours['CYAN'] = '\u001b[36m'

    # Start the main prompt loop with an intro message
    MainPrompt(colours).cmdloop('Welcome! Type \'help\' to obtain a list of commands.')


if __name__ == '__main__':
    # Call the main function
    main()