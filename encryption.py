import binascii
from cmd import Cmd
from tabulate import tabulate

from Crypto.Cipher import AES, DES, DES3, ARC2, CAST, Salsa20
from Crypto.Random import get_random_bytes
from base64 import b64encode, b64decode

from main import MainPrompt


def bytes_to_base64(byte_input):
    return b64encode(byte_input).decode()


def base64_to_bytes(base64_input):
    try:
        # Return the decoded bytes
        return b64decode(base64_input)
    except binascii.Error:
        return None


def is_valid_byte(req, bt):
    # Decode to (hopefully) bytes
    bt = base64_to_bytes(bt)

    # Check if the type really is "bytes"
    if type(bt) != bytes:
        return False

    # Return whether or not the byte length is equal to the requirement
    return len(bt) == req


class Prompt(Cmd):
    def __init__(self, cls):
        super(Prompt, self).__init__()
        self.prompt = '{blue}program {cyan}(encryption) ➥ {reset}'.format(blue=cls['BLUE'], cyan=cls['CYAN'], reset=cls['RESET'])
        self.cls = cls

    # We define the settings here
    settings = {
        'CIPHER': {
            'value': 'AES',
            'description': 'Use \'ciphers\' for a complete list',
            'required': True
        },
        'KEY': {
            'value': None,
            'description': 'A secret key',
            'required': False
        },
        'TEXT': {
            'value': None,
            'description': 'The text to encrypt/decrypt',
            'required': True
        },
        'NONCE': {
            'value': None,
            'description': 'Number used in communication',
            'required': False
        },
        'MAC': {
            'value': None,
            'description': 'Message Authentication Code',
            'required': False
        },
        'IV': {
            'value': None,
            'description': 'Initialization Vector',
            'required': False
        }
    }

    def do_help(self, _ln):
        print('\nAll commands that can be used within this module can be found below: ')
        cmd_list = [
            ['settings', 'View current settings'],
            ['set', 'Set the value of a setting'],
            ['unset', 'Unset a certain setting'],
            ['encrypt', 'Encrypt some text (configure first)'],
            ['decrypt', 'Decrypt some text (Configure first)'],
            ['ciphers', 'Obtain a list with supported ciphers'],
            ['back', 'Return to the previous prompt']
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

        # Get the option name in caps
        opt_name = arr.pop(0).upper()
        # Join the rest of the array representing the option value
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

    def do_encrypt(self, ln):
        # Store the cipher setting (cph), and text setting (txt) in a variable for improved readability
        cph = self.settings['CIPHER']['value']
        txt = self.settings['TEXT']['value']

        if txt is None:
            print(self.cls['RED'] + 'There was no text set.')
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
            print('--=(AES)=--\nKey: {key}\nNonce: {nonce}\nMac: {mac}\nOutput: {output}'.format(
                key=key, nonce=nonce, mac=mac, output=ciptext))
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
            print('--=(Single-DES)=--\nKey: {key}\nIV: {iv}\nOutput: {output}'.format(key=key, iv=iv, output=ciptext))
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

            print('--=(Triple-DES)=--\nKey: {key}\nIV: {iv}\nOutput: {output}'.format(key=key, iv=iv, output=ciptext))
        elif cph == 'RC2':
            key = self.__get_byte_setting__('KEY', 16)

            cip = ARC2.new(key, ARC2.MODE_CFB)

            ciptext = bytes_to_base64(cip.encrypt(txt))
            key = bytes_to_base64(key)
            iv = bytes_to_base64(cip.iv)

            self.settings['TEXT']['value'] = ciptext
            self.settings['KEY']['value'] = key
            self.settings['IV']['value'] = iv

            print('--=(RC2)=--\nKey: {key}\nIV: {iv}\nOutput: {output}'.format(key=key, iv=iv, output=ciptext))
        elif cph == 'CAST-128':
            key = self.__get_byte_setting__('KEY', 16)

            cip = CAST.new(key, CAST.MODE_OPENPGP)

            ciptext = bytes_to_base64(cip.encrypt(txt))
            key = bytes_to_base64(key)

            self.settings['TEXT']['value'] = ciptext
            self.settings['KEY']['value'] = key

            print('--=(CAST-128)=--\nKey: {key}\nOutput: {output}'.format(key=key, output=ciptext))

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

            print('--=(Salsa20)=--\nKey: {key}\nNonce: {nonce}\nOutput: {output}'.format(key=key, nonce=nonce,
                                                                                         output=ciptext))
        else:
            print(self.cls['RED'] + 'You configured an invalid cipher. (Case sensitive)')
            return

    def do_decrypt(self, ln):
        cph = self.settings['CIPHER']['value']
        txt = self.settings['TEXT']['value'] if self.settings['TEXT']['value'] is None else base64_to_bytes(self.settings['TEXT']['value'])

        if txt is None:
            print(self.cls['RED'] + 'There was no valid base64 text set.')
            return

        # This looks ugly but is quite clever:
        # We will not have to check later if a value is None and if that's not the case convert it using ~
        # base64_to_bytes and then check again, since this function can also return None
        key = self.settings['KEY']['value'] if self.settings['KEY']['value'] is None else base64_to_bytes(self.settings['KEY']['value'])
        nonce = self.settings['NONCE']['value'] if self.settings['NONCE']['value'] is None else base64_to_bytes(self.settings['NONCE']['value'])
        mac = self.settings['MAC']['value'] if self.settings['MAC']['value'] is None else base64_to_bytes(self.settings['MAC']['value'])
        iv = self.settings['IV']['value'] if self.settings['IV']['value'] is None else base64_to_bytes(self.settings['IV']['value'])

        # Symmetric Blocks
        if cph == 'AES':
            if key is None or nonce is None:
                print(self.cls['RED'] + '(AES) The following values are required and must be base64:', ' - KEY', ' - NONCE', ' - MAC', sep='\n')
                return

            # Create cipher
            cip = AES.new(key, AES.MODE_EAX, nonce=nonce)

            try:
                # Verify using the mac and decrypt it
                ciptext = cip.decrypt_and_verify(txt, mac)
                print(self.cls['GREEN'] + '(AES) Decryption successful: ' + self.cls['RESET'] + ciptext.decode())
            except ValueError:
                print(self.cls['RED'] + '(AES) Decryption failed.')

        elif cph == 'Single-DES':
            if key is None or iv is None:
                print(self.cls['RED'] + '(Single-DES) The following values are required and must be base64:', ' - KEY',
                      ' - IV', sep='\n')
                return

            # Create cipher
            cip = DES.new(key, DES.MODE_OFB, iv=iv)
            ciptext = cip.decrypt(txt)

            print(self.cls['GREEN'] + '(Single-DES) Decryption successful: ' + self.cls['RESET'] + ciptext.decode())
        elif cph == 'Triple-DES':
            if key is None or iv is None:
                print(self.cls['RED'] + '(Triple-DES) The following values are required and must be base64:', ' - KEY',
                      ' - IV', sep='\n')
                return

            # Create cipher
            cip = DES3.new(key, DES3.MODE_CFB, iv=iv)
            ciptext = cip.decrypt(txt)

            print(self.cls['GREEN'] + '(Triple-DES) Decryption successful: ' + self.cls['RESET'] + ciptext.decode())
        elif cph == 'RC2':
            if key is None or iv is None:
                print(self.cls['RED'] + '(RC2) The following values are required and must be base64:', ' - KEY', ' - IV', sep='\n')
                return

            # Create cipher
            cip = ARC2.new(key, ARC2.MODE_CFB, iv=iv)
            ciptext = cip.decrypt(txt)

            print(self.cls['GREEN'] + '(RC2) Decryption successful: ' + self.cls['RESET'] + ciptext.decode())
        elif cph == 'CAST-128':
            if key is None:
                print(self.cls['RED'] + '(CAST-128) The following values are required and must be base64:', ' - KEY', sep='\n')
                return

            # So the iv must be 10 bytes long for decryption (8 for encryption)
            # and the iv is encrypted and prefixed, so we separate it below
            iv = txt[:8 + 2]
            txt = txt[8 + 2:]

            # Create cipher
            cip = CAST.new(key, CAST.MODE_OPENPGP, iv=iv)
            ciptext = cip.decrypt(txt)

            print(self.cls['GREEN'] + '(CAST-128) Decryption successful: ' + self.cls['RESET'] + ciptext.decode())

        # Symmetric Streams
        elif cph == 'Salsa20':
            if key is None or nonce is None:
                print(self.cls['RED'] + '(Salsa20) The following values are required and must be base64:', ' - KEY', ' - NONCE', sep='\n')
                return

            cip = Salsa20.new(key, nonce=nonce)
            ciptext = cip.decrypt(txt)

            print(self.cls['GREEN'] + '(Salsa20) Decryption successful: ' + self.cls['RESET'] + ciptext.decode())
        else:
            print(self.cls['RED'] + 'You configured an invalid cipher. (Case sensitive)')
            return

    def do_ciphers(self, _ln):
        print(self.cls['BLUE'] + '-----[Symmetric]-----',
              self.cls[
                  'RESET'] + 'Please note that all ciphers use a predefined MODE they use to encrypt & decrypt. This',
              'MODE may differ depending on the cipher, this also explains why some ciphers use',
              'NONCE and others use IV.',
              'AES is the most standard in this PoC and also uses an additional MAC or TAG value to',
              'verify and decrypt.',
              self.cls['CYAN'] + 'Block: ' + self.cls['RESET'] + 'AES, Single-DES, Triple-DES, RC2, CAST-128',
              self.cls['CYAN'] + 'Stream: ' + self.cls['RESET'] + 'Salsa20', sep='\n', end='\n\n')

    def default(self, ln):
        ln = ln.lower()

        if ln == 'back' or ln == 'b':
            MainPrompt(self.cls).cmdloop()
            return True

        print(self.cls['RED'] + 'That\'s not a valid command. Use \'help\' for a list of commands.' + self.cls['RESET'])

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
