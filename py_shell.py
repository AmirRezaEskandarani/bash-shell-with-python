__author__ = "Amirreza Eskandarani"

import os
import subprocess

def execute_command(command):
    
    try:
        if "|" in command:
            # save to restore original value of stdin stdout later
            s_in, s_out = (0, 0)
            s_in = os.dup(0)
            s_out = os.dup(1)

            # first command takes command from stdin
            fdin = os.dup(s_in)

            # iterate over all the commands that are piped
            for cmd in command.split("|"):
              
                os.dup2(fdin, 0)
                os.close(fdin)

                # restore stdout if this is the last command or not
                if cmd == command.split("|")[-1]:
                  
                    fdout = os.dup(s_out)
                else:
                   
                    fdin, fdout = os.pipe()

                # redirect stdout to pipe
                os.dup2(fdout, 1)
                os.close(fdout)

                try:
                   
                    subprocess.run(cmd.strip().split())
                except Exception:
                    print("pysh: command not found: {}".format(cmd.strip()))

            # restore original value of stdout and stdin
            os.dup2(s_in, 0)
            os.dup2(s_out, 1)
            os.close(s_in)
            os.close(s_out)
        else:
            # run used here to execute commands in a subshell
            subprocess.run(command.split(" "))
    except Exception:
        print("command not found: {}".format(command))


def psh_cd(path):
    """convert to absolute path and change directory"""
    try:
        # subprocess runs the command in a subshell so we use os instead
        os.chdir(os.path.abspath(path))
    except Exception:
        print("cd: no such file or directory: {}".format(path))


def psh_help():
    print("""pysh: If you don't know usage of a command
     use man <your command> or google it.""")

commands = []

def main():
    while True:
        inp = input("$ ")
        if inp == "exit":
            break

        elif inp[:3] == "cd ":
            psh_cd(inp[3:])
            commands.append(inp)

        elif inp == "help":
            psh_help()
            commands.append(inp)

        elif inp.endswith("&"):
            inp = inp.replace("&", "")
            command_list = inp.split()
            subprocess.Popen(command_list)
            commands.append(inp)

        elif "exec" in inp:
            inp = inp[5:]
            execute_command(inp)
            break

        elif ";" in inp:
            commands.append(inp)
            index = inp.index(";")
            cmd = inp[:index]
            execute_command(cmd)
            
            cmd = inp[index + 2:]
            execute_command(cmd)


        elif "history" in inp:
            commands.append(inp)
            # check if user entered any digits
            check = any(chr.isdigit() for chr in inp)
            if check:
                # print last <number> commands
                number = [int(s) for s in inp.split() if s.isdigit()]
                print (commands[0:number[0]])

            elif " less" in inp:
                # print last 10 commands
                print (commands[-10:])

            elif " tail" in inp:
                # print last 25 commands
                print (commands[-25:])

            else :
                # when user didin't type any digits
                print(commands)
            

        elif ">" in inp:
            p = subprocess.Popen(inp, shell=True)
            os.waitpid(p.pid, 1)
            commands.append(inp)

        elif "<" in inp:
            p = subprocess.Popen(inp, shell=True)
            os.waitpid(p.pid, 0)
            commands.append(inp)

        elif "!!" in inp:
            print("last command :", commands[-1])
            commands.append(inp)

        else:
            commands.append(inp)
            execute_command(inp)


if '__main__' == __name__:
    main()