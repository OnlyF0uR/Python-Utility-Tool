from distutils import util
from cmd import Cmd
from tabulate import tabulate
import matplotlib.pyplot as plt

from main import MainPrompt, BLUE, CYAN, RED, RESET, GREEN


class Prompt(Cmd):
    prompt = '{blue}program {cyan}(collatz) ➥ {reset}'.format(blue=BLUE, cyan=CYAN, reset=RESET)

    # We define the settings here
    settings = {
        'NUMBER': {
            'value': None,
            'description': 'The number that should be thrown into 3x+1',
        },
        'THRESHOLD': {
            'value': 20000,
            'description': 'Stop after x iterations',
        }
    }

    def do_help(self, _ln):
        print('\nAll commands that can be used within this module can be found below: ')
        cmd_list = [
            ['settings', 'View current settings'],
            ['set', 'Set the value of a setting'],
            ['calculate', 'Calculate the amount of steps']
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
            try:
                num = int(opt_value)
                if num < 1:
                    raise ValueError()
                self.settings[opt_name]['value'] = num
            except ValueError:
                print(RED + 'You must enter a number that is greater than 0.')
                return

            print(GREEN + 'Successfully updated the settings.')
        else:
            print(RED + 'That value cannot be set.')

    def do_calculate(self, _ln):
        num = self.settings['NUMBER']['value']
        thres = self.settings['THRESHOLD']['value']

        success = True

        values = [num]
        s = 0  # Amount of steps
        while num != 1:
            # Check if number is even
            if num % 2 == 0:
                num /= 2
            else:
                num = num * 3 + 1
            s += 1  # Python does not support i++ :(
            values.append(num)

            if s == thres:
                success = False
                break

        if success:
            print(GREEN + 'Finished in ' + str(s) + ' steps.' + RESET)
        else:
            print(GREEN + 'Finished in ' + str(s) + ' steps. (Threshold reached)' + RESET)

        while True:
            try:
                plot_result = bool(util.strtobool(input('Would you like to plot the result? Enter \'yes\' or \'no\': ')))
                break
            except ValueError:
                print(RED + 'You must enter either \'yes\' or \'no\': ')

        if plot_result:
            # plt.plot(list(range(0, len(values))), values)
            plt.plot(values)
            plt.title('Collatz Conjecture (3x+1)')
            # plt.xticks(np.arange(num, len(values), 1.0))
            plt.ylabel('Value of n')
            plt.show()

    def default(self, ln):
        ln = ln.lower()

        if ln == 'back' or ln == 'b':
            MainPrompt().cmdloop()
            return True

        print(RED + 'That\'s not a valid command. Use \'help\' for a list of commands.' + RESET)
