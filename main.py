global x

def check():
    print(x)
    print("test")

def set_configuration():
    global x
    x = 25

def main():
    set_configuration()
    check()

if __name__ == '__main__':
    main()
    print("THE FUCK")
