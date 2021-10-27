from cmd import Cmd
from main import BLUE, CYAN, RED, RESET, GREEN
from tabulate import tabulate
from main import MainPrompt
from Crypto.Cipher import AES, DES, DES3, ARC2, Blowfish, CAST, Salsa20
from Crypto.Random import get_random_bytes
from base64 import b64encode, b64decode


def bytes_to_base64(byte_input):
    # Return the encoded bytes as base64
    return b64encode(byte_input).decode()


def base64_to_bytes(base64_input):
    # Return the decoded bytes
    return b64decode(base64_input)


def is_valid_byte(req, bt):
    # Decode to (hopefully) byte
    bt = base64_to_bytes(bt)

    # Check if it really is a byte
    if type(bt) != bytes:
        return False

    # Return whether or not the byte length is equal to the requirement
    return len(bt) == req


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
            'description': 'The key to use for encryption/decryption',
            'required': False
        },
        'TEXT': {
            'value': None,
            'description': 'The text to encrypt/decrypt',
            'required': True
        },
        'NONCE': {
            'value': None,
            'description': 'The nonce that can be obtained after encryption/decryption',
            'required': False
        },
        'MAC': {
            'value': None,
            'description': 'The mac that can be obtained after encryption',
            'required': False
        },
        'VERBOSE': {
            'value': False,
            'description': 'Output valuable (debug) logging data',
            'required': True
        }
    }

    def do_help(self, _ln):
        print('\nAll commands that can be used within this module can be found below: ')
        cmd_list = [
            ['info', 'Obtain information about this module'],
            ['settings', 'View current settings'],
            ['set', 'Set the value of a setting'],
            ['unset', 'Unset a certain setting'],
            ['encrypt', 'Encrypt some text (configure first)'],
            ['decrypt', 'Decrypt some text (Configure first)'],
            ['ciphers', 'Obtain a list with supported ciphers'],
            ['back', 'Return to the previous prompt']
        ]
        print(tabulate(cmd_list, stralign="center", tablefmt="fancy_grid", headers=[BLUE + "Command" + RESET,
                                                                                    BLUE + "Description" + RESET]))

    def do_info(self, _ln):
        print('todo')

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

    def do_unset(self, ln):
        opt_name = ln.upper()

        # Check if the specified setting exists
        if opt_name in self.settings:
            if self.settings[opt_name]['required']:
                print(RED + 'You cannot unset a required variable, try \'set\' instead.')
            else:
                # Split the input into key and value
                self.settings[opt_name]['value'] = None
                print(GREEN + 'Successfully updated the settings.')
        else:
            print(RED + 'That value cannot be unset.')

    def do_encrypt(self, ln):
        # Store the cipher setting (cph), and text setting (txt) in a variable for improved readability
        cph = self.settings['CIPHER']['value']
        txt = self.settings['TEXT']['value']

        if txt is None:
            print(RED + 'There was no text set.')
            return

        txt = txt.encode()

        # Symmetric Blocks
        if cph == 'AES':
            # Get or generate the key and nonce
            key = self.__get_byte_setting__('KEY', 16)
            nonce = self.__get_byte_setting__('NONCE', 15)

            # Create cipher
            cip = AES.new(key, AES.MODE_EAX, nonce=nonce)

            # Convert all the byte variables to base64
            ciptext = bytes_to_base64(cip.encrypt(txt))

            # We split this because we can then log the raw bytes with verbose
            dig = cip.digest()
            mac = bytes_to_base64(dig)

            # Check for verbose
            if self.settings['VERBOSE']['value']:
                print('Encrypting with: ')
                print(type(txt), txt)
                print(type(key), key)
                print(type(nonce), nonce)
                print(type(dig), dig)

            key = bytes_to_base64(key)
            nonce = bytes_to_base64(nonce)

            # Set some config values automatically
            self.settings['KEY']['value'] = key
            self.settings['NONCE']['value'] = nonce
            self.settings['TEXT']['value'] = ciptext
            self.settings['MAC']['value'] = mac

            # Print the result
            print('Key: {key}\nNonce: {nonce}\nMac: {mac}\nOutput: {output}'.format(key=key, nonce=nonce, mac=mac,
                                                                                    output=ciptext))
        elif cph == 'Single-DES':
            # Get or generate the key
            key = self.__get_byte_setting__('KEY', 8)

            # Create cipher
            cip = DES.new(key, DES.MODE_OFB)

            ciptext = bytes_to_base64(cip.iv + cip.encrypt(txt))
            key = bytes_to_base64(key)

            # Set some config values automatically
            self.settings['TEXT']['value'] = ciptext
            self.settings['KEY']['value'] = key

            # Print the result
            print('Key: {key}\nOutput: {output}'.format(key=key, output=ciptext))
        elif cph == 'Tiple-DES':
            def gen_des3_key():
                # So why do we do this?
                # Well according to the documentation this must be done to
                # ~ stop Triple DES from degrading to Single DES
                while 1:
                    try:
                        # Set the bits in a TDES key (des3_key to prevent shadowing)
                        des3_key = DES3.adjust_key_parity(get_random_bytes(24))
                        break
                    except ValueError:
                        pass

                # Finally, return the key
                return des3_key

            # Check for already configured key
            if self.settings['KEY']['value'] is not None:
                # Check if byte is valid
                if is_valid_byte(24, self.settings['KEY']['value']):
                    # Set the local key to the configured key
                    key = base64_to_bytes(self.settings['KEY']['value'])
                else:
                    # Generate a new key
                    key = gen_des3_key()
            else:
                key = gen_des3_key()

            cip = DES3.new(key, DES3.MODE_CFB)

            ciptext = bytes_to_base64(cip.iv + cip.encrypt(txt))
            key = bytes_to_base64(key)

            self.settings['TEXT']['value'] = ciptext
            self.settings['KEY']['value'] = key

            print('Key: {key}\nOutput: {output}'.format(key=key, output=ciptext))
        elif cph == 'RC2':
            key = self.__get_byte_setting__('KEY', 16)

            cip = ARC2.new(key, ARC2.MODE_CFB)

            ciptext = bytes_to_base64(cip.iv + cip.encrypt(txt))
            key = bytes_to_base64(key)

            self.settings['TEXT']['value'] = ciptext
            self.settings['KEY']['value'] = key

            print('Key: {key}\nOutput: {output}'.format(key=key, output=ciptext))
        elif cph == 'Blowfish':
            key = self.__get_byte_setting__('KEY', 32)

            cip = Blowfish.new(key, Blowfish.MODE_CBC)

            ciptext = bytes_to_base64(cip.iv + cip.encrypt(txt))
            key = bytes_to_base64(key)

            self.settings['TEXT']['value'] = ciptext
            self.settings['KEY']['value'] = key

            print('Key: {key}\nOutput: {output}'.format(key=key, output=ciptext))
        elif cph == 'CAST-128':
            key = self.__get_byte_setting__('KEY', 16)

            cip = CAST.new(key, CAST.MODE_OPENPGP)

            ciptext = bytes_to_base64(cip.encrypt(txt))
            key = bytes_to_base64(key)

            self.settings['TEXT']['value'] = ciptext
            self.settings['KEY']['value'] = key

            print('Key: {key}\nOutput: {output}'.format(key=key, output=ciptext))

        # Symmetric Streams
        elif cph == 'Salsa20':
            key = self.__get_byte_setting__('KEY', 32)

            cip = Salsa20.new(key)

            ciptext = bytes_to_base64(cip.nonce + cip.encrypt(txt))
            key = bytes_to_base64(key)

            self.settings['TEXT']['value'] = ciptext
            self.settings['KEY']['value'] = key

            print('Key: {key}\nOutput: {output}'.format(key=key, output=ciptext))
        else:
            print(RED + 'You configured an invalid cipher.')
            return

    def do_decrypt(self, ln):
        cph = self.settings['CIPHER']['value']
        txt = self.settings['TEXT']['value']

        if txt is None:
            print(RED + 'There was no text set.')
            return

        # Decode the encoded bytes
        txt = base64_to_bytes(txt)

        # Get the appropiate settings
        key = self.settings['KEY']['value']
        nonce = self.settings['NONCE']['value']
        mac = self.settings['MAC']['value']

        # Symmetric Blocks
        if cph == 'AES':
            if key is None or nonce is None:
                print(RED + '(AES) The following values are required: ', ' - KEY', ' - NONCE', ' - MAC', sep='\n')

            # Define the variables
            key = base64_to_bytes(key)
            nonce = base64_to_bytes(nonce)
            mac = base64_to_bytes(mac)

            # Check for verbose
            if self.settings['VERBOSE']['value']:
                print('Decrypting with: ')
                print(type(txt), txt)
                print(type(key), key)
                print(type(nonce), nonce)
                print(type(mac), mac)

            # Create cipher
            cip = AES.new(key, AES.MODE_EAX, nonce=nonce)

            try:
                # Verify using the mac and decrypt it
                ciptext = cip.decrypt_and_verify(txt, mac)
                print(GREEN + 'Decryption successful: ' + ciptext)
            except ValueError:
                print(RED + 'Decryption failed.')

        elif cph == 'Single-DES':
            print('todo')
        elif cph == 'Tiple-DES':
            print('todo')
        elif cph == 'RC2':
            print('todo')
        elif cph == 'Blowfish':
            print('todo')
        elif cph == 'CAST-128':
            print('todo')

        # Symmetric Streams
        elif cph == 'Salsa20':
            print('todo')
        else:
            print(RED + 'You configured an invalid cipher.')
            return

    def do_ciphers(self, _ln):
        print('-----[Symmetric]-----',
              'Block: AES, Single-DES, Triple-DES, RC2, Blowfish, CAST-128',
              'Stream: Salsa20', sep='\n', end='\n\n')

    def default(self, ln):
        ln = ln.lower()

        if ln == 'back' or ln == 'b':
            MainPrompt().cmdloop()
            return True

        print(RED + 'That\'s not a valid command. Use \'help\' for a list of commands.' + RESET)

    def __get_byte_setting__(self, setting, byte_value):
        # Check if the setting's value is set
        if self.settings[setting]['value'] is not None:
            # Check if the configured (byte) setting is valid
            if is_valid_byte(byte_value, self.settings[setting]['value']):
                # Set the key
                key = base64_to_bytes(self.settings[setting]['value'])
            else:
                # The key is invalid so generate a new one
                key = get_random_bytes(byte_value)
        else:
            # If the value is not set generate a new key
            key = get_random_bytes(byte_value)

        # Finally return the key
        return key
