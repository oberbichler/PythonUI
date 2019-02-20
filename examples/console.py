import python_ui as ui


class Window(ui.ApplicationWindow):
    def __init__(self):
        super(Window, self).__init__(
            title='Example',
        )

    def _started(self):
        Fore, Back, Style = ui.ConsoleStyles

        print('use colors like',
              Fore.RED + 'red,',
              Fore.GREEN + 'green,',
              Fore.YELLOW + 'yellow,',
              Fore.BLUE + 'blue,',
              Fore.MAGENTA + 'magenta,',
              Fore.CYAN + 'cyan',
              Fore.WHITE + 'or just white',
              Style.RESET_ALL)
        print(Style.BRIGHT + 'write ' + Fore.RED + 'bold ' + Fore.GREEN +
              'text ' + Fore.BLUE + 'in ' + Fore.YELLOW + 'different ' +
              Fore.MAGENTA + 'colors' + Style.RESET_ALL)
        print(Style.BRIGHT + Fore.BLACK + Back.GREEN + ' or ' + Back.WHITE +
              ' use ' + Back.RED + ' background ' + Back.YELLOW + ' colors ' +
              Style.RESET_ALL)


Window.run()
