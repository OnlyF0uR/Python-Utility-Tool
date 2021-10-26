from cmd import Cmd
from main import BLUE, CYAN, RED, RESET
from tabulate import tabulate
from main import MainPrompt


class Prompt(Cmd):
    prompt = '{blue}program {cyan}(encryption) ➥ {reset}'.format(blue=BLUE, cyan=CYAN, reset=RESET)
    settings = [
        {'name': 'ALGO', 'value': 'AES', 'required': True},
        {'name': 'TEXT', 'value': None, 'required': True},
        {'name': 'KEY', 'value': None, 'required': True},
    ]

    def do_help(self, arg: str):
        print('\nAll commands that can be used within this module can be found below: ' + CYAN)
        cmd_list = [
            ['settings', 'View current settings'],
            ['set', 'Set the value of a setting'],
            ['encrypt', 'Encrypt some text (configure first)'],
            ['decrypt', 'Decrypt some text (Configure first)'],
            ['back', 'Return to the previous prompt']
        ]
        print(tabulate(cmd_list, stralign="center", tablefmt="fancy_grid", headers=[BLUE + "Command" + RESET,
                                                                                    BLUE + "Description" + RESET]))

    def do_settings(self, ln):
        settings_list = []

        for setting in self.settings:
            settings_list.append([setting['name'], setting['value'], setting['required'] and 'Yes' or 'No'])

        print(tabulate(settings_list, stralign="center", tablefmt="fancy_grid", headers=[BLUE + "Setting" + RESET,
                                                                                         BLUE + "Value" + RESET,
                                                                                         BLUE + "Required" + RESET]))

    def do_set(self, ln):
        print('set a value')

    def do_encrypt(self):
        print('encrypt')

    def do_decrypt(self):
        print('decrypt')

    def default(self, ln):
        if ln == 'back' or ln == 'b':
            MainPrompt().cmdloop()
            return True

        print(RED + 'That\'s not a valid command. Use \'help\' for a list of commands.' + RESET)
