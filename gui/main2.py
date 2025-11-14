import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
from time import sleep
from HPIB import HP4155

boxw=5
combow=boxw+2

default={
          'GPIB_addr' : 17,
          'fontsize' : 16,
          'smu1_vname' : "Vs",
          'smu1_iname' : "Is",
          'smu1_mode' : "COMM",
          'smu1_func' : "CONS",
          'smu1_comp' : "--",
          'smu2_vname' : "Vd",
          'smu2_iname' : "Id",
          'smu2_mode' : "V",
          'smu2_func' : "0.05",
          'smu2_comp' : "0.01",
          'smu3_vname' : "Vg",
          'smu3_iname' : "Ig",
          'smu3_mode' : "V",
          'smu3_func' : "VAR1",
          'smu3_comp' : "--",
          'smu4_vname' : "Vb",
          'smu4_iname' : "Ib",
          'smu4_mode' : "COMM",
          'smu4_func' : "CONS",
          'smu4_comp' : "--",
          'vsu1_vname' : "VS1",
          'vsu1_func' : "CONS",
          'vsu2_vname' : "VS2",
          'vsu2_func' : "CONS",
          'vmu1_vname' : "VM1",
          'vmu2_vname' : "VM2"}        

class App(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        
        frm = ttk.Frame(self, padding=10)
        frm.grid()

        custom_font = tkFont.Font(family="Arial", size=default['fontsize'])
        
        text_widget = tk.Entry(frm, width=50, font=custom_font).grid(column=0, row=0, columnspan=10, sticky='w')
        Dir_Select = tk.Button(frm, text='Save dir', font=custom_font).grid(column=11, row=0)

        smu1_enable=tk.BooleanVar()
        smu2_enable=tk.BooleanVar()
        smu3_enable=tk.BooleanVar()
        smu4_enable=tk.BooleanVar()
        vsu1_enable=tk.BooleanVar()
        vsu2_enable=tk.BooleanVar()
        vmu1_enable=tk.BooleanVar()
        vmu2_enable=tk.BooleanVar()
        
        def on_button_toggle():

            var1_start.config(state=tk.NORMAL)
            var1_stop.config(state=tk.NORMAL)
            var1_step.config(state=tk.NORMAL)
            var1_comp.config(state=tk.NORMAL)
            var2_start.config(state=tk.NORMAL)
            var2_stop.config(state=tk.NORMAL)
            var2_step.config(state=tk.NORMAL)
            var2_comp.config(state=tk.NORMAL)
            self.enable=[smu1_enable.get(), smu2_enable.get(), smu3_enable.get(), smu4_enable.get(), vsu1_enable.get(), vsu2_enable.get(), vmu1_enable.get(), vmu2_enable.get()]
            self.mode=[ x if self.enable[n] else None for n, x in enumerate([smu1_mode.get(),smu2_mode.get(),smu3_mode.get(),smu4_mode.get()])]
            self.func=[ x if self.enable[n] else None for n, x in enumerate([smu1_func.get(),smu2_func.get(),smu3_func.get(),smu4_func.get(),vsu1_func.get(),vsu2_func.get()])]
            i=0
            for widget in smubox.winfo_children():
                if "_" not in widget.winfo_name() and "label" not in widget.winfo_name():
                    i+=1
                    curr_state=self.enable[i-1]
                    curr_state=tk.NORMAL if curr_state else tk.DISABLED
                    continue
                widget.config(state=curr_state)
            if "VAR1" not in self.func:
                var1_start.config(state=tk.DISABLED)
                var1_stop.config(state=tk.DISABLED)
                var1_step.config(state=tk.DISABLED)
                var1_comp.config(state=tk.DISABLED)
            if "VAR2" not in self.func:
                var2_start.config(state=tk.DISABLED)
                var2_stop.config(state=tk.DISABLED)
                var2_step.config(state=tk.DISABLED)
                var2_comp.config(state=tk.DISABLED)

######################### SMU box

        smubox=ttk.Frame(frm, padding=2)
        smubox.grid(column=0, row=1, rowspan=8, columnspan=5)
        
        #### SMU1
        
        SMU1E = tk.Checkbutton(smubox, text="SMU1", variable=smu1_enable, onvalue=True, offvalue=False, command=on_button_toggle, name="smu1", font=custom_font)
        SMU1E.select()
        SMU1E.grid(column=0, row=1, sticky='w')
        
        SMU1V = tk.Entry(smubox, width=boxw, name="smu1_vname", font=custom_font)
        SMU1V.grid(column=1, row=1)
        SMU1V.insert(0, default['smu1_vname'])
        
        SMU1I = tk.Entry(smubox, width=boxw, name="smu1_iname", font=custom_font)
        SMU1I.grid(column=2, row=1)
        SMU1I.insert(0, 'IS')
        
        smu1_mode=tk.StringVar()
        SMU1M = ttk.Combobox(smubox, textvariable=smu1_mode, width=combow, values=["COMM", "I", "V"], name="smu1_mode", font=custom_font)
        SMU1M.grid(column=3, row=1)
        SMU1M.set('COMM')
        
        smu1_func=tk.StringVar()
        SMU1F = ttk.Combobox(smubox, textvariable=smu1_func, width=combow, values=["CONS", "VAR1", "VAR2", "VARD"], name="smu1_func", font=custom_font)
        SMU1F.grid(column=4, row=1)
        SMU1F.insert(0, 'CONS')

        SMU1C = ttk.Entry(smubox, width=boxw, name="smu1_comp", font=custom_font)
        SMU1C.grid(column=5, row=1)
        SMU1C.insert(0, "--")

        #### SMU2
        
        SMU2E = tk.Checkbutton(smubox, text="SMU2", variable=smu2_enable, onvalue=True, offvalue=False, command=on_button_toggle, name="smu2", font=custom_font)
        SMU2E.select()
        SMU2E.grid(column=0, row=2, sticky='w')
        
        SMU2V = tk.Entry(smubox, width=boxw, name="smu2_vname", font=custom_font)
        SMU2V.grid(column=1, row=2)
        SMU2V.insert(0, 'VD')
        
        SMU2I = tk.Entry(smubox, width=boxw, name="smu2_iname", font=custom_font)
        SMU2I.grid(column=2, row=2)
        SMU2I.insert(0, 'ID')
        
        smu2_mode=tk.StringVar()
        SMU2M = ttk.Combobox(smubox, textvariable=smu2_mode, width=combow, values=["COMM", "I", "V"], name="smu2_mode", font=custom_font)
        SMU2M.grid(column=3, row=2)
        SMU2M.insert(0, 'V')
        
        smu2_func=tk.StringVar()
        SMU2F = ttk.Combobox(smubox, textvariable=smu2_func, width=combow, values=["CONS", "VAR1", "VAR2", "VARD"], name="smu2_func", font=custom_font)
        SMU2F.grid(column=4, row=2)
        SMU2F.insert(0, 0.050)

        SMU2F = ttk.Entry(smubox, width=boxw, name="smu2_comp", font=custom_font)
        SMU2F.grid(column=5, row=2)
        SMU2F.insert(0, 10e-3)

        #### SMU3
        
        SMU3E = tk.Checkbutton(smubox, text="SMU3", variable=smu3_enable, onvalue=True, offvalue=False, command=on_button_toggle, name="smu3", font=custom_font)
        SMU3E.select()
        SMU3E.grid(column=0, row=3, sticky='w')
        
        SMU3V = tk.Entry(smubox, width=boxw, name="smu3_vname", font=custom_font)
        SMU3V.grid(column=1, row=3)
        SMU3V.insert(0, 'VG')
        
        SMU3I = tk.Entry(smubox, width=boxw, name="smu3_iname", font=custom_font)
        SMU3I.grid(column=2, row=3)
        SMU3I.insert(0, 'IG')
        
        smu3_mode=tk.StringVar()
        SMU3M = ttk.Combobox(smubox, textvariable=smu3_mode, width=combow, values=["COMM", "I", "V"], name="smu3_mode", font=custom_font)
        SMU3M.grid(column=3, row=3)
        SMU3M.insert(0, 'V')
        
        smu3_func=tk.StringVar()
        SMU3F = ttk.Combobox(smubox, textvariable=smu3_func, width=combow, values=["CONS", "VAR1", "VAR2", "VARD"], name="smu3_func", font=custom_font)
        SMU3F.grid(column=4, row=3)
        SMU3F.insert(0, 'VAR1')

        SMU3F = ttk.Entry(smubox, width=boxw, name="smu3_comp", font=custom_font)
        SMU3F.grid(column=5, row=3)
        SMU3F.insert(0, "--")

        #### SMU4
        
        SMU4E = tk.Checkbutton(smubox, text="SMU4", variable=smu4_enable, onvalue=True, offvalue=False, command=on_button_toggle, name="smu4", font=custom_font)
        SMU4E.select()
        SMU4E.grid(column=0, row=4, sticky='w')
        
        SMU4V = tk.Entry(smubox, width=boxw, name="smu4_vname", font=custom_font)
        SMU4V.grid(column=1, row=4)
        SMU4V.insert(0, 'VB')
        
        SMU4I = tk.Entry(smubox, width=boxw, name="smu4_iname", font=custom_font)
        SMU4I.grid(column=2, row=4)
        SMU4I.insert(0, default['smu4_iname'])
        
        smu4_mode=tk.StringVar()
        SMU4M = ttk.Combobox(smubox, textvariable=smu4_mode, width=combow, values=["COMM", "I", "V"], name="smu4_mode", font=custom_font)
        SMU4M.grid(column=3, row=4)
        SMU4M.insert(0, 'COMM')
        
        smu4_func=tk.StringVar()
        SMU4F = ttk.Combobox(smubox, textvariable=smu4_func, width=combow, values=["CONS", "VAR1", "VAR2", "VARD"], name="smu4_func", font=custom_font)
        SMU4F.grid(column=4, row=4)
        SMU4F.insert(0, 'CONS')

        SMU4F = ttk.Entry(smubox, width=boxw, name="smu4_comp", font=custom_font)
        SMU4F.grid(column=5, row=4)
        SMU4F.insert(0, "--")

        #### VSU1
        
        VSU1E = tk.Checkbutton(smubox, text="VS1", variable=vsu1_enable, onvalue=True, offvalue=False, command=on_button_toggle, name="vsu1", font=custom_font)
        VSU1E.grid(column=0, row=5, sticky='w')

        VSU1V = tk.Entry(smubox, width=boxw, name="vsu1_vname", font=custom_font)
        VSU1V.grid(column=1, row=5)
        VSU1V.insert(0, 'VS1')

        tk.Label(smubox, text="---", font=custom_font).grid(column=2, row=5)
        tk.Label(smubox, text="------", font=custom_font).grid(column=3, row=5)
        
        vsu1_func=tk.StringVar()
        VSU1F = ttk.Combobox(smubox, textvariable=vsu1_func, width=combow, values=["CONS", "VAR1", "VAR2", "VARD"], name="vsu1_func", font=custom_font)
        VSU1F.grid(column=4, row=5)
        VSU1F.insert(0, 'CONS')

        tk.Label(smubox, text="--", font=custom_font).grid(column=5, row=5)

        #### VSU2
        
        VSU2E = tk.Checkbutton(smubox, text="VS2", variable=vsu2_enable, onvalue=True, offvalue=False, command=on_button_toggle, name="vsu2", font=custom_font)
        VSU2E.grid(column=0, row=6, sticky='w')
        
        VSU2V = tk.Entry(smubox, width=boxw, name="vsu2_vname", font=custom_font)
        VSU2V.grid(column=1, row=6)
        VSU2V.insert(0, 'VS2')

        tk.Label(smubox, text="---", font=custom_font).grid(column=2, row=6)
        tk.Label(smubox, text="------", font=custom_font).grid(column=3, row=6)
        
        vsu2_func=tk.StringVar()
        VSU2F = ttk.Combobox(smubox, textvariable=vsu2_func, width=combow, values=["CONS", "VAR1", "VAR2", "VARD"], name="vsu2_func", font=custom_font)
        VSU2F.grid(column=4, row=6)
        VSU2F.insert(0, 'CONS')

        tk.Label(smubox, text="--", font=custom_font).grid(column=5, row=6)

        #### VMU1

        
        vmu1_enable=tk.BooleanVar()
        VMU1E = tk.Checkbutton(smubox, text="VM1", variable=vmu1_enable, onvalue=True, offvalue=False, command=on_button_toggle, name="vmu1", font=custom_font)
        VMU1E.select()
        VMU1E.grid(column=0, row=7, sticky='w')
        
        VMU1V = tk.Entry(smubox, width=boxw, name="vmu1_vname", font=custom_font)
        VMU1V.grid(column=1, row=7)
        VMU1V.insert(0, 'VM1')

        tk.Label(smubox, text="---", font=custom_font).grid(column=2, row=7)
        tk.Label(smubox, text="------", font=custom_font).grid(column=3, row=7)
        tk.Label(smubox, text="------", font=custom_font).grid(column=4, row=7)
        tk.Label(smubox, text="--", font=custom_font).grid(column=5, row=7)
        

        #### VMU2
        
        vmu2_enable=tk.BooleanVar()
        VMU2E = tk.Checkbutton(smubox, text="VM2", variable=vmu2_enable, onvalue=True, offvalue=False, command=on_button_toggle, name="vmu2", font=custom_font)
        VMU2E.select()
        VMU2E.grid(column=0, row=8, sticky='w')
        
        VMU2V = tk.Entry(smubox, width=boxw, name="vmu2_vname", font=custom_font)
        VMU2V.grid(column=1, row=8)
        VMU2V.insert(0, 'VM2')

        tk.Label(smubox, text="---", font=custom_font).grid(column=2, row=8)
        tk.Label(smubox, text="------", font=custom_font).grid(column=3, row=8)
        tk.Label(smubox, text="------", font=custom_font).grid(column=4, row=8)
        tk.Label(smubox, text="--", font=custom_font).grid(column=5, row=8)

########################## Varbox

        varbox=ttk.Frame(frm, padding=2)
        varbox.grid(column=8, row=1, rowspan=4, columnspan=4, sticky='n')

        tk.Label(varbox, text="Start", font=custom_font).grid(column=1, row=0)
        tk.Label(varbox, text="Stop", font=custom_font).grid(column=2, row=0)
        tk.Label(varbox, text="Step", font=custom_font).grid(column=3, row=0)
        tk.Label(varbox, text="Comp", font=custom_font).grid(column=4, row=0)

        tk.Label(varbox, text="VAR1", font=custom_font).grid(column=0, row=1)

        var1_start = tk.Entry(varbox, width=boxw, font=custom_font)
        var1_start.grid(column=1, row=1)
        var1_start.insert(0, 0)

        var1_stop = tk.Entry(varbox, width=boxw, font=custom_font)
        var1_stop.grid(column=2, row=1)
        var1_stop.insert(0, 5)

        var1_step = tk.Entry(varbox, width=boxw, font=custom_font)
        var1_step.grid(column=3, row=1)
        var1_step.insert(0, .1)

        var1_comp = tk.Entry(varbox, width=boxw, font=custom_font)
        var1_comp.grid(column=4, row=1)
        var1_comp.insert(0, 10e-3)

        tk.Label(varbox, text="VAR2", font=custom_font).grid(column=0, row=2)

        var2_start = tk.Entry(varbox, width=boxw, font=custom_font)
        var2_start.grid(column=1, row=2, padx=1)
        var2_start.insert(0, 0)

        var2_stop = tk.Entry(varbox, width=boxw, font=custom_font)
        var2_stop.grid(column=2, row=2)
        var2_stop.insert(0, 5)

        var2_step = tk.Entry(varbox, width=boxw, font=custom_font)
        var2_step.grid(column=3, row=2)
        var2_step.insert(0, .1)

        var2_comp = tk.Entry(varbox, width=boxw, font=custom_font)
        var2_comp.grid(column=4, row=2)
        var2_comp.insert(0, 10e-3)

        tk.Label(varbox, text="Func", font=custom_font).grid(row=3, column=0)
        save_list = tk.Entry(varbox, width=4*boxw+3, font=custom_font)
        save_list.grid(row=3, column=1, columnspan=4, sticky='w')
        save_list.insert(0, "Vf=V2-V1")

        tk.Label(varbox, text="Save", font=custom_font).grid(row=5, column=0)
        save_list = tk.Entry(varbox, width=4*boxw+3, font=custom_font)
        save_list.grid(row=5, column=1, columnspan=4, sticky='w')
        save_list.insert(0, "Vg, Id, Vd, Ig")

        tk.Label(varbox, text="Load", font=custom_font).grid(row=6, column=0)
        save_list = ttk.Combobox(varbox, width=3*boxw, font=custom_font)
        save_list.grid(row=6, column=1, columnspan=4, sticky='w')
        save_list.insert(0, "Id x Vgs")

        on_button_toggle()

def close():
    root.destroy()

def connect():
    global HP
    try:
        HP=HP4155("GPIB0::17", debug=False)
        root.destroy()
    except:
        pass
    
try:
    HP=HP4155("GPIB0::17", debug=False)
    root.destroy
except:
    root = tk.Tk()
    frm = ttk.Frame(root, padding=10)
    frm.grid()
    ttk.Label(frm, text="Waiting for HP4155", font=tkFont.Font(family="Arial", size=default['fontsize'])).grid(column=0, row=0)
    ttk.Button(frm, text="Retry", command=connect).grid(column=0, row=1)
    ttk.Button(frm, text="Quit", command=close).grid(column=1, row=1)

    root.mainloop()

if HP:

    myapp = App()
    myapp.master.title("HPIB")
    myapp.master.maxsize(1000, 720)

    myapp.mainloop()

