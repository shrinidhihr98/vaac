import curses
import logging
from curses import ascii, wrapper

class WindowHandler():
    def __init__(self, stdscr, screen_pad, inputHandler, maxlines):
        self.stdscr = stdscr
        self.pad = screen_pad
        self.y_offset = 0
        self.cursor_y = 1
        self.cursor_x = len(inputHandler.prompt)
        self.maxlines = maxlines

    def initscreen(self, inputHandler):
        self.stdscr.refresh()
        self.pad.erase()
        self.pad.addstr('[]'+"\n"+inputHandler.screen_log+inputHandler.prompt+" ")
        self.pad.refresh(0, 0, 0, 0, curses.LINES-1, curses.COLS)
        logging.info("windowhandler.initscreen():Screen Initialized:" +
                     str(curses.LINES)+","+str(curses.COLS)+"\n")

    def writeInput(self, inputHandler):
        logging.info("windowhandler.writeInput(): Writing input.\n")
        if inputHandler.resizeBool:
            logging.debug("windowhandler.writeInput(): Resizing pad.\n")
            curses.update_lines_cols()
            self.pad.resize(self.maxlines, curses.COLS)

        self.pad.erase()
        self.pad.addstr(str(inputHandler.commands_list)+"\n")
        self.pad.addstr(inputHandler.screen_log)
        self.pad.addstr(inputHandler.prompt+"".join(inputHandler.command))

    def move_cursor(self, inputHandler):
        logging.debug("windowHandler.move_cursor,moving to y,x:" +
                      str(self.cursor_y)+","+str(self.cursor_x)+"\n")
        self.pad.move(self.cursor_y, self.cursor_x)

    def refresh(self):
        logging.info("windowHandler.refresh():Refreshing...\n")
        self.pad.refresh(self.y_offset, 0, 0, 0, curses.LINES-1, curses.COLS)
        logging.info("----------------------\n")

    def updateyx(self, inputHandler):
        logging.info("windowHandler.updateyx(): Updating y,x.\n")
        y, x = self.pad.getyx()
        char = inputHandler.char
        if (not inputHandler.updateBool):
            return

        self.cursor_x = (inputHandler.cmd_char_idx +
                         len(inputHandler.prompt)) % curses.COLS
        self.cursor_y = y

        if char == curses.KEY_PPAGE:
            logging.debug("Got pageup.\n")
            self.y_offset -= curses.LINES - 1
            if self.y_offset < 0:
                self.y_offset = 0
        elif char == curses.KEY_NPAGE:
            logging.debug("Got pagedown.\n")
            self.y_offset += curses.LINES - 1
            if self.y_offset + curses.LINES >= self.cursor_y:
                self.y_offset = y - curses.LINES + 1
        elif y >= curses.LINES-1:
            self.y_offset = y - curses.LINES + 1

        if (self.y_offset == y - curses.LINES + 1) or (self.y_offset == 0 and (inputHandler.screen_log.count("\n") < curses.LINES)):
            curses.curs_set(2)
        else:
            curses.curs_set(0)

        logging.debug("windowHandler.updateyx:current y,x" +
                      str(self.cursor_y)+","+str(self.cursor_x)+"\n")
        logging.debug("windowHandler.updateyx:New y,x"+str(y)+","+str(x)+"\n")
        logging.debug("windowHandler.updateyx:Lines,cols " +
                      str(curses.LINES)+","+str(curses.COLS)+"\n")
        logging.debug("windowHandler.updateyx:y-offset " +
                      str(self.y_offset)+"\n")


