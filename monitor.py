#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 21:18:15 2023

@author: ki
"""

import multiprocessing.dummy
import multiprocessing
import subprocess
import json
import os
import datetime as dt
from tkinter import *
from pathlib import Path


alarm = {}


def ping(ip: list):

    # if ip[0] == '127.0.0.1':
    #     return

    success = subprocess.run(
        f'ping {ip[0]} -c1 -w1 -l1', shell=True, stdout=subprocess.PIPE, encoding='utf-8')

    info = success.stdout.split('\n\n')

    if not success.returncode:
        ip[1].configure(fg='lightgreen', text=info[1].strip())
        ip[2].configure(bg='green')
        if ip[0] in alarm.keys():
            text_alert.insert(
                "insert", f'\t[#] "{ip[2].cget("text")}" на связи \n\t[#] перерыв связи {dt.datetime.now() - alarm[ip[0]]}\n ')
            del(alarm[ip[0]])
    else:
        ip[1].configure(fg='red', text=info[1].strip())
        ip[2].configure(bg='red')
        if ip[0] not in alarm.keys():
            text_alert.insert(
                "insert", f'[!] {dt.datetime.now().strftime("%d.%m.%y %H:%M:%S")}')
            text_alert.insert("insert", f' {ip[2].cget("text")}\n ')
            alarm[ip[0]] = dt.datetime.now()


def set_objects() -> list:
    """Созданиёт сетку виджетов
    и возвращает список созданных виджетов
    """
    global text_alert

    frames = [Frame(relief='ridge', bd=10) for _ in range(4)]
    set_obj = []
    btn = []
    lbl = []

    def redact_obj(obj):

        def save():

            data[str(obj)] = [ent_name.get().strip(),
                              ent_ip.get().strip(), txt.get(1.0, 'end').strip()]

            with open(file_setting, 'w') as f:
                f.write(json.dumps(data, ensure_ascii=True, indent=4))

            btn[obj-1].configure(text=data[str(obj)][0])
            lbl[obj-1].configure(text=data[str(obj)][1])
            top.destroy()

        top = Toplevel()
        top.title('Редактирование')
        head = ['Название', 'IP адрес', 'Описание']
        for n, h in enumerate(head):
            Label(top, text=h, font='Arial 24',
                  relief='solid',
                  fg='blue',
                  bd=1,
                  bg='khaki').grid(row=0 if h != 'Описание' else 2,
                                   column=n if h != 'Описание' else 0,
                                   ipadx=10,
                                   columnspan=2 if h == 'Описание' else 1,
                                   sticky='ewsn')
        ent_name = Entry(top, text=data[str(obj)]
                         [0], font='Arial 24', relief='solid')
        ent_name.insert(0, data[str(obj)][0])
        ent_name.grid(row=1, column=0, ipadx=10, sticky='ewsn')

        ent_ip = Entry(top, font='Arial 24', relief='solid')
        ent_ip.insert(0, data[str(obj)][1])
        ent_ip.grid(row=1, column=1, ipadx=10, sticky='ewsn')

        txt = Text(top, font='Arial 14', relief='solid')
        txt.insert(1.0, data[str(obj)][2])
        txt.grid(row=3, column=0, ipadx=10, columnspan=2, sticky='ewsn')

        Button(top, text='Сохранить изменения', font='Arial 24',
               relief='solid',
               fg='blue',
               bd=1,
               bg='khaki',
                  command=save).grid(row=4, column=0, ipadx=10, columnspan=2, sticky='ewsn')

    try:
        with open(file_setting, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
        for i in range(1, 61):
            data[str(i)] = ['pass', '127.0.0.1', 'object info']
        with open(file_setting, 'w') as f:
            f.write(json.dumps(data, ensure_ascii=False, indent=4))

    count = 1
    for n, fr in enumerate(frames):
        fr.pack(side='left', padx=5)
        if n != len(frames)-1:
            for wid in range(1, 21):
                btn.append(Button(fr, text=data[str(count)][0], font='Arial 10',
                                  command=lambda c=count: redact_obj(c)))
                btn[-1].grid(row=wid, column=0, pady=1, sticky='ewsn')
                lbl.append(Label(fr, text=data[str(
                    count)][1], fg='green', bg='black', font='Arial 6', width=50, height=3))
                lbl[-1].grid(row=wid, column=1, pady=1)

                set_obj.append((data[str(count)][1], lbl[-1], btn[-1]))
                count += 1
    frame_alert = frames[-1]
    Label(frame_alert, text='Сообщения', font='Arial 14 bold').pack(
        side='top', fill='both', expand=True)
    text_alert = Text(frame_alert, font='Arial 10 bold',
                      fg='purple', width=60, height=82)
    text_alert.pack(side='bottom', fill='both', expand=True)
    text_alert.insert(
        "insert", f'      [#]   Мониторинг сети запущен {dt.datetime.now().strftime("%d.%m.%y в %H:%M:%S")}   [#]\n\n')

    return set_obj


def ping_range(b):

    num_threads = 2 * multiprocessing.cpu_count()

    p = multiprocessing.dummy.Pool(num_threads)
    # with multiprocessing.dummy.Pool(num_threads) as p: не выводит результат
    #     p.map_async(ping, b)

    # for _ in b: # последовательный вызов работает корректно

    #     ping(_)

    p.map_async(ping, b)
    p.close()

    root.after(1000, lambda: ping_range(b))


if __name__ == "__main__":
    root = Tk()
    file_setting = Path(__file__).parent.resolve() / 'setting.json'
    root.title('Монитор сети')
    # os.system('sudo ip addr add 192.168.1.150/24 brd 192.168.1.255 dev eth0')

    ping_range(set_objects())

    root.mainloop()
