"""
The dictionary class is not meant to be instantiated, but used as a collection of strings for
translation purposes. By adding lists here it is possible to change the interface language.

"""


class Dictionary(object):
    ENGLISH = 1
    SWEDISH = 2
    GERMAN = 3

    lang = ENGLISH

    dic = [
        #
        # [key, English, Swedish]
        #
        ['addargs', 'Add arguments as needed', 'Lägg till eventuella argument'],
        ['board', 'Select board used', 'Välj typ av läsare'],
        ['checkarray', 'Please check last array, since it might not be complete.',
         'Var vänlig kontrollera sista arrayen, eftersom den kan vara felaktig.'],
        ['checklin', 'Checking Linux port address.', 'Kontrollerar adress för Linux.'],
        ['ctrlwintitle', 'Settings for collecting channel packages.', 'Inställningar för att samla data paket.'],
        ['checkmac', 'Checking OS X port address.', 'Kontrollerar adress för OS X.'],
        ['checkwin', 'Checking Windows port address.', 'Kontrollerar adress för Windows.'],
        ['cychan', 'Cyton board only', 'Enbart Cyton'],
        ['daisychan', 'On Daisy board', 'På Daisy'],
        ['deactivate_plug', 'Deactivating Plugins...', 'Avaktiverar plugin-moduler...'],
        ['selport', 'Select port', 'Välj port'],
        ['cancel', 'Cancel', 'Ångra'],
        ['end_byte', 'ID: <%dic> <Unexpected END_BYTE found <%s> instead of <%s>',
         'ID-nummer: <%dic> Oväntat slut med BYTE %dic hittat i filen istället för %s'],
        ['estserial', 'Serial established...', 'Seriell port uppkopplad...'],
        ['exiting', 'User.py exiting...', 'Avslutar programmet'],
        ['init', "Initialise", "Förbered"],
        ['log', 'Logging enabled', 'Loggning av händelser'],
        ['logmess', 'Status messages', 'Statusmeddelanden'],
        ['nogang', 'Cannot handle Ganglion Board\n at the Moment.',
         'Ganglion board kan inte\nanvändas just nu.'],
        ['noport', 'Cannot find OpenBCI port', 'Kan inte hitta rätt OpenBCI port.'],
        ['stalled', 'Device Stalled', 'Dataströmmen har upphört att sända.'],
        ['packtime', 'Desired time intervals in milliseconds: ', 'Önskad insamlingsintervaller i millisekunder: '],
        ['packets', 'Number of packets in bunch: ', 'Antal paket i bunten: '],
        ['plugsclose', 'Closing, data saved to: ', "Stannar dataströmmen, data sparat på: "],
        ['plugs', 'Available Plugins', 'Tilläggsprogram'],
        ['selport', 'Select port', 'Välj port'],
        ['shapes', 'Shape Display', 'Testfönster'],
        ['stallwarn', 'Device appears to be stalled. Quitting...',
         'Strömmen verkar ha stannat av. Avslutar!'],
        ['tooltipport', 'For Cyton, port to connect to OpenBCI Dongle \n' +
         '(e.g., "/dev/ttyUSB0" or "/dev/tty.usbserial-*"). For\n' +
         'Ganglion, MAC address of the board. For both, \n' +
         'select AUTO to attempt auto-detection.', "§§§ To be translated. §§§"],
        ['tooltipmess',
         'Here all important information will be displayed. Keep an eye here for status and error messages.',
         'Här visas all information under körningen. Håll ett öga här för att se status- och felmeddelanden.'],
        ['v3connect', 'Connecting to V3 at port %s', 'Kopplar upp mot V3 på port %s'],
        ['wintitle', 'OPEN BCI Python client', 'Open BCI Python Application']

    ]

    # ============================================
    # Returns the proper string for the selected language.
    #
    @staticmethod
    def get_string(key):
        for item in Dictionary.dic:
            if item[0] == key:
                return item[Dictionary.lang]
        return "§§§ Missing text §§§"

    # ============================================
    # Sets the language of the User Interface
    #
    @staticmethod
    def set_lang(language):
        Dictionary.lang = language

    # ============================================
    # Get the current language of the user interface
    #
    @staticmethod
    def get_lang():
        return Dictionary.lang

# ============================================
#  END OF FILE
# ============================================