class InputHandler:
    def __init__(self, stdscr, screen_pad):
        self.screen_log = '''This is the vaac terminal program.\nType "help" for more information.\n'''
        self.command = []  # list of chars
        self.commands_list = []
        self.char = 0
        self.exitstring = "exit"
        self.prompt = "> "
        self.cmd_list_pointer = 0
        self.cmd_char_idx = 0
        self.stdscr = stdscr
        self.pad = screen_pad        
        self.updateBool = False
        self.resizeBool = False
        self.process = None

    def takeInput(self):
        self.char = self.stdscr.getch()
        logging.debug("inputHandler.takeInput(): Got char:" +
                      str(self.char)+"\n")

    def processArgs(self):
        self.resizeBool = False
        if self.char >= 32 and self.char <= 126:
            self.command.insert(self.cmd_char_idx, chr(self.char))
            self.cmd_char_idx += 1
            self.updateBool = True
        
        elif self.char == curses.KEY_UP:
            self.cmd_list_pointer -= 1
            if self.cmd_list_pointer < 0:
                self.cmd_list_pointer = 0
            
            self.command = list(self.commands_list[self.cmd_list_pointer])
            
            self.cmd_char_idx = len(self.command)
        
        elif self.char == curses.KEY_DOWN:
            self.cmd_list_pointer += 1
            if self.cmd_list_pointer >= len(self.commands_list):
                self.cmd_list_pointer = len(self.commands_list)-1
            self.command = list(self.commands_list[self.cmd_list_pointer])
            self.cmd_char_idx = len(self.command)
        
        elif self.char == curses.KEY_BACKSPACE:
            if self.command != []:
                logging.debug("inputHandler.processArgs(): Backspace...removing:" + str(self.command[self.cmd_char_idx-1]) + "\n")
                del self.command[self.cmd_char_idx-1]
                self.cmd_char_idx -= 1
            self.updateBool = True
        
        elif self.char == ord('\n') and self.command != []:
            self.cmd_list_pointer += 1

            if self.commands_list != [] and self.commands_list[-1] == "":
                self.commands_list.pop()

            command_string = "".join(self.command)
            self.commands_list.append(command_string)
            self.getOutput()  # Probable spaghetti
            self.commands_list.append("")

            while len(self.command) > 0:
                self.command.pop()

            self.cmd_char_idx = 0

        elif self.char == curses.KEY_LEFT:
            if self.cmd_char_idx > 0:
                self.cmd_char_idx -= 1
            self.updateBool = True
        
        elif self.char == curses.KEY_RIGHT:
            if self.cmd_char_idx < len(self.command):
                self.cmd_char_idx += 1
            self.updateBool = True
        
        elif self.char == curses.KEY_HOME:
            self.cmd_char_idx = 0
            self.updateBool = True
        
        elif self.char == curses.KEY_END:
            self.cmd_char_idx = len(self.command)
            self.updateBool = True
        
        elif self.char == curses.KEY_NPAGE:
            self.updateBool = True
        
        elif self.char == curses.KEY_PPAGE:
            self.updateBool = True
        
        elif self.char == curses.KEY_RESIZE:
            self.updateBool = True
            self.resizeBool = True
        
        else:
            self.updateBool = False
        
        logging.debug("inputHandler.processArgs: currentcommand " +
                      "".join(self.command)+"\n")
        logging.debug("inputHandler.processArgs: commands_list: " +
                      str(self.commands_list)+"\n")
        logging.debug("inputHandler.processArgs: cmd_char_idx: " +
                      str(self.cmd_char_idx)+"\n")

    def checkIfExit(self):
        try:
            if self.commands_list[-2] == self.exitstring:
                return True
        except:
            return False

    def getLastInput(self):
        return self.commands_list[-1]

    def getOutput(self):
        self.screen_log += self.prompt+self.commands_list[-1]+"\n"
        input_command = self.commands_list[-1].split()
        if input_command == ['exit']:
            return
        
        if input_command == ['help']:
            help_str = '''This is the Vaac terminal. It provides an interface to communicate with your system. You can type into this terminal, or speak into it.\nThis is a primitive terminal and might not support all key strokes.\nThis terminal accepts simple, natural language commands. You can use up and down to navigate through commands history, and page up and page down to scroll. Use backspace to delete a typed character.\nFor help setting up Vaac, use the README.md file, or go to the Vaac github page.\n'''
            self.screen_log += help_str


def main(stdscr):
    logging.basicConfig(filename='term.log', level=logging.DEBUG)
    logging.disable(logging.CRITICAL)
    maxlines = 2000
    pad = curses.newpad(maxlines, curses.COLS)
    inputHandler = InputHandler(stdscr, pad)
    windowHandler = WindowHandler(stdscr, pad, inputHandler, maxlines)
    windowHandler.initscreen(inputHandler)
    while 1:
        windowHandler.refresh()
        inputHandler.takeInput()
        inputHandler.processArgs()
        windowHandler.writeInput(inputHandler)
        windowHandler.updateyx(inputHandler)
        windowHandler.move_cursor(inputHandler)
        if inputHandler.checkIfExit():
            logging.info("main(): Exiting..."+"\n")
            break


wrapper(main)