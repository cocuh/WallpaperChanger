#!/usr/bin/env python
import os
import sys
import subprocess
import shlex
import argparse
import random
import platform

CONFIG_PATH = os.path.expanduser('~/.config/wallpaperchanger.conf')

if sys.version_info.major == 2:
    import ConfigParser as configparser
    import Tkinter as tk
else: # major version == 3
    import configparser
    import tkinter as tk

try:
    import PIL.Image
    import PIL.ImageTk
except ImportError:
    PIL = None


class WallpaperChanger(object):
    """main class

    this contains filenames, config.
    """

    def __init__(self):
        self.wrap_config = WrapConfig()
        self.wrap_config.load()

        self.config = self.wrap_config.config
        self.base_path = os.path.expanduser(self.config.get('Main', 'path'))

    def call(self, filename, is_abspath=False):
        if is_abspath:
            path = filename
        else:
            path = os.path.join(self.base_path, filename)
        replace_dic = {'filepath': path}
        command = []

        # avoid to split filename which includes spaces.
        for line in shlex.split(self.config.get('Main', 'command')):
            command.append(line.format(**replace_dic))
        res = subprocess.call(command)
        if res == 0:
            self.config.set('Wallpaper', 'current', filename)
            self.wrap_config.write()

    def get_filenames(self):
        return sorted(os.listdir(self.base_path))

    def get_abspath(self, filename):
        return os.path.join(self.base_path, filename)


def get_default_wallpaper_change_command():
    system_name = platform.system()
    if system_name == 'Linux': # linux
        return 'feh --bg-fill {filepath}'
    elif system_name == 'Darwin': # mac os x
        return r'osascript -e "tell application \"Finder\" to set desktop picture to POSIX file \"{filepath}\""'


class WrapConfig(object):
    """
    Wrap ConfigParser,
    """
    DEFAULT = {
        'Main': {
            'path': '~/picture/wallpaper',
            'command': get_default_wallpaper_change_command(),
        },
        'Wallpaper': {
            'current': '',
            'default': '',
        }
    }

    def __init__(self):
        self.config = configparser.ConfigParser()

    def load(self):
        """load config file
        
        if not exists, make file.
        """
        if self.is_exists():
            self.config.read(CONFIG_PATH)
        else:
            self.set_default()
            self.write()

    def write(self):
        """save config file,
        
        automatically make directory.
        """
        if not self.is_exists_parent_directory():
            parent_path = self._get_parent_path()
            os.makedirs(parent_path)

        with open(CONFIG_PATH, 'w') as fp:
            self.config.write(fp)

    def set_default(self, overwrite=False):
        """set default, referring self.DEFAULT dictionary 
        
        if overwrite flag is True, 
        all config is overwrite.
        if the flag is False and not exists the option, append.
        """
        for section in self.DEFAULT.keys():
            if not self.config.has_section(section):
                self.config.add_section(section)

            for option in self.DEFAULT.get(section, {}).keys():
                if overwrite or not self.config.has_option(section, option):
                    self.config.set(section, option, self.DEFAULT[section][option])

    def is_exists_parent_directory(self):
        parent_path = self._get_parent_path()
        return os.path.isdir(parent_path)

    def is_exists(self):
        return os.path.exists(CONFIG_PATH)

    def _get_parent_path(self):
        return os.path.abspath(os.path.dirname(CONFIG_PATH))


