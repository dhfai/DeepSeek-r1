def input_for_accepted(title, generator):
    while True:
        print(title)
        data = generator()
        if input("> Accept [y/n]? ").lower() == 'y':
            return data
        print("Try again...")