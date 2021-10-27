from cmd import Cmd
from tabulate import tabulate

from Crypto.Cipher import AES, DES, DES3, ARC2, Blowfish, CAST, Salsa20
from Crypto.Random import get_random_bytes
from base64 import b64encode, b64decode

from main import MainPrompt, BLUE, CYAN, RED, RESET, GREEN


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
        'IV': {
            'value': None,
            'description': 'The initialization vector that can be obtained after encryption',
            'required': False
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
            mac = bytes_to_base64(cip.digest())

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

            # Translate some variables into base, including the encrypted bytes
            ciptext = bytes_to_base64(cip.encrypt(txt))
            key = bytes_to_base64(key)
            iv = bytes_to_base64(cip.iv)

            # Set some config values automatically
            self.settings['TEXT']['value'] = ciptext
            self.settings['KEY']['value'] = key
            self.settings['IV']['value'] = iv

            # Print the result
            print('Key: {key}\nIV: {iv}\nOutput: {output}'.format(key=key, iv=iv, output=ciptext))
        elif cph == 'Triple-DES':
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

            # Translate some variables into base, including the encrypted bytes
            ciptext = bytes_to_base64(cip.encrypt(txt))
            key = bytes_to_base64(key)
            iv = bytes_to_base64(cip.iv)

            self.settings['TEXT']['value'] = ciptext
            self.settings['KEY']['value'] = key
            self.settings['IV']['value'] = iv

            print('Key: {key}\nIV: {iv}\nOutput: {output}'.format(key=key, iv=iv, output=ciptext))
        elif cph == 'RC2':
            key = self.__get_byte_setting__('KEY', 16)

            cip = ARC2.new(key, ARC2.MODE_CFB)

            ciptext = bytes_to_base64(cip.encrypt(txt))
            key = bytes_to_base64(key)
            iv = bytes_to_base64(cip.iv)

            self.settings['TEXT']['value'] = ciptext
            self.settings['KEY']['value'] = key
            self.settings['IV']['value'] = iv

            print('Key: {key}\nIV: {iv}\nOutput: {output}'.format(key=key, iv=iv, output=ciptext))
        elif cph == 'Blowfish':
            key = self.__get_byte_setting__('KEY', 32)

            cip = Blowfish.new(key, Blowfish.MODE_CBC)

            ciptext = bytes_to_base64(cip.encrypt(txt))
            key = bytes_to_base64(key)
            iv = bytes_to_base64(cip.iv)

            self.settings['TEXT']['value'] = ciptext
            self.settings['KEY']['value'] = key
            self.settings['IV']['value'] = iv

            print('Key: {key}\nIV: {iv}\nOutput: {output}'.format(key=key, iv=iv, output=ciptext))
        elif cph == 'CAST-128':
            key = self.__get_byte_setting__('KEY', 16)

            cip = CAST.new(key, CAST.MODE_OPENPGP)

            ciptext = bytes_to_base64(cip.encrypt(txt))
            key = bytes_to_base64(key)
            iv = bytes_to_base64(cip.iv)

            self.settings['TEXT']['value'] = ciptext
            self.settings['KEY']['value'] = key
            self.settings['IV']['value'] = iv

            print('Key: {key}\nIV: {iv}\nOutput: {output}'.format(key=key, iv=iv, output=ciptext))

        # Symmetric Streams
        elif cph == 'Salsa20':
            key = self.__get_byte_setting__('KEY', 32)

            cip = Salsa20.new(key)

            ciptext = bytes_to_base64(cip.encrypt(txt))
            key = bytes_to_base64(key)
            nonce = bytes_to_base64(cip.nonce)

            self.settings['TEXT']['value'] = ciptext
            self.settings['KEY']['value'] = key
            self.settings['NONCE']['value'] = nonce

            print('Key: {key}\nNonce: {nonce}\nOutput: {output}'.format(key=key, nonce=nonce, output=ciptext))
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
        iv = self.settings['IV']['value']

        # Symmetric Blocks
        if cph == 'AES':
            if key is None or nonce is None:
                print(RED + '(AES) The following values are required: ', ' - KEY', ' - NONCE', ' - MAC', sep='\n')
                return

            # Define the variables
            key = base64_to_bytes(key)
            nonce = base64_to_bytes(nonce)
            mac = base64_to_bytes(mac)

            # Create cipher
            cip = AES.new(key, AES.MODE_EAX, nonce=nonce)

            try:
                # Verify using the mac and decrypt it
                ciptext = cip.decrypt_and_verify(txt, mac)
                print(GREEN + '(AES) Decryption successful: ' + RESET + ciptext.decode())
            except ValueError:
                print(RED + '(AES) Decryption failed.')

        elif cph == 'Single-DES':
            if key is None or iv is None:
                print(RED + '(Single-DES) The following values are required: ', ' - KEY', ' - IV', sep='\n')
                return

            key = base64_to_bytes(key)
            iv = base64_to_bytes(iv)

            # Create cipher
            cip = DES.new(key, DES.MODE_OFB, iv=iv)
            ciptext = cip.decrypt(txt)

            print(GREEN + '(Single-DES) Decryption successful: ' + RESET + ciptext.decode())
        elif cph == 'Triple-DES':
            if key is None or iv is None:
                print(RED + '(Triple-DES) The following values are required: ', ' - KEY', ' - IV', sep='\n')
                return

            key = base64_to_bytes(key)
            iv = base64_to_bytes(iv)

            # Create cipher
            cip = DES3.new(key, DES3.MODE_CFB, iv=iv)
            ciptext = cip.decrypt(txt)

            print(GREEN + '(Triple-DES) Decryption successful: ' + RESET + ciptext.decode())
        elif cph == 'RC2':
            if key is None or iv is None:
                print(RED + '(RC2) The following values are required: ', ' - KEY', ' - IV', sep='\n')
                return

            key = base64_to_bytes(key)
            iv = base64_to_bytes(iv)

            # Create cipher
            cip = ARC2.new(key, ARC2.MODE_CFB, iv=iv)
            ciptext = cip.decrypt(txt)

            print(GREEN + '(RC2) Decryption successful: ' + RESET + ciptext.decode())
        elif cph == 'Blowfish':
            if key is None or iv is None:
                print(RED + '(Blowfish) The following values are required: ', ' - KEY', ' - IV', sep='\n')
                return

            key = base64_to_bytes(key)
            iv = base64_to_bytes(iv)

            # Create cipher
            cip = Blowfish.new(key, Blowfish.MODE_CBC, iv=iv)
            ciptext = cip.decrypt(txt)

            print(GREEN + '(Blowfish) Decryption successful: ' + RESET + ciptext.decode())
        elif cph == 'CAST-128':
            if key is None or iv is None:
                print(RED + '(CAST-128) The following values are required: ', ' - KEY', ' - IV', sep='\n')
                return

            key = base64_to_bytes(key)
            iv = base64_to_bytes(iv)

            # Create cipher
            cip = CAST.new(key, CAST.MODE_OPENPGP, iv=iv)
            ciptext = cip.decrypt(txt)

            print(GREEN + '(CAST-128) Decryption successful: ' + RESET + ciptext.decode())

        # Symmetric Streams
        elif cph == 'Salsa20':
            if key is None or nonce is None:
                print(RED + '(Salsa20) The following values are required: ', ' - KEY', ' - NONCE', sep='\n')
                return

            key = base64_to_bytes(key)
            nonce = base64_to_bytes(nonce)

            cip = Salsa20.new(key, nonce=nonce)
            ciptext = cip.decrypt(txt)

            print(GREEN + '(Salsa20) Decryption successful: ' + RESET + ciptext.decode())
        else:
            print(RED + 'You configured an invalid cipher.')
            return

    def do_ciphers(self, _ln):
        print(BLUE + '-----[Symmetric]-----',
              RESET + 'Please note that all ciphers use a predefined MODE they use to encrypt & decrypt. This',
              'MODE may differ depending on the cipher, this also explains why some ciphers use',
              'NONCE and others use IV.',
              'AES is the most standard in this PoC and also uses an additional MAC or TAG value to',
              'verify and decrypt.',
              CYAN + 'Block: ' + RESET + 'AES, Single-DES, Triple-DES, RC2, Blowfish, CAST-128',
              CYAN + 'Stream: ' + RESET + 'Salsa20', sep='\n', end='\n\n')

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
