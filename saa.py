# -*- coding: utf-8 -*-
__version__ = "0.0.7"
__author__ = "Mikhail Chermenskiy <m.interstate@gmail.com>"

import codecs
import math
import os
import shutil
import sys
from datetime import datetime
from tkinter import (DISABLED, END, Button, Entry, Frame, Label, Listbox, Menu,
                     Radiobutton, Scrollbar, Tk, filedialog, messagebox)

container = []
countfiler = 0
resDir = ''
sdir = ''
f_amount = 0

def main_quit():  # Выход из программы
    if messagebox.askyesno("Выход", "Вы действительно хотите выйти?"):
        global root
        root.destroy()

def about():
    messagebox.showinfo("SAA", "Программа для поиска и архивирования.\nСпециально для ADV Group. 2017")

def askdir():
    return filedialog.askdirectory()

def askfile():
    file_opt = options = {}
    options['defaultextension'] = '.csv'
    options['filetypes'] = [('Файл с разделителями', '.csv'),]
    options['initialdir'] = 'C:\\'
    options['initialfile'] = 'export.csv'
    options['parent'] = root
    options['title'] = 'Экспорт результатов поиска...'
    return filedialog.asksaveasfilename(**file_opt)

def setdirpath():
    # global sdir
    sdir = filedialog.askdirectory()
    dir_text['text'] = 'Папка для поиска: %s' % sdir
    go_butt['state'] = 'normal'

def setresdirpath():
    global resDir
    resDir = askdir()
    resdir_text['text'] = 'Папка для перемещения: %s' % resDir
    mv_butt['state'] = 'normal'

def find():  # Поиск файлов
    # global resDir
    # global f_amount
    listbox.delete(0, END)
    p_words = []
    if words_var.get() == 1:
        p_words = readwordsfile()
    elif words_var.get() == 0:
        entdatestr = '%s/%s/%s' % (day_ent.get(), month_ent.get(), year_ent.get())
        brd_date = datetime.strptime(entdatestr, "%d/%m/%Y")
    for i in os.walk(sdir):
        container.append(i)
    for d, files in container:
        for f in files:
            if words_var.get() == 1: # поиск по словарю
                a = os.path.splitext(f)[0]
                for l in a.split(' '):
                    for k in p_words:
                        if k in l:
                            fi_str = os.path.join(d, f).replace('\\', '/')
                            f_amount += os.path.getsize(fi_str)
                            listbox.insert(END, fi_str)
                continue
            try: # поиск по дате
                file_date = get_date(os.path.join(d, f))
            except Exception as errgetdate:
                func_writelog(os.path.join(d, f))
                continue
            if (file_date) and (file_date < brd_date):
                fi_str = os.path.join(d, f).replace('\\', '/')
                f_amount += os.path.getsize(fi_str)
                listbox.insert(END, fi_str)
            elif not file_date:
                ersstr = 'Не удается прочитать свойства файла %s' % os.path.join(d, f)
                continue
    if (resDir) and (listbox.size()>0):
        mv_butt['state'] = 'normal'
    count_text['text'] = 'Найдено файлов: %s. Объем: %s' % (listbox.size(), func_human_size(f_amount))

def func_human_size(nbytes): # Переводим размер из байтов в удобочитаемый вид
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    human = nbytes
    rank = 0
    if nbytes != 0:
        rank = int((math.log10(nbytes)) / 3)
        rank = min(rank, len(suffixes) - 1)
        human = nbytes / (1024.0 ** rank)
    f = ('%.2f' % human).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[rank])

def func_chkdirs():
    cont = []
    for i in os.walk(sdir):
        cont.append(i)
    for d in reversed(cont): #, dirs, files in reversed(cont):
        if (os.path.exists(d)) and (not os.listdir(d)):
            os.rmdir(d)