class Gui(tk.Frame):
    """
    Graphical interface for wallpaper selecting.
    """
    THUMBNAIL_SIZE = (400, 400)

    def __init__(self, master, changer):
        self._changer = changer
        tk.Frame.__init__(self, master)
        self.pack()
        self.create_widgets()
        self.init_binds()
        self.set_listbox_filenames()
        self.set_thumbnail()

        self.filename = None
        self.key = ''

    def create_widgets(self):
        """init widgets
        """
        f_left = tk.Frame(self)
        f_left.pack({'fill': tk.BOTH, 'side': 'left'})

        self.elem_listbox = tk.Listbox(f_left)
        self.elem_listbox.pack({'side': 'top', 'fill': tk.BOTH})
        self.elem_entry = tk.Entry(f_left, textvariable=self.gen_entry_callback())
        self.elem_entry.pack({'side': 'bottom'})
        self.elem_entry.focus_set()

        if PIL is not None:
            f_right = tk.Frame(self)
            f_right.pack({'fill': tk.BOTH})
            self.elem_thumbnail = tk.Label(f_right)
            self.elem_thumbnail.pack({
                'side': 'right',
            })

    
    def init_binds(self):
        """init binds
        """
        self.master.bind('<Escape>', self.action_destroy)
        self.master.bind('<Return>', self.action_finish)
        self.master.bind('<Tab>', self.action_completion)
        self.elem_listbox.bind('<<ListboxSelect>>', self.action_select)
        self.elem_listbox.bind('<Double-Button-1>', self.action_finish)

    def action_destroy(self, *args):
        """destroy gui
        
        callback function
        """
        self.master.destroy()

    def action_select(self, event=None):
        """set thumbnail
        when select item in listbox, called   
        
        callback function
        """
        if event is not None:
            idx = int(self.elem_listbox.curselection()[0])
            self.filename = self.elem_listbox.get(idx)
            self.set_thumbnail(self.filename)


    def action_finish(self, *args):
        """apply new wallpaper by calling Changer.call
        """
        if self.filename is not None:
            self._changer.call(self.filename)
            self.action_destroy()

    def action_completion(self, *args):
        """Completion in textbox(Entry).
        
        hooked Tab key, and disable default tab action by returning "break".
        """
        names = self.get_filtered_filenames(self.key)
        base = names[0]
        others = names[1:]
        for idx in (len(base) - x for x in range(len(base))):
            flag = True
            for line in others:
                if not base[:idx] in line:
                    flag = False
            if flag:
                self.elem_entry.delete(0, tk.END)
                self.elem_entry.insert(0, base[:idx])
                break
        return 'break'

    def gen_entry_callback(self):
        def callback(sv):
            self.key = sv.get()
            names = self.get_filtered_filenames(self.key)

            self.set_listbox_filenames(names)
            if len(names) == 1:
                self.filename = names[0]
                self.set_thumbnail(names[0])
            else:
                self.filename = None
                self.set_thumbnail()

        string_var = tk.StringVar()
        string_var.trace('w', lambda name, index, mode, sv=string_var: callback(sv))
        return string_var
    
    def set_listbox_filenames(self, filenames=None):
        self.elem_listbox.delete(0, self.elem_listbox.size() - 1)
        if filenames is None:
            filenames = self._changer.get_filenames()
        for name in filenames:
            self.elem_listbox.insert(tk.END, name)

    def set_thumbnail(self, ifilename=None):
        if PIL is not None:
            size = self.THUMBNAIL_SIZE
            thumbnail = PIL.Image.new('RGBA', size, (0, 0, 0, 0))
            if ifilename is not None:
                filename = self._changer.get_abspath(ifilename)
                image = PIL.Image.open(filename)
                image.thumbnail(size, PIL.Image.ANTIALIAS)

                offset_x = int(max((size[0] - image.size[0]) / 2, 0))
                offset_y = int(max((size[1] - image.size[1]) / 2, 0))
                thumbnail.paste(image, (offset_x, offset_y))

            self.thumbnail = PIL.ImageTk.PhotoImage(thumbnail)
            self.elem_thumbnail.configure(image=self.thumbnail)

    def get_filtered_filenames(self, keyword):
        return [x for x in self._changer.get_filenames() if x.find(keyword) == 0]


def parse_argument():
    parser = argparse.ArgumentParser(
        description='Wallpaper Changer on Python.',
        epilog='''Change ~/.config/wallpaperchanger.conf if you need.'''
    )
    parser.add_argument('filename',
                        nargs='?',
                        default=None,
                        help='set the picture, ')
    parser.add_argument('-d', '--default',
                        action='store_true',
                        help='set default picture as wallpaper, if you set config'
    )
    parser.add_argument('-r', '--random',
                        action='store_true',
                        help='set random picture',
    )
    parser.add_argument('-n', '--next',
                        action='store_true',
                        help='set next picture, alphabetical order.',
    )
    parser.add_argument('--init',
                        action='store_true',
                        help='regen config file.')
    return parser.parse_args()


def main():
    arguments = parse_argument()

    changer = WallpaperChanger()

    if arguments.filename is not None:
        is_abspath = False
        filename = ''
        if arguments.filename in changer.get_filenames():
            filename = arguments.filename
        elif os.path.exists(os.path.abspath(arguments.filename)):
            filename = os.path.abspath(arguments.filename)
            is_abspath = True
        else:
            print("'{filename}' not found".format(filename=arguments.filename))
            exit(1)

        changer.call(filename, is_abspath)
        return

    if arguments.default:
        filename = changer.config.get('Wallpaper', 'default')
        changer.call(filename)
        return

    if arguments.random:
        filenames = changer.get_filenames()
        idx = random.randrange(0, len(filenames))
        filename = filenames[idx]
        changer.call(filename)
        return

    if arguments.next:
        filenames = changer.get_filenames()
        current = changer.config.get('Wallpaper', 'current')
        idx = filenames.find(current) # -1 or 0<=idx<len
        filename = filenames[(idx + 1) % len(filenames)]
        changer.call(filename)
        return

    if arguments.init:
        changer.wrap_config.set_default(overwrite=True)
        changer.wrap_config.write()

    w = tk.Tk()
    gui = Gui(w, changer)
    gui.mainloop()


if __name__ == '__main__':
    main()
