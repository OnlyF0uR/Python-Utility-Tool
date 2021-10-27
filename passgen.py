from distutils import util
from cmd import Cmd
from tabulate import tabulate
import string
import random

from main import MainPrompt, BLUE, CYAN, RED, RESET, GREEN


class Prompt(Cmd):
    prompt = '{blue}program {cyan}(passgen) ➥ {reset}'.format(blue=BLUE, cyan=CYAN, reset=RESET)

    # We define the settings here
    settings = {
        'LENGTH': {
            'value': 16,
            'description': 'The length of the password',
        },
        'LOWERCASE': {
            'value': True,
            'description': 'Whether or not to include lowercase characters',
        },
        'UPPERCASE': {
            'value': True,
            'description': 'Whether or not to include uppercase characters',
        },
        'NUMBERS': {
            'value': True,
            'description': 'Whether or not to include lowercase numbers',
        },
        'SYMBOLS': {
            'value': False,
            'description': 'Whether or not to include lowercase symbols',
        },
        'DUPLICATES': {
            'value': False,
            'description': 'Whether or not to include duplicate characters',
        },
    }

    def do_help(self, _ln):
        print('\nAll commands that can be used within this module can be found below: ')
        cmd_list = [
            ['settings', 'View current settings'],
            ['set', 'Set the value of a setting'],
            ['generate', 'Generate a password'],
            ['back', 'Return to the previous prompt']
        ]
        print(tabulate(cmd_list, stralign="center", tablefmt="fancy_grid", headers=[BLUE + "Command" + RESET,
                                                                                    BLUE + "Description" + RESET]))

    def do_settings(self, _ln):
        settings_list = []

        for s in self.settings:
            settings_list.append([s, self.settings[s]['value'], self.settings[s]['description']])

        print(tabulate(settings_list, stralign="center", tablefmt="fancy_grid", headers=[BLUE + "Setting" + RESET,
                                                                                         BLUE + "Value" + RESET,
                                                                                         BLUE + "Description" + RESET]))

    def do_set(self, ln):
        arr = ln.split(' ')

        opt_name = arr.pop(0).upper()
        opt_value = ' '.join(arr)

        # Check if the specified setting exists
        if opt_name in self.settings:
            if opt_name == 'LENGTH':
                try:
                    self.settings['LENGTH']['value'] = int(opt_value)
                except ValueError:
                    print(RED + 'You must enter a number.')
                    return
            else:
                try:
                    self.settings[opt_name]['value'] = bool(util.strtobool(opt_value))
                except ValueError:
                    print(RED + 'You must enter either \'yes\' or \'no\'.')
                    return

            print(GREEN + 'Successfully updated the settings.')
        else:
            print(RED + 'That value cannot be set.')

    def do_generate(self, _ln):
        lng = self.settings['LENGTH']['value']
        if lng < 1:
            print(RED + 'You must at least generate one number.')
            return

        low = self.settings['LOWERCASE']['value']
        upp = self.settings['UPPERCASE']['value']
        num = self.settings['NUMBERS']['value']
        sym = self.settings['SYMBOLS']['value']
        if not low and not upp and not num and not sym:
            print(RED + 'You must at least select one set of allowed characters.')
            return

        char_set = ''

        if low:
            char_set += string.ascii_lowercase
        if upp:
            char_set += string.ascii_uppercase
        if num:
            char_set += string.digits
        if sym:
            char_set += string.punctuation

        # Convert string chararacter set to array
        char_set = list(char_set)

        if self.settings['DUPLICATES']['value']:
            pwd = ''
            for i in range(0, lng):
                pwd += char_set[random.randint(0, len(char_set) - 1)]

            print(GREEN + 'Password successfully generated: ' + pwd)
        else:
            random.shuffle(char_set)
            pwd_arr = random.choices(char_set, k=lng)

            print(GREEN + 'Password successfully generated: ' + ''.join(pwd_arr))

    def default(self, ln):
        ln = ln.lower()

        if ln == 'back' or ln == 'b':
            MainPrompt().cmdloop()
            return True

        print(RED + 'That\'s not a valid command. Use \'help\' for a list of commands.' + RESET)