def func_move():
    if messagebox.askyesno("Переместить", "Переместить найденные файлы?"):
        global sdir
        global resDir
        movecount = 0
        passcount = 0
        rsd = sdir.split('/')[-1] # имя папки, в которой искали
        npath = resDir + '/' + rsd # папка, в которую переносим
        files_to_move = listbox.get(0, END)
        for ftm in reversed(files_to_move):
            newpath = ftm.replace(sdir, npath)
            rdir = os.path.dirname(newpath)
            if not os.path.exists(rdir):
                try:
                    os.makedirs(rdir)
                except Exception as err:
                    func_writelog(str(err))
            try:
                shutil.move(ftm, newpath)
                func_writelog(ftm)
                movecount += 1
            except Exception as errm:
                try:
                    ftmr = newpath.replace('\u202c', '')
                    shutil.move(ftm, ftmr)
                    func_writelog(ftm)
                    movecount += 1
                    if not os.listdir(os.path.dirname(ftm)):
                        os.rmdir(os.path.dirname(ftm))
                except Exception as errmf:
                    func_writelog(str(errmf))
                    passcount += 1
                    continue
                func_writelog(str(errm))
                passcount += 1
                continue
            if not os.listdir(os.path.dirname(ftm)):
                os.rmdir(os.path.dirname(ftm))
        if (os.path.exists(sdir)) and (not os.listdir(sdir)):
            os.rmdir(sdir)
        count_text['text'] = 'Перемещено: %s. Пропущено: %s' % (movecount, passcount)
        if messagebox.askyesno("Перемещение завершено.", "Перемещение выполнено\nСохранить список перемещенных файлов?"):
            func_export(files_to_move)
        func_chkdirs()
        clearres()
        
def func_export(listfiles):
    export_file = askfile()
    fl = codecs.open(export_file, 'w', 'cp1251')
    strno = 1
    for fstring in listfiles:
        writestr = ('%s;%s;\n' % (str(strno),fstring))
        try:
            fl.write(writestr)
        except Exception as err:
            fl.write('%s;Ошибка %s;' % (str(strno),str(err)))
            continue
        strno += 1
    fl.close()
        
def func_writelog(files):
    f = codecs.open('saa.log', 'a', 'cp1251')
    ts = str(datetime.now())
    try:
        writestr = ts + ' ==> ' + files + '\n'
        f.write(writestr)
    except Exception as e:
        ss = files
        writestr = ts + ' Error: ' + str(e) + ' On: ' + ss + '\n'
        f.write(writestr)
    f.close()

def get_date(dfile):
    try:
        return datetime.fromtimestamp(int(os.path.getmtime(dfile))) # получаем дату модификации файла
    except Exception as e:
        func_writelog(str(e))

def getwordslist():
    if readwordsfile():
        messagebox.showinfo("SAA - Список слов", readwordsfile())

def wrad_change():
    if words_var.get() == 1:
        pass
    elif words_var.get() == 0:
        pass

def readwordsfile():
    try:
        wf = open('words.cfg', 'r')
        words_list = [line.strip() for line in wf]
        wf.close()
        return words_list
    except IOError as ior:
        info_str = "SAA - ошибка", "Ошибка чтения списка слов.\nУбедитесь, что файл words.cfg доступен для чтения.\nError: %s", ior
        messagebox.showinfo(info_str)
        return False

def clearres():
    if messagebox.askyesno("Очистить", "Очистить все результаты?"):
        global sdir
        global resDir
        global container
        global f_amount
        container = []
        sdir = ''
        resDir = ''
        dir_text['text'] = 'Папка для поиска не выбрана...'
        resdir_text['text'] = 'Папка для переноса не выбрана...'
        listbox.delete(0, END)
        go_butt['state'] = 'disabled'
        mv_butt['state'] = 'disabled'
        count_text['text'] = 'Найдено файлов:'
        f_amount = 0
        day_ent.delete(0, END)
        month_ent.delete(0, END)
        year_ent.delete(0, END)

# ----------- Создание главного окна
root = Tk()
root.title('SAA - Search and Arch')
root.geometry('800x600+100+100')

