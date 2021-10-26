from cmd import Cmd
from main import BLUE, CYAN, RED, RESET, GREEN
from tabulate import tabulate
from main import MainPrompt
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from base64 import b64encode, b64decode


def bytes_to_base64(byte_input):
    return b64encode(byte_input).decode()


def base64_to_bytes(base64_input):
    return b64decode(base64_input).decode()


class Prompt(Cmd):
    prompt = '{blue}program {cyan}(encryption) ➥ {reset}'.format(blue=BLUE, cyan=CYAN, reset=RESET)

    # We define the settings here
    settings = {
        'CIPHER': {
            'value': 'AES',
            'description': 'The specific cipher, use \'ciphers\' for a complete list',
            'required': True
        },
        'KEY': {
            'value': None,
            'description': 'The key to use for decryption',
            'required': False
        },
        'TEXT': {
            'value': None,
            'description': 'The text to encrypt/decrypt',
            'required': True
        },
        'NONCE': {
            'value': None,
            'description': 'The nonce that can be obtained after encryption',
            'required': False
        },
        'MAC': {
            'value': None,
            'description': 'The mac that can be obtained after encryption',
            'required': False
        }
    }

    def do_help(self, _ln):
        print('\nAll commands that can be used within this module can be found below: ')
        cmd_list = [
            ['settings', 'View current settings'],
            ['set', 'Set the value of a setting'],
            ['encrypt', 'Encrypt some text (configure first)'],
            ['decrypt', 'Decrypt some text (Configure first)'],
            ['ciphers', 'Obtain a list with supported ciphers'],
            ['back', 'Return to the previous prompt']
        ]
        print(tabulate(cmd_list, stralign="center", tablefmt="fancy_grid", headers=[BLUE + "Command" + RESET,
                                                                                    BLUE + "Description" + RESET]))

    def do_settings(self, _ln):
        settings_list = []

        for s in self.settings:
            settings_list.append([s, self.settings[s]['value'], self.settings[s]['description'],
                                  self.settings[s]['required'] and 'Yes' or 'No'])

        print(tabulate(settings_list, stralign="center", tablefmt="fancy_grid", headers=[BLUE + "Setting" + RESET,
                                                                                         BLUE + "Value" + RESET,
                                                                                         BLUE + "Description" + RESET,
                                                                                         BLUE + "Required" + RESET]))

    def do_set(self, ln):
        arr = ln.split(' ')

        opt_name = arr.pop(0).upper()
        opt_value = ' '.join(arr)

        # Check if the specified setting exists
        if opt_name in self.settings:
            # Split the input into key and value
            self.settings[opt_name]['value'] = opt_value
            print(GREEN + 'Successfully updated the settings.')
        else:
            print(RED + 'That value cannot be set.')

    def do_encrypt(self, ln):
        # Store the cipher setting (cph), and text setting (txt) in a variable for improved readability
        cph = self.settings['CIPHER']['value']
        txt = self.settings['TEXT']['value']

        if cph is None or txt is None:
            print(RED + 'Please make sure all required parameters are configured.')
            return

        # Symmetric Blocks
        if cph == 'AES':
            key = get_random_bytes(16)
            nonce = get_random_bytes(15)

            cip = AES.new(key, AES.MODE_EAX, nonce=nonce)

            # Convert all the byte variables to base64
            ciptext = bytes_to_base64(cip.encrypt(txt.encode()))
            mac = bytes_to_base64(cip.digest())

            key = bytes_to_base64(key)
            nonce = bytes_to_base64(nonce)

            self.settings['KEY']['value'] = key
            self.settings['NONCE']['value'] = nonce
            self.settings['TEXT']['value'] = ciptext
            self.settings['MAC']['value'] = mac

            print('Key: {key}\nNonce: {nonce}\nMac: {mac}\nOutput: {output}'.format(key=key, nonce=nonce, mac=mac,
                                                                                    output=ciptext))
        elif cph == 'Single-Des':
            print('todo')
        elif cph == 'Tiple-Des':
            print('todo')
        elif cph == 'RC2':
            print('todo')
        elif cph == 'Blowfish':
            print('todo')
        elif cph == 'CAST-128':
            print('todo')

        # Symmetric Stremas
        elif cph == 'ChaCha20':
            print('todo')
        elif cph == 'XChaCha20':
            print('todo')
        elif cph == 'Salsa20':
            print('todo')
        elif cph == 'ARC4':
            print('todo')
        else:
            print(RED + 'You configured an invalid cipher.')
            return

    def do_decrypt(self, ln):
        cph = self.settings['CIPHER']['value']
        txt = self.settings['TEXT']['value']
        key = self.settings['KEY']['value']
        nonce = self.settings['NONCE']['value']
        mac = self.settings['MAC']['value']

        if cph is None or txt is None or key is None or nonce is None or mac is None:
            print(RED + 'Please make sure all required parameters are configured.')
            return

        print('decrypt')

    def do_ciphers(self, _ln):
        print('-----[Symmetric]-----',
              'Block: AES, Single-DES, Triple-DES, RC2, Blowfish, CAST-128',
              'Stream: ChaCha20, XChaCha20, Salsa20, ARC4', sep='\n', end='\n\n')

    def default(self, ln):
        ln = ln.lower()

        if ln == 'back' or ln == 'b':
            MainPrompt().cmdloop()
            return True

        print(RED + 'That\'s not a valid command. Use \'help\' for a list of commands.' + RESET)
