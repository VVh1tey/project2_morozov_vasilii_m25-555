import prompt

def welcome():
    print("Welcome to the Primitive DB!")
    
    # Справочная информация, которая выводится в начале и по команде help
    help_text = (
        "<command> exit - выйти из программы\n"
        "<command> help - справочная информация"
    )
    
    print(help_text)

    while True:
        command = prompt.string('Введите команду: ')
        
        if command == 'exit':
            break
        elif command == 'help':
            print(help_text)
        else:
            # Логика для неизвестных команд (опционально)
            print(f"Unknown command: {command}")
            print(help_text)