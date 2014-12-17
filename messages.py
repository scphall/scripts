#!/usr/bin/python

###############################################################################

"""
    Classes for colourting information in formatted fashion.
    Contains class:
        Message(name, colour, font)
            For printing formatted messages.

"""

__title__  = "messages.py"
__author__ = "Sam Hall"
__email__  = "shall@cern.ch"

###############################################################################

config = {
    'LEN'   :   80,
    'COL1'  :   17
}


class Message:
    def __init__(self, name, colour, font='normal'):
        """Initialize the Message class"""
        self.config = config
        self.colour = ''
        self.font = ''
        self.reset = '\033[m'
        self.colours = {
                'black'     :   30,
                'red'       :   31,
                'yellow'    :   32,
                'orange'    :   33,
                'blue'      :   34,
                'purple'    :   35,
                'greenblue' :   36,
                'grey'      :   37,
                'green'     :   38
            }
        self.fonts = {
                'normal'    :   0,
                'bold'      :   1
            }
        self.template = '\033[%d;%dm'
        self.set_type(colour, font)
        self.set_name(name)
        self.last = False
        return

    def set_name(self, name):
        """Colour the name."""
        self.name = self.get_colour_string(name)
        return

    def set_type(self, colour, font='normal'):
        """Set colour and font of message."""
        self.colour = self.colours[colour]
        self.font = self.fonts[font]
        self.colourStr = self.template%(self.font, self.colour)
        return

    def get_colour_string(self, msg):
        """Output a coloured version of the Input string."""
        string  = self.colourStr
        string += '%s%s'%(str(msg), self.reset)
        return string

    def get_msg(self, msg):
        """Format the input message appropriately."""
        global config
        template = ' | %s%s: %s'
        spaces = 10 - (len(self.name) - len(self.colourStr) - len(self.reset))
        msg = self.get_colour_string(msg)
        msg = template%(self.name, ' '*spaces, msg)
        return msg

    def rc(self, msg):
        rep = ('\n %s|%s '+' '*14)%(self.reset, self.colourStr)
        msg = msg.replace('\n', rep)
        return msg

    def print_msg(self, msg):
        """Print the formatted message!"""
        msg = self.get_msg(msg)
        msg = self.rc(msg)
        if self.last:
            spaces = len(self.name) - len(self.colourStr) - len(self.reset)
            msg = msg.replace(self.name, ' ' * spaces)
        if msg.endswith('-%s'%self.reset):
            msg = msg.replace('-%s'%self.reset, '%s'%self.reset)
            self.last = True
        else:
            self.last = False
        print msg
        return


###############################################################################

class Messages:
    def __init__(self, header=['-']):
        """Initialize Messages class, just a group of the Message class"""
        self.config = config
        self.Error  = Message('ERROR', 'red')
        self.Info   = Message('INFO', 'orange')
        self.Result = Message('RESULT', 'purple')
        self.Debug  = Message('DEBUG', 'blue')
        self.Raw    = Message('RAW', 'green')
        self.header = header
        self.debugsw = False
        self.print_header(header)
        self.results = []
        self.last = ''
        return

    def init(self, header=['-']):
        """Alias for __init__, more beautiful for in code use."""
        self.__init__(header)

    def set_last(self, lastString):
        """Set last switches."""
        if lastString == 'raw':
            self.Error.last = False
            self.Info.last = False
            self.Debug.last = False
            self.Result.last = False
        if lastString == 'debug':
            self.Error.last = False
            self.Info.last = False
            self.Result.last = False
        if lastString == 'error':
            self.Info.last = False
            self.Debug.last = False
            self.Result.last = False
        if lastString == 'info':
            self.Error.last = False
            self.Debug.last = False
            self.Result.last = False
        if lastString == 'result':
            self.Error.last = False
            self.Info.last = False
            self.Debug.last = False
        return

    def set_debug(self, sw=True):
        """Turns debug mode on and off."""
        self.debugsw = sw
        return

    def error(self, msg):
        """Print an error message."""
        self.Error.print_msg(msg)
        self.set_last('error')
        return

    def info(self, msg):
        """Print an informative message."""
        self.Info.print_msg(msg)
        self.set_last('info')
        return

    def result(self, name, result, printnow=True):
        """Print a result."""
        msg = ''
        name = '%10s'%name
        msg += '%s = %s'%(name, str(result))
        if printnow:
            self.Result.print_msg(msg)
        self.results.append(msg)
        self.set_last('result')
        return

    def debug(self, name, result=None):
        """Print a result."""
        if not self.debugsw:
            return
        msg = ''
        if result is not None:
            name = '%10s'%name
            msg += '%s = %s'%(name, str(result))
        else:
            msg += '%s'%(name)
        self.Debug.print_msg(msg)
        self.set_last('debug')
        return

    def raw(self, msg=''):
        """Print raw output."""
        if(isinstance(msg, str)):
            msg = msg.replace('\n', '\n | ')
            print ' | '+msg
        else:
            print msg
        self.set_last('raw')
        return


    def print_header(self, header):
        """Print a header about the function."""
        global config
        line = '='*config['LEN']
        if len(header) == 1 and header[0] == '-':
            return
        if header == []:
            print '\n'+line
            return
        header = [x.center(80, ' ') for x in header]
        head = '\n'.join(header)
        head = '\n%s\n%s\n%s'%(line, head, line)
        print head
        return

    def foot(self, printfoot=True):
        """Print a footer."""
        global config
        line = '='*config['LEN']
        print line
        if not printfoot or len(self.results) == 0:
            return
        #if self.header != []:
        #    info = '  Summary of results from %s.\n'%self.header[0]
        #else:
        #    info = '  Summary of results from script.\n'
        foot = ''
        for r in self.results:
            foot += '  %s\n'%r
        foot = foot.split('=')
        foot = [self.Result.get_colour_string(x) for x in foot]
        foot = '='.join(foot)
        #foot = '%s%s%s\n'%(info, foot, line)
        foot = '%s%s\n'%(foot, line)
        print foot
        self.set_last('raw')
        return

    def line(self):
        print ' | ' + '-'*77
        self.set_last('raw')
        return

###############################################################################

if __name__ == "__main__":
    msg = Messages([__title__, __author__, __email__])
    msg.set_debug()
    msg.error('Badger related error.')
    msg.info('Information about a hippy-')
    msg.info(' but a hippy pig.')
    msg.result('Pig', 0.345)
    msg.debug('test', 123)
    msg.debug('test')
    msg.raw('This is a raw thing.')
    msg.foot()



