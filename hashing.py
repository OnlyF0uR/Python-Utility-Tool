from cmd import Cmd
from tabulate import tabulate

from Crypto.Hash import SHA256, SHA512, BLAKE2b, MD5, SHA1
from Crypto.Protocol.KDF import bcrypt, bcrypt_check, scrypt
from Crypto.Random import get_random_bytes
from base64 import b64encode, b64decode

from main import MainPrompt


def bytes_to_base64(byte_input):
    # Return the encoded bytes as base64
    return b64encode(byte_input).decode()


def base64_to_bytes(base64_input):
    # Return the decoded bytes
    return b64decode(base64_input)


class Prompt(Cmd):
    def __init__(self, cls):
        super(Prompt, self).__init__()
        self.prompt = '{blue}program {cyan}(hashing) ➥ {reset}'.format(blue=cls['BLUE'], cyan=cls['CYAN'],
                                                                       reset=cls['RESET'])
        self.cls = cls

    # We define the settings here
    settings = {
        'ALGORITHM': {
            'value': 'SHA-256',
            'description': 'The algorithm to use for hashing',
            'required': True
        },
        'TEXT': {
            'value': None,
            'description': 'The text to hash (a password e.g)',
            'required': True
        },
        'HASH': {
            'value': None,
            'description': 'Only used for comparing hashes',
            'required': False
        },
        'SALT': {
            'value': None,
            'description': 'The salt that gets generated when hashing',
            'required': False
        }
    }

    def do_help(self, _ln):
        print('\nAll commands that can be used within this module can be found below: ')
        cmd_list = [
            ['settings', 'View current settings'],
            ['set', 'Set the value of a setting'],
            ['unset', 'Unset a certain setting'],
            ['hash', 'Hash some text (configure first)'],
            ['check', 'Check if a hash (TEXT) matches a generate hash (HASH)'],
            ['hashes', 'Obtain a list with supported hashes'],
        ]
        print(tabulate(cmd_list, stralign="center", tablefmt="fancy_grid",
                       headers=[self.cls['BLUE'] + "Command" + self.cls['RESET'],
                                self.cls['BLUE'] + "Description" + self.cls['RESET']]))

    def do_settings(self, _ln):
        settings_list = []

        for s in self.settings:
            settings_list.append([s, self.settings[s]['value'], self.settings[s]['description'],
                                  self.settings[s]['required'] and 'Yes' or 'No'])

        print(tabulate(settings_list, stralign="center", tablefmt="fancy_grid",
                       headers=[self.cls['BLUE'] + "Setting" + self.cls['RESET'],
                                self.cls['BLUE'] + "Value" + self.cls['RESET'],
                                self.cls['BLUE'] + "Description" + self.cls['RESET'],
                                self.cls['BLUE'] + "Required" + self.cls['RESET']]))

    def do_set(self, ln):
        arr = ln.split(' ')

        opt_name = arr.pop(0).upper()
        opt_value = ' '.join(arr)

        # Check if the specified setting exists
        if opt_name in self.settings:
            # Split the input into key and value
            self.settings[opt_name]['value'] = opt_value
            print(self.cls['GREEN'] + 'Successfully updated the settings.')
        else:
            print(self.cls['RED'] + 'That value cannot be set.')

    def do_unset(self, ln):
        opt_name = ln.upper()

        # Check if the specified setting exists
        if opt_name in self.settings:
            if self.settings[opt_name]['required']:
                print(self.cls['RED'] + 'You cannot unset a required variable, try \'set\' instead.')
            else:
                # Split the input into key and value
                self.settings[opt_name]['value'] = None
                print(self.cls['GREEN'] + 'Successfully updated the settings.')
        else:
            print(self.cls['RED'] + 'That value cannot be unset.')

    def do_hash(self, _ln):
        algo = self.settings['ALGORITHM']['value']
        txt = self.settings['TEXT']['value']

        if txt is None:
            print(self.cls['RED'] + 'There was no text set.')
            return

        # Convert text to bytes
        txt = txt.encode()

        if algo == 'SHA-256':
            print('todo')
        elif algo == 'SHA-512':
            print('todo')
        elif algo == 'BLAKE2b':
            print('todo')
        elif algo == 'bcrypt':
            print('todo')
        elif algo == 'scrypt':
            print('todo')
        elif algo == 'MD5':
            print('todo')
        elif algo == 'SHA-1':
            print('todo')
        else:
            print(self.cls['RED'] + 'You configured an invalid algorithm.')
            return

    def do_check(self, _ln):
        algo = self.settings['ALGORITHM']['value']
        txt = self.settings['TEXT']['value']
        hsh = self.settings['HASH']['value']

        if txt is None or hsh is None:
            print(self.cls['RED'] + 'There was no text or hash set.')
            return

        # Convert text to bytes
        txt = txt.encode()

        if algo == 'SHA-256':
            print('todo')
        elif algo == 'SHA-512':
            print('todo')
        elif algo == 'BLAKE2b':
            print('todo')
        elif algo == 'bcrypt':
            print('todo')
        elif algo == 'scrypt':
            print('todo')
        elif algo == 'MD5':
            print('todo')
        elif algo == 'SHA-1':
            print('todo')
        else:
            print(self.cls['RED'] + 'You configured an invalid algorithm.')
            return

    def do_hashes(self, _ln):
        print(self.cls['BLUE'] + '-----[HASHES]-----', self.cls['RESET'] +
              'Be aware that some of the algorithms like MD5 and SHA-1 are not '
              'secure anymore and should never be used to hash valuable data. '
              'An algorithm such as BCrypt defaultly only supports strings of max '
              '72 bytes long, therefore we must encrypt the text with another hash (SHA256 in this example) '
              'to implement support for longer strings.', self.cls['CYAN'] +
              'Hashes: ' + self.cls['RESET'] + 'SHA-256, SHA-512, BLAKE2b, bcrypt, scrypt, MD5, SHA-1', sep='\n', end='\n\n')

    def default(self, ln):
        ln = ln.lower()

        if ln == 'back' or ln == 'b':
            MainPrompt(self.cls).cmdloop()
            return True

        print(self.cls['RED'] + 'That\'s not a valid command. Use \'help\' for a list of commands.' + self.cls['RESET'])
