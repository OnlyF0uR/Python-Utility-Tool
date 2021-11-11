from cmd import Cmd
from tabulate import tabulate

from Crypto.Hash import SHA256, SHA512, BLAKE2b, MD5, SHA1
from Crypto.Protocol.KDF import bcrypt, scrypt
from Crypto.Random import get_random_bytes
from base64 import b64encode

from main import MainPrompt
from encryption import bytes_to_base64, base64_to_bytes


class Prompt(Cmd):
    def __init__(self, cls):
        super(Prompt, self).__init__()
        self.prompt = '{blue}program {cyan}(hashing) ➥ {reset}'.format(blue=cls['BLUE'], cyan=cls['CYAN'], reset=cls['RESET'])
        self.cls = cls

    # We define the settings here
    settings = {
        'ALGO': {
            'value': 'SHA-256',
            'description': 'Use \'algos\' for a complete list',
            'required': True
        },
        'TEXT': {
            'value': None,
            'description': 'The text to hash (a password e.g)',
            'required': True
        },
        'HASH': {
            'value': None,
            'description': 'Hash to compare to (Only for comparing)',
            'required': False
        },
        'SALT': {
            'value': None,
            'description': 'Additional safeguard value',
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
            ['compare', 'Compare a hash (setting: TEXT) with a generated hash (setting: HASH)'],
            ['algos', 'Obtain a list with supported hashing algorithms'],
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
        txt = self.settings['TEXT']['value']

        if txt is None:
            print(self.cls['RED'] + 'There was no text set.')
            return

        algo = self.settings['ALGO']['value']
        salt = self.settings['SALT']['value']  # Is allowed to be None

        if salt is not None:
            salt = base64_to_bytes(salt)

        # Generate a hash
        res, salt = self.__hash_text__(algo, txt.encode(), salt)
        if res is None:
            print(self.cls['RED'] + 'You configured an invalid algorithm. (Case sensitive)')
            return

        self.settings['HASH']['value'] = res

        if salt is not None:
            self.settings['SALT']['value'] = salt
            print('--=({algo})=--\nSalt: {salt}\nHash: {output}'.format(algo=algo, salt=salt, output=res))
        else:
            print('--=({algo})=--\nHash: {output}'.format(algo=algo, output=res))

    def do_compare(self, _ln):
        txt = self.settings['TEXT']['value']
        hsh = self.settings['HASH']['value']

        if txt is None or hsh is None:
            print(self.cls['RED'] + 'There was no text or hash set.')
            return

        algo = self.settings['ALGO']['value']
        salt = self.settings['SALT']['value'] if self.settings['SALT']['value'] is None else base64_to_bytes(self.settings['SALT']['value'])

        if algo == 'bcrypt' or algo == 'scrypt':
            if salt is None:
                print(self.cls['RED'] + 'A salt is required for that algorithm.')
                return

        res, salt = self.__hash_text__(algo, txt.encode(), salt)
        if res is None:
            print(self.cls['RED'] + 'You configured an invalid algorithm. (Case sensitive)')
            return

        if res == hsh:
            print(self.cls['GREEN'] + '--=({algo})=--\nHashed & Compared: IDENTICAL HASH'.format(algo=algo))
        else:
            print(self.cls['RED'] + '--=({algo})=--\nHashed & Compared: DIFFERENT HASH'.format(algo=algo))

    def do_algos(self, _ln):
        print(self.cls['BLUE'] + '-----[ALGORITHMS]-----', self.cls['RESET'] +
              'Be aware that some of the algorithms like MD5 and SHA-1 are not '
              'secure anymore and should never be used to hash valuable data. '
              'An algorithm such as bcrypt defaultly only supports strings of max '
              '72 bytes long, therefore we must encrypt the text with another hash (SHA256 in this instance) '
              'to implement support for longer strings.', self.cls['CYAN'] +
              'Algorithms: ' + self.cls['RESET'] + 'SHA-256, SHA-512, BLAKE2b, bcrypt, scrypt, MD5, SHA-1', sep='\n', end='\n\n')

    def default(self, ln):
        ln = ln.lower()

        if ln == 'back' or ln == 'b':
            MainPrompt(self.cls).cmdloop()
            return True

        print(self.cls['RED'] + 'That\'s not a valid command. Use \'help\' for a list of commands.' + self.cls['RESET'])

    def __hash_text__(self, algo, txt, salt):
        hash_res = None

        if algo == 'SHA-256':
            hash_res = SHA256.new(txt).hexdigest()
        elif algo == 'SHA-512':
            hash_res = SHA512.new(txt).hexdigest()
        elif algo == 'BLAKE2b':
            hash_res = BLAKE2b.new(key=txt).hexdigest()
        elif algo == 'bcrypt':
            if salt is None:
                salt = get_random_bytes(16)

            # bcrypt only support input of 72 bytes long, although we can use a workaround for this
            # we can first hash the text with something else and encode it to base64
            base = b64encode(SHA256.new(txt).digest())
            hash_res = bcrypt(base, cost=12, salt=salt).decode()  # Cost: 4 to 31, at least 12 is recommended

            salt = bytes_to_base64(salt)
        elif algo == 'scrypt':
            if salt is None:
                salt = get_random_bytes(16)

            # key_len = length of key, N = costs, r = block size, p = parallelization
            hash_res = bytes_to_base64(scrypt(txt, salt, key_len=16, N=2**16, r=8, p=1))

            salt = bytes_to_base64(salt)
        elif algo == 'MD5':
            hash_res = MD5.new(txt).hexdigest()
        elif algo == 'SHA-1':
            hash_res = SHA1.new(txt).hexdigest()

        return hash_res, salt
