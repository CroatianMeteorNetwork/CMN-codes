# coding=utf-8
# Copyright 2015 Denis Vida, denis.vida@gmail.com

# The SuperBind is free software; you can redistribute
# it and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, version 2.

# The SuperBind is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with the SuperBind ; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA

# Inspired by: https://www.daniweb.com/software-development/python/threads/70746/keypress-event-with-holding-down-the-key#post463445

from Tkinter import *

class SuperBind():
    """ Enable any key to have proper events on being pressed once or being held down longer.

        pressed_function is called when the key is being held down.
        release_function is called when the key is pressed only once or released after pressing it constantly

        Arguments:
            key - key to be pressed, e.g. 'a'
            master - 'self' from master class
            root - Tkinter root of master class
            pressed_function - function to be called when the key is pressed constantly
            release_function - function to be called when the key is released or pressed only once

        e.g. calling from master class:
        a_key = SuperBind('a', self, self.root, self.print_press, self.print_release)
    """

    def __init__(self, key, master, root, pressed_function, release_function):
        self.afterId = None
        self.master = master
        self.root = root

        self.pressed_function = pressed_function
        self.release_function = release_function

        self.root.bind('<KeyPress-'+key+'>', self.keyPress)
        self.root.bind('<KeyRelease-'+key+'>', self.keyRelease)

        self.pressed_counter = 0

    def keyPress(self, event):
        if self.afterId != None:
            self.master.after_cancel( self.afterId )
            self.afterId = None

            self.pressed_function()
        else:
            if self.pressed_counter > 1:
                self.pressed_function()
            else:
                # Comment out the following line for only one event on key press:
                self.release_function()
                pass
            
            self.pressed_counter += 1


    def keyRelease(self, event):
        self.afterId = self.master.after_idle( self.processRelease, event )

    def processRelease(self, event):
        self.release_function()
        self.afterId = None
        self.pressed_counter = 0

class SuperUnbind():
    """ Unbind all that was bound by SuperBind.
    """
    def __init__(self, key, master, root):
        self.master = master
        self.root = root

        self.root.unbind('<KeyPress-'+key+'>')
        self.root.unbind('<KeyRelease-'+key+'>')


#####################################################
# Example of usage by pressing key 'a'

class MyFrame(Frame):
    def __init__(self, root):
        Frame.__init__(self, root)

        self.root = root
        self.pack()

        a_key = SuperBind('a', self, self.root, lambda: self.printPress('hola'), self.printRelease)

    def printPress(self, text = 'nema'):
        print 'key pressed', text

    def printRelease(self):
        print 'key released'

        
        
root = Tk()
root.geometry("400x30+0+0")
app1 = MyFrame(root)
root.mainloop()