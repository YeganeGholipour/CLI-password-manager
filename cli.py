import cmd

class MyCLI(cmd.Cmd):
    prompt = '>>'
    intro = 'Welcome to the MyCLI application.'

    def do_hello(self, line):
        print('Hello, world!')

    def do_quit(self, line):
        return True
    
    def precmd(self, line):
        print('Before command execution')
        return line
    
    def postcmd(self, stop, line):
        print('After command execution')
        return stop
    
    def preloop(self):
        print("Initialixation before the CLI loop")

    def postloop(self):
        print("Finalization after CLI loop")
    



if __name__ == '__main__':
    MyCLI().cmdloop()