# ----------- МЕНЮ
m = Menu(root)
root.config(menu=m)
fm = Menu(m)  # Меню "Файл"
em = Menu(m)  # Меню "Правка"
hm = Menu(m)  # Меню "О программе"
m.add_cascade(label="Файл", menu=fm)
fm.add_command(label="Искать", command=find)
fm.add_command(label="Выход", command=main_quit)
m.add_cascade(label="Правка", menu=em)
em.add_command(label="Очистить", command=clearres)
m.add_cascade(label="?", menu=hm)
hm.add_command(label="О программе", command=about)

# ----------- ОСНОВНЫЕ ФРЕЙМЫ
topFrame = Frame(root, height=80, bd=2, relief=GROOVE)
bottomFrameLeft = Frame(root, width=300, bd=2, relief=GROOVE)
bottomFrameRight = Frame(root, bd=2, relief=GROOVE)

# ----------- ПОЛЯ ДЛЯ ДАТЫ
day_ent = Entry(topFrame, width=10)
month_ent = Entry(topFrame, width=10)
year_ent = Entry(topFrame, width=10)

# ----------- ОСНОВНОЙ ЛИСТБОКС
listbox = Listbox(bottomFrameRight, height=340, width=300, selectmode=EXTENDED)

# ----------- ТЕКСТОВЫЕ МЕТКИ
dir_text = Label(topFrame, height=1, justify=LEFT, text='Папка для поиска не выбрана...')
resdir_text = Label(topFrame, height=1, justify=LEFT, text='Папка для переноса не выбрана...')
count_text = Label(topFrame, height=1, justify=LEFT, text='Найдено файлов: ')
info_text = Label(topFrame, height=1, justify=LEFT, text='')

# ----------- КНОПКИ
setdir_butt = Button(bottomFrameLeft, text='Исх. папка', width=10, command=setdirpath)
resdir_butt = Button(bottomFrameLeft, text='Кон. папка', width=10, command=setresdirpath)
go_butt = Button(bottomFrameLeft, text='Поиск', width=10, command=find, state=DISABLED)
mv_butt = Button(bottomFrameLeft, text='Переместить', width=10, command=func_move, state=DISABLED)

# ----------- РАДИОКНОПКИ
words_var = IntVar()
words_var.set(0)
wrad0 = Radiobutton(topFrame, text='Без словаря', variable=words_var, value=0, command=wrad_change).grid(row=3, column=0, sticky=W)
wrad1 = Radiobutton(topFrame, text='Со словарем', variable=words_var, value=1, command=wrad_change).grid(row=3, column=1, sticky=W)

# ----------- СКРОЛЛБАР ДЛЯ ЛИСТБОКСА
scrollbar = Scrollbar(listbox)
scrollbar['command'] = listbox.yview
listbox['yscrollcommand'] = scrollbar.set

# ----------- УПАКОВКА ВСЕХ ОБЪЕКТОВ
topFrame.pack(side='top', fill='both')
bottomFrameLeft.pack(side='left', fill='y')
bottomFrameRight.pack(side='left', fill='both', expand=1)

Label(topFrame, text='День:').grid(row=0, column=0, sticky=W)
Label(topFrame, text='Месяц:').grid(row=1, column=0, sticky=W)
Label(topFrame, text='Год:').grid(row=2, column=0, sticky=W)

day_ent.grid(row=0, column=1)
month_ent.grid(row=1, column=1)
year_ent.grid(row=2, column=1)

dir_text.grid(row=0, column=2, sticky=W)
resdir_text.grid(row=1, column=2, sticky=W)
count_text.grid(row=2, column=2, sticky=W)
info_text.grid(row=2, column=3, sticky=E)

go_butt.pack(side='top')
mv_butt.pack(side='top')
setdir_butt.pack(side='top')
resdir_butt.pack(side='top')

listbox.pack(side='left', fill='both', expand=1)
scrollbar.pack(side='right', fill='y')

root.mainloop()
