#!/usr/bin/env python
c=lambda k,v:globals().update({k:v})
i=lambda n:c(n,__import__(n))

i('os')
i('sys')
i('subprocess')
i('shlex')
i('argparse')
i('random')
i('itertools')

c('CONFIG_PATH',os.path.expanduser('~/.config/wallpaperchanger.conf'))

(sys.version_info.major==2 and(
    c('configparser',__import__('ConfigParser'))or c('tk',__import__('Tkinter'))or c('next',lambda o:o.next())
)or(
    i('configparser')or c('tk',__import__('tkinter'))
))

i('PIL')or i('PIL.Image')or i("PIL.ImageTk") # TODO

c("WallpaperChanger",type('WallpaperChanger',(),
  {
      '__doc__':"main class\n\n    this contains filenames, config.\n",
      '__init__':lambda s:s.__dict__.update({'wrap_config':WrapConfig()})or s.wrap_config.load()or s.__dict__.update({'config':s.wrap_config.config,'base_path':os.path.expanduser(s.wrap_config.config.get('Main', 'path'))}),
      'call':lambda s,fn,ia=False:subprocess.call([l.format(file=fn if ia else os.path.join(s.base_path, fn))for l in shlex.split(s.config.get('Main','command'))])==0and(s.config.set('Wallpaper', 'current', fn)or s.wrap_config.write()),
      'get_filenames': lambda s:sorted(os.listdir(s.base_path)),
        'get_abspath': lambda s,fn:os.path.join(s.base_path, fn),
  }
))

c("WrapConfig",type("WrapConfig",(),{
    "__doc__":"""\nWrap ConfigParser,\n""",
    "DEFAULT":{'Main':{'path':'~/picture/wallpaper','command':'feh --bg-fill {file}',},'Wallpaper':{'current':'','default':'',}},
    "__init__":lambda s:s.__dict__.update({"config":configparser.ConfigParser()})or None,
    'load':lambda s:s.is_exists()and (s.config.read(CONFIG_PATH)and None)or(s.set_default()or s.write()),
    'write':lambda s:(s.is_exists_parent_directory()or os.makedirs(s._get_parent_path())or True)and(lambda fp:(s.config.write(fp)and None)or fp.close())(open(CONFIG_PATH, 'w')),
    'set_default':lambda s,ow=False:[(s.config.has_section(sec)or s.config.add_section(sec))and[(ow or not s.config.has_option(sec, opt)and s.config.set(sec,option,s.DEFAULT[sec][opt]))for opt in s.DEFAULT.get(sec, {}).keys()]for sec in s.DEFAULT.keys()]and None,
    'is_exists_parent_directory':lambda s:os.path.isdir(s._get_parent_path()),
    'is_exists':lambda s:os.path.exists(CONFIG_PATH),
    '_get_parent_path':lambda s:os.path.abspath(os.path.dirname(CONFIG_PATH)),
}))

c("Gui",type("Gui",(tk.Frame,),{
    '__doc__':'\nGraphical interface for wallpaper selecting.\n',
    'THUMBNAIL_SIZE':(400, 400),
    '__init__':lambda s,master,ch: s.__dict__.update({'_changer':ch,'filename':None,'key':''})or tk.Frame.__init__(s, master)or s.pack()or s.create_widgets()or s.init_binds()or s.set_listbox_filenames()or s.set_thumbnail(),
    'create_widgets':lambda s:(lambda fl:fl.pack({'fill': tk.BOTH, 'side': 'left'})or s.__dict__.update({'elem_listbox':tk.Listbox(fl),'elem_entry':tk.Entry(fl,textvariable=s.gen_entry_callback())}))(tk.Frame(s))or s.elem_listbox.pack({'side': 'top', 'fill': tk.BOTH})or s.elem_entry.pack({'side': 'bottom'})or s.elem_entry.focus_set()or PIL is None or(lambda fr:fr.pack({'fill': tk.BOTH})or s.__dict__.update({'elem_thumbnail':tk.Label(fr)}) or s.elem_thumbnail.pack({'side': 'right',}))(tk.Frame(s))or None,
    'init_binds':lambda s:s.master.bind('<Escape>', s.action_destroy)and s.master.bind('<Return>', s.action_finish)and s.master.bind('<Tab>', s.action_completion)and s.elem_listbox.bind('<<ListboxSelect>>', s.action_select)and s.elem_listbox.bind('<Double-Button-1>', s.action_finish)and None,
    'action_destroy':lambda s,*args:s.master.destroy(),
    'action_select':lambda s,e=None:(e and s.__dict__.update({'filename':s.elem_listbox.get(int(s.elem_listbox.curselection()[0]))})or s.set_thumbnail(s.filename))or None,
    'action_finish':lambda s,*args:(s.filename and s._changer.call(s.filename)or s.action_destroy()),
    'action_completion':lambda s,*args:(lambda names:(lambda idx:idx and (s.elem_entry.delete(0, tk.END)or s.elem_entry.insert(0, names[0][:idx])and None))(next(itertools.dropwhile(lambda idx:not all(names[0][:idx]in l for l in names[1:]),(len(names[0])-x for x in range(len(names[0])))),None)))(s.get_filtered_filenames(s.key))or 'break',
    'gen_entry_callback':lambda s:(lambda string_var:string_var.trace('w', lambda name, index, mode, sv=string_var: (lambda sv:(lambda names:s.set_listbox_filenames(names)or len(names)==1 and(s.__dict__.update({'filename':names[0]})or s.set_thumbnail(names[0])or True)or(s.__dict__.update({'filename':None})or s.set_thumbnail()))(s.__dict__.update({'key':sv.get()})or s.get_filtered_filenames(s.key)))(sv))and None or string_var)(tk.StringVar())
    

}))


def set_listbox_filenames(s, filenames=None):
    s.elem_listbox.delete(0, s.elem_listbox.size() - 1)
    if filenames is None:
        filenames = s._changer.get_filenames()
    for name in filenames:
        s.elem_listbox.insert(tk.END, name)
Gui.set_listbox_filenames = set_listbox_filenames

def set_thumbnail(s, ifilename=None):
    if PIL is not None:
        size = s.THUMBNAIL_SIZE
        thumbnail = PIL.Image.new('RGBA', size, (0, 0, 0, 0))
        if ifilename is not None:
            filename = s._changer.get_abspath(ifilename)
            image = PIL.Image.open(filename)
            image.thumbnail(size, PIL.Image.ANTIALIAS)

            offset_x = int(max((size[0] - image.size[0]) / 2, 0))
            offset_y = int(max((size[1] - image.size[1]) / 2, 0))
            thumbnail.paste(image, (offset_x, offset_y))

        s.thumbnail = PIL.ImageTk.PhotoImage(thumbnail)
        s.elem_thumbnail.configure(image=s.thumbnail)
Gui.set_thumbnail=set_thumbnail

def get_filtered_filenames(s, keyword):
    return [x for x in s._changer.get_filenames() if x.find(keyword) == 0]
Gui.get_filtered_filenames=get_filtered_filenames


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
            print("'{file}' not found".format(file=arguments.filename))
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
