from datetime import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import tkinter.font as tkFont
import configparser
from time import sleep

from matplotlib import style
import matplotlib.pyplot as plt
from HPIB import HP4155

boxw=4
valuew=boxw
combow=boxw+1
default_fontsize=16

scripts=configparser.ConfigParser()
scripts.read(__file__.rsplit('\\', 1)[0] + '\\Scripts.ini')
user_scripts=configparser.ConfigParser()
user_scripts.read(__file__.rsplit('\\', 1)[0] + '\\UserScripts.ini')

def exptofloat(s):
    try:    
        return float(s)
    except:
        if "m" in s:
            return float(s.replace("m","e-3"))
        if "u" in s:
            return float(s.replace("u","e-6"))
        if "n" in s:
            return float(s.replace("n","e-9"))
        if "p" in s:
            return float(s.replace("p","e-12"))
        raise

class App(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        
        frm = ttk.Frame(self, padding=10)
        frm.grid()

        custom_font = tkFont.Font(family="Arial", size=default_fontsize)
        small_font = tkFont.Font(family="Arial", size=default_fontsize-2)
        big_font = tkFont.Font(family="Arial", size=default_fontsize+2)
        
        Save_path = tk.Entry(frm, width=50, font=custom_font)
        Save_path.grid(column=0, row=0, columnspan=10, sticky='w')
        Dir_Select = tk.Button(frm, text='Save dir', font=custom_font, command=lambda: OnDirSelect())
        Dir_Select.grid(column=11, row=0)

        smu1_enable=tk.BooleanVar()
        smu2_enable=tk.BooleanVar()
        smu3_enable=tk.BooleanVar()
        smu4_enable=tk.BooleanVar()
        vsu1_enable=tk.BooleanVar()
        vsu2_enable=tk.BooleanVar()
        vmu1_enable=tk.BooleanVar()
        vmu2_enable=tk.BooleanVar()

        def OnDirSelect():
            path=filedialog.askdirectory()
            Save_path.delete(0, tk.END)
            Save_path.insert(0, path)
        
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

        def SendConfig(self):
            global HP

            HP.disable_all()
            if smu1_enable.get():
                HP.set_SMU( "SMU1", SMU1V.get(), SMU1I.get(), SMU1M.get(), SMU1F.get(), SMU1C.get())
                HP.beep()

            if smu2_enable.get():
                HP.set_SMU("SMU2", SMU2V.get(), SMU2I.get(), SMU2M.get(), SMU2F.get(), SMU2C.get())
                HP.beep()

            if smu3_enable.get():
                HP.set_SMU("SMU3", SMU3V.get(), SMU3I.get(), SMU3M.get(), SMU3F.get(), SMU3C.get())
                HP.beep()
            
            if smu4_enable.get():
                HP.set_SMU("SMU4", SMU4V.get(), SMU4I.get(), SMU4M.get(), SMU4F.get(), SMU4C.get())
                HP.beep()

            if vsu1_enable.get():
                HP.set_VSMU("VSU1", VSU1V.get(), VSU1F.get())
                HP.beep()

            if vsu2_enable.get():
                HP.set_VSMU("VSU2", VSU2V.get(), VSU2F.get())
                HP.beep()

            HP.set_var("VAR1", exptofloat(var1_start.get()), exptofloat(var1_stop.get()), exptofloat(var1_step.get()))

            if "VAR2" in self.func:
                HP.set_var("VAR2", exptofloat(var2_start.get()), exptofloat(var2_stop.get()), exptofloat(var2_step.get()))

            HP.set_axis("X", x_trace.get(), self.x_scale.get(), exptofloat(x_start.get()), exptofloat(x_stop.get()))
            HP.set_axis("Y1", y1_trace.get(), self.y1_scale.get(), exptofloat(y1_start.get()), exptofloat(y1_stop.get()))
            trace_list=[x_trace.get(), y1_trace.get()]

            if "-" not in y2_trace.get():
                trace_list.append(y2_trace.get())
                HP.set_axis("Y2", y2_trace.get(), self.y2_scale.get(), exptofloat(y2_start.get()), exptofloat(y2_stop.get()))

                
            for trace in save_list.get().split(","):
                if trace.strip(" ") not in trace_list:
                    trace_list.append(trace.strip(" "))

            HP.user_function(ufunc.get())
            HP.save_list=trace_list

            HP.term=script.get()

            Meas_btn.config(text="Measure\n", state=tk.NORMAL)

        def OnMeasure(self):

            if not Save_path.get():
                OnDirSelect()

            global HP
            HP.Stop_flag=False
            HP.IntTime=IntTime_combo.get()
            HP.DelayTime=float(DelayTime_entry.get())*1e-3
            HP.HoldTime=float(HoldTime_entry.get())*1e-3
            HP.SweepMode=Sweep_combo.get()
            HP.StopCond=Stopat_combo.get()
            HP.measure()

            self.StartTime=datetime.now()
            Meas_btn.config(text=f"Measuring...\n{(datetime.now()-self.StartTime).seconds} s", state=tk.DISABLED)
            self.after(500, check_measure)
        
        def check_measure():
            global HP
            if HP.State=="MEAS":
                Meas_btn.config(text=f"Measuring...\n{(datetime.now()-self.StartTime).seconds} s", state=tk.DISABLED)
                self.after(500, check_measure)
                return 0
            
            if not HP.Stop_flag:
                Meas_btn.config(text="Measurement\ncomplete")
                df=HP.get_data()
                save_path=Save_path.get() + "/" + HP.term + "-" + datetime.now().strftime('%y%m%d %H%M%S') + ".csv"
                df.to_csv(save_path, float_format='%+.5E')
                fig, ax = plt.subplots()
                ax.plot(df[x_trace.get()], df[y1_trace.get()])
                ax.set_xlabel(x_trace.get())
                ax.set_ylabel(y1_trace.get())
                if "-" not in y2_trace.get():
                    ax2 = ax.twinx()
                    ax2.plot(df[x_trace.get()], df[y2_trace.get()])
                    ax2.set_ylabel(y2_trace.get())
                fig.savefig(save_path.replace(".csv", ".png"), dpi=300)
                Meas_btn.config(text="Measure\n", state=tk.NORMAL)
                plt.show()
            

        def OnStop(self):
            global HP
            HP.Stop_flag=True
            Meas_btn.config(text="Measure", state=tk.NORMAL)
            HP.stop()

        def LoadScript(self):
            global HP
            if script.get() == "Save":
                SaveScript(self)
                return 0
            
            if script.get() == "Reload":
                scripts.read(__file__.rsplit('\\', 1)[0] + '\\MainScripts2.ini')
                user_scripts.read(__file__.rsplit('\\', 1)[0] + '\\UserScripts.ini')
                script.config(values=scripts.sections()+user_scripts.sections()+['Reload', 'Save'])
                return 0

            if script.get() in scripts.sections():
                for child in frm.winfo_children():
                    for widget in child.winfo_children():
                        if widget.winfo_name() in scripts[script.get()].keys():
                            try:
                                widget.config(state=tk.NORMAL)
                                widget.delete(0, tk.END)
                                widget.insert(0, scripts[script.get()][widget.winfo_name()])
                            except:
                                widget.deselect()
                                if "True" in scripts[script.get()][widget.winfo_name()]:
                                    widget.select()
                frm.after(1, lambda: on_button_toggle())
                return 0
            
            if script.get() in user_scripts.sections():
                for child in frm.winfo_children():
                    for widget in child.winfo_children():
                        if widget.winfo_name() in user_scripts[script.get()].keys():
                            try:
                                widget.config(state=tk.NORMAL)
                                widget.delete(0, tk.END)
                                widget.insert(0, user_scripts[script.get()][widget.winfo_name()])
                            except:
                                widget.deselect()
                                if "True" in user_scripts[script.get()][widget.winfo_name()]:
                                    widget.select()
                frm.after(1, lambda: on_button_toggle())
                return 0

        def SaveScript(self):
            new_script=configparser.ConfigParser()
            ScriptName=tk.simpledialog.askstring("Dialog", prompt="Enter script name:", initialvalue=None, show=None, parent=None)
            new_script.add_section(ScriptName)
            new_script[ScriptName]["smu1"]=str(smu1_enable.get())
            new_script[ScriptName]["smu2"]=str(smu2_enable.get())
            new_script[ScriptName]["smu3"]=str(smu3_enable.get())
            new_script[ScriptName]["smu4"]=str(smu4_enable.get())
            new_script[ScriptName]["vsu1"]=str(vsu1_enable.get())
            new_script[ScriptName]["vsu2"]=str(vsu2_enable.get())
            new_script[ScriptName]["vmu1"]=str(vmu1_enable.get())
            new_script[ScriptName]["vmu2"]=str(vmu2_enable.get())
            for child in frm.winfo_children():
                for widget in child.winfo_children():
                    if "!" not in widget.winfo_name():
                        try:
                            new_script[ScriptName][widget.winfo_name()]=widget.get()
                        except:
                            pass
            with open(__file__.rsplit('\\', 1)[0] + '\\UserScripts.ini', 'a') as configfile:
                new_script.write(configfile)

######################### SMU box

        smubox=ttk.Frame(frm, padding=2)
        smubox.grid(column=0, row=1, rowspan=8, columnspan=5)
        
        #### SMU1
        
        SMU1E = tk.Checkbutton(smubox, text="SMU1", variable=smu1_enable, onvalue=True, offvalue=False, command=on_button_toggle, name="smu1", font=custom_font)
        SMU1E.select()
        SMU1E.grid(column=0, row=1, sticky='w')
        
        SMU1V = tk.Entry(smubox, width=boxw, name="smu1_vname", font=custom_font)
        SMU1V.grid(column=1, row=1)
        SMU1V.insert(0, "V1")
        
        SMU1I = tk.Entry(smubox, width=boxw, name="smu1_iname", font=custom_font)
        SMU1I.grid(column=2, row=1)
        SMU1I.insert(0, "I1")
        
        smu1_mode=tk.StringVar()
        SMU1M = ttk.Combobox(smubox, textvariable=smu1_mode, width=combow, values=["COMM", "I", "V"], name="smu1_mode", font=custom_font)
        SMU1M.grid(column=3, row=1)
        SMU1M.set('COMM')
        
        smu1_func=tk.StringVar()
        SMU1F = ttk.Combobox(smubox, textvariable=smu1_func, width=combow, values=["CONS", "VAR1", "VAR2", "VARD"], name="smu1_func", font=custom_font)
        SMU1F.grid(column=4, row=1)
        SMU1F.bind("<<ComboboxSelected>>", lambda event: on_button_toggle())
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
        SMU2V.insert(0, "V2")
        
        SMU2I = tk.Entry(smubox, width=boxw, name="smu2_iname", font=custom_font)
        SMU2I.grid(column=2, row=2)
        SMU2I.insert(0, "I2")
        
        smu2_mode=tk.StringVar()
        SMU2M = ttk.Combobox(smubox, textvariable=smu2_mode, width=combow, values=["COMM", "I", "V"], name="smu2_mode", font=custom_font)
        SMU2M.grid(column=3, row=2)
        SMU2M.insert(0, 'V')
        
        smu2_func=tk.StringVar()
        SMU2F = ttk.Combobox(smubox, textvariable=smu2_func, width=combow, values=["CONS", "VAR1", "VAR2", "VARD"], name="smu2_func", font=custom_font)
        SMU2F.grid(column=4, row=2)
        SMU2F.bind("<<ComboboxSelected>>", lambda event: on_button_toggle())
        SMU2F.insert(0, 'VAR2')

        SMU2C = ttk.Entry(smubox, width=boxw, name="smu2_comp", font=custom_font)
        SMU2C.grid(column=5, row=2)
        SMU2C.insert(0, "--")

        #### SMU3
        
        SMU3E = tk.Checkbutton(smubox, text="SMU3", variable=smu3_enable, onvalue=True, offvalue=False, command=on_button_toggle, name="smu3", font=custom_font)
        SMU3E.select()
        SMU3E.grid(column=0, row=3, sticky='w')
        
        SMU3V = tk.Entry(smubox, width=boxw, name="smu3_vname", font=custom_font)
        SMU3V.grid(column=1, row=3)
        SMU3V.insert(0, "V3")
        
        SMU3I = tk.Entry(smubox, width=boxw, name="smu3_iname", font=custom_font)
        SMU3I.grid(column=2, row=3)
        SMU3I.insert(0, "I3")
        
        smu3_mode=tk.StringVar()
        SMU3M = ttk.Combobox(smubox, textvariable=smu3_mode, width=combow, values=["COMM", "I", "V"], name="smu3_mode", font=custom_font)
        SMU3M.grid(column=3, row=3)
        SMU3M.insert(0, 'V')
        
        smu3_func=tk.StringVar()
        SMU3F = ttk.Combobox(smubox, textvariable=smu3_func, width=combow, values=["CONS", "VAR1", "VAR2", "VARD"], name="smu3_func", font=custom_font)
        SMU3F.grid(column=4, row=3)
        SMU3F.bind("<<ComboboxSelected>>", lambda event: on_button_toggle())
        SMU3F.insert(0, 'VAR1')

        SMU3C = ttk.Entry(smubox, width=boxw, name="smu3_comp", font=custom_font)
        SMU3C.grid(column=5, row=3)
        SMU3C.insert(0, "--")

        #### SMU4
        
        SMU4E = tk.Checkbutton(smubox, text="SMU4", variable=smu4_enable, onvalue=True, offvalue=False, command=on_button_toggle, name="smu4", font=custom_font)
        SMU4E.select()
        SMU4E.grid(column=0, row=4, sticky='w')
        
        SMU4V = tk.Entry(smubox, width=boxw, name="smu4_vname", font=custom_font)
        SMU4V.grid(column=1, row=4)
        SMU4V.insert(0, "V4")
        
        SMU4I = tk.Entry(smubox, width=boxw, name="smu4_iname", font=custom_font)
        SMU4I.grid(column=2, row=4)
        SMU4I.insert(0, "I4")
        
        smu4_mode=tk.StringVar()
        SMU4M = ttk.Combobox(smubox, textvariable=smu4_mode, width=combow, values=["COMM", "I", "V"], name="smu4_mode", font=custom_font)
        SMU4M.grid(column=3, row=4)
        SMU4M.insert(0, 'COMM')
        
        smu4_func=tk.StringVar()
        SMU4F = ttk.Combobox(smubox, textvariable=smu4_func, width=combow, values=["CONS", "VAR1", "VAR2", "VARD"], name="smu4_func", font=custom_font)
        SMU4F.grid(column=4, row=4)
        SMU4F.bind("<<ComboboxSelected>>", lambda event: on_button_toggle())
        SMU4F.insert(0, 'CONS')

        SMU4C = ttk.Entry(smubox, width=boxw, name="smu4_comp", font=custom_font)
        SMU4C.grid(column=5, row=4)
        SMU4C.insert(0, "--")

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
        varbox.grid(column=8, row=1, rowspan=4, columnspan=4)

        tk.Label(varbox, text="Start", font=small_font).grid(column=1, row=0)
        tk.Label(varbox, text="Stop", font=small_font).grid(column=2, row=0)
        tk.Label(varbox, text="Step", font=small_font).grid(column=3, row=0)
        tk.Label(varbox, text="Comp", font=small_font).grid(column=4, row=0)

        tk.Label(varbox, text="VAR1", font=small_font).grid(column=0, row=1, sticky='w')

        var1_start = tk.Entry(varbox, width=valuew, font=small_font, name="var1_start")
        var1_start.grid(column=1, row=1)
        var1_start.insert(0, 0)

        var1_stop = tk.Entry(varbox, width=valuew, font=small_font, name="var1_stop")
        var1_stop.grid(column=2, row=1)
        var1_stop.insert(0, 5)

        var1_step = tk.Entry(varbox, width=valuew, font=small_font, name="var1_step")
        var1_step.grid(column=3, row=1)
        var1_step.insert(0, .1)

        var1_comp = tk.Entry(varbox, width=valuew, font=small_font, name="var1_comp")
        var1_comp.grid(column=4, row=1)
        var1_comp.insert(0, 10e-3)

        tk.Label(varbox, text="VAR2", font=small_font).grid(column=0, row=2, sticky='w')

        var2_start = tk.Entry(varbox, width=valuew, font=small_font, name="var2_start")
        var2_start.grid(column=1, row=2, padx=1)
        var2_start.insert(0, 0.1)

        var2_stop = tk.Entry(varbox, width=valuew, font=small_font, name="var2_stop")
        var2_stop.grid(column=2, row=2)
        var2_stop.insert(0, 0.1)

        var2_step = tk.Entry(varbox, width=valuew, font=small_font, name="var2_step")
        var2_step.grid(column=3, row=2)
        var2_step.insert(0, 1)

        var2_comp = tk.Entry(varbox, width=valuew, font=small_font, name="var2_comp")
        var2_comp.grid(column=4, row=2)
        var2_comp.insert(0, 10e-3)

        tk.Label(varbox, text="Func", font=small_font).grid(row=3, column=0, sticky='w')
        ufunc = tk.Entry(varbox, width=18, font=small_font, name="ufunc")
        ufunc.grid(row=3, column=1, columnspan=4, padx=(2, 0), sticky='w')
        ufunc.insert(0, "Vf=VM2-VM1")

        tk.Label(varbox, text="Trace", font=small_font).grid(column=1, row=5)
        tk.Label(varbox, text="Start", font=small_font).grid(column=2, row=5)
        tk.Label(varbox, text="Stop", font=small_font).grid(column=3, row=5)
        tk.Label(varbox, text="Scale", font=small_font).grid(column=4, row=5)

        tk.Label(varbox, text="X", font=small_font).grid(column=0, row=6, sticky='w')

        x_trace = tk.Entry(varbox, width=valuew, font=small_font, name="x_trace")
        x_trace.grid(column=1, row=6, padx=1)
        x_trace.insert(0, "Vg")

        x_start = tk.Entry(varbox, width=valuew, font=small_font, name="x_start")
        x_start.grid(column=2, row=6)
        x_start.insert(0, 0)

        x_stop = tk.Entry(varbox, width=valuew, font=small_font, name="x_stop")
        x_stop.grid(column=3, row=6)
        x_stop.insert(0, 5)

        self.x_scale=tk.StringVar()    
        self.x_scale.set("LIN")   
        x_scale_box = ttk.Combobox(varbox, textvariable=self.x_scale, width=valuew, font=small_font, values=["LIN", "LOG"], name="x_scale")
        x_scale_box.grid(column=4, row=6, pady=(3, 2))
        

        tk.Label(varbox, text="Y1", font=small_font).grid(column=0, row=7, sticky='w')

        y1_trace = tk.Entry(varbox, width=valuew, font=small_font, name="y1_trace")
        y1_trace.grid(column=1, row=7)
        y1_trace.insert(0, "Id")

        y1_start = tk.Entry(varbox, width=valuew, font=small_font, name="y1_start")
        y1_start.grid(column=2, row=7)
        y1_start.insert(0, 0)

        y1_stop = tk.Entry(varbox, width=valuew, font=small_font, name="y1_stop")
        y1_stop.grid(column=3, row=7)
        y1_stop.insert(0, 1e-2)

        self.y1_scale=tk.StringVar()
        self.y1_scale.set("LIN")        
        y1_scale_box = ttk.Combobox(varbox, textvariable=self.y1_scale, width=valuew, font=small_font, values=["LIN", "LOG"], name="y1_scale")
        y1_scale_box.grid(column=4, row=7, pady=(3, 2))

        tk.Label(varbox, text="Y2", font=small_font).grid(column=0, row=8, sticky='w')

        y2_trace = tk.Entry(varbox, width=valuew, font=small_font, name="y2_trace")
        y2_trace.grid(column=1, row=8, padx=1)
        y2_trace.insert(0, "--")

        y2_start = tk.Entry(varbox, width=valuew, font=small_font, name="y2_start")
        y2_start.grid(column=2, row=8)
        y2_start.insert(0, "--")

        y2_stop = tk.Entry(varbox, width=valuew, font=small_font, name="y2_stop")
        y2_stop.grid(column=3, row=8)
        y2_stop.insert(0, "--")

        self.y2_scale=tk.StringVar() 
        self.y2_scale.set("LIN")        
        y2_scale_box = ttk.Combobox(varbox, textvariable=self.y2_scale, width=valuew, font=small_font, values=["LIN", "LOG"], name="y2_scale")
        y2_scale_box.grid(column=4, row=8, pady=(3, 2))

        tk.Label(varbox, text="Trace", font=small_font).grid(row=9, column=0, sticky='w')
        save_list = tk.Entry(varbox, width=4*boxw, font=small_font, name="save_list")
        save_list.grid(row=9, column=1, columnspan=4, sticky='w')
        save_list.insert(0, "Vg, Id")

        tk.Label(varbox, text="Load", font=small_font).grid(row=10, column=0, sticky='w')
        script = ttk.Combobox(varbox, width=3*boxw, font=small_font, values=scripts.sections()+user_scripts.sections()+['Reload', 'Save'], name="!script")
        script.grid(row=10, column=1, columnspan=4, sticky='w')
        script.bind("<<ComboboxSelected>>", lambda event: LoadScript(self))
        script.insert(0, "Id x Vgs")

        ########################## CtrlBox

        ctrlbox=ttk.Frame(frm, padding=2)
        ctrlbox.grid(column=13, row=0, rowspan=12, columnspan=7, sticky='n')

        style = ttk.Style()
        style.configure('Large.TButton', font=('Helvetica', 18))
        style.configure('Small.TButton', font=('Helvetica', 14))

        Config_btn = ttk.Button(ctrlbox, text='Send Config', style='Small.TButton', command=lambda: SendConfig(self))
        Config_btn.grid(column=0, row=0, columnspan=3, rowspan=2, ipadx=10, ipady=5)

        Meas_btn = ttk.Button(ctrlbox, text='Measure\n', style='Large.TButton', command=lambda: OnMeasure(self))
        Meas_btn.grid(column=0, row=3, columnspan=3, rowspan=5, ipadx=20, ipady=15, pady=5)
        Meas_btn.config(text="Measurement\nnot loaded", state=tk.DISABLED)        

        IntTime_txt = tk.Label(ctrlbox, text="Int Time", font=small_font)
        IntTime_txt.grid(column=0, row=10, padx=(10, 0), sticky='w')
        IntTime_combo = ttk.Combobox(ctrlbox, width=combow+2, font=small_font, values=["SHORt", "MEDium", "LONG"], name="!int_time")
        IntTime_combo.grid(column=1, row=10, columnspan=2, padx=(0, 10))
        IntTime_combo.set("SHORt")

        DelayTime_txt = tk.Label(ctrlbox, text="DTime", font=small_font)
        DelayTime_txt.grid(column=0, row=11, padx=(10, 0), sticky='w')
        DelayTime_entry = tk.Entry(ctrlbox, width=combow, font=small_font, name="!delay_time")
        DelayTime_entry.grid(column=1, row=11, sticky='w')
        DelayTime_entry.insert(0, 1)
        DelayTime_unit = tk.Label(ctrlbox, text="ms", font=small_font)
        DelayTime_unit.grid(column=2, row=11, padx=(0, 10), sticky='w')

        HoldTime_txt = tk.Label(ctrlbox, text="HTime", font=small_font)
        HoldTime_txt.grid(column=0, row=12, padx=(10, 0), sticky='w')
        HoldTime_entry = tk.Entry(ctrlbox, width=combow, font=small_font, name="!hold_time")
        HoldTime_entry.grid(column=1, row=12, sticky='w')
        HoldTime_entry.insert(0, 1)
        HoldTime_unit = tk.Label(ctrlbox, text="ms", font=small_font)
        HoldTime_unit.grid(column=2, row=12, padx=(0, 10), sticky='w')

        Sweep_txt = tk.Label(ctrlbox, text="Sweep", font=small_font)
        Sweep_txt.grid(column=0, row=13, padx=(10, 0), sticky='w')
        Sweep_combo = ttk.Combobox(ctrlbox, width=combow+2, font=small_font, values=["SINGle", "DOUBle"], name="!sweep")
        Sweep_combo.grid(column=1, row=13, columnspan=2, padx=(0, 10))
        Sweep_combo.set("SINGle")

        Stopat_txt = tk.Label(ctrlbox, text="Stop at", font=small_font)
        Stopat_txt.grid(column=0, row=14, padx=(10, 0), sticky='w')
        Stopat_combo = ttk.Combobox(ctrlbox, width=combow+2, font=small_font, values=["OFF", "COMPliance", "ABNormal"], name="!stopat")
        Stopat_combo.grid(column=1, row=14, columnspan=2, padx=(0, 10))
        Stopat_combo.set("OFF")

        Stop_btn = ttk.Button(ctrlbox, text='Stop', style='Small.TButton', command=lambda: OnStop(self))
        Stop_btn.grid(column=0, row=15, columnspan=3, rowspan=2, ipady=5, pady=(10, 0))

        frm.after(100, lambda: LoadScript(self))

def conn_fail():
    def on_close():
        global HP
        root.destroy()

    def connect():
        global HP
        try:
            HP=HP4155(f"GPIB0::{GPIB_Spinbox.get()}", debug=False)
        except:
            return 1
        root.destroy()

    def on_debug():
        global HP
        HP=HP4155("GPIB0::17", debug=True)
        root.destroy()

    global root
    root = tk.Tk()
    root.title("Set GPIB Address")
    frm = ttk.Frame(root, padding=10)
    frm.grid()

    style = ttk.Style()
    style.configure('TButton', font=('Helvetica', 18))

    ttk.Label(frm, text="Waiting for HP4155", font=tkFont.Font(family="Arial", size=default_fontsize+2)).grid(column=0, row=0, columnspan=2)
    ttk.Button(frm, text="Retry", command=connect).grid(column=0, row=1, ipadx=10, ipady=15, padx=5, pady=10)
    ttk.Button(frm, text="Debug", command=lambda: on_debug()).grid(column=1, row=1, ipadx=10, ipady=15, padx=5, pady=10)
    ttk.Button(frm, text="Quit", command=on_close).grid(column=0, row=3, padx=5, columnspan=2, ipady=5, pady=10)
    ttk.Label(frm, text="GPIB:", font=tkFont.Font(family="Arial", size=default_fontsize)).grid(column=0, row=2, columnspan=2, pady=10, padx=(15,5), sticky='w')
    GPIB_Spinbox = ttk.Spinbox(frm, from_=0, to=25, width=3, font=tkFont.Font(family="Arial", size=default_fontsize+2))
    GPIB_Spinbox.set(17)
    GPIB_Spinbox.grid(column=1, row=2, padx=(6, 0), sticky='w')
     
    root.protocol('WM_DELETE_WINDOW', on_close)
    root.mainloop()

def donothing():
    return 0

def string_comm():
    def Writebox(msg):
        # AnsBox.delete(0, tk.END)
        AnsBox.insert('1.0', msg + "\n")

    global HP
    root = tk.Tk()
    root.title("Serial IO")
    frm = ttk.Frame(root, padding=10)
    frm.grid()

    style = ttk.Style()
    style.configure('TButton', font=('Helvetica', 18))

    from tkinter.scrolledtext import ScrolledText

    ttk.Label(frm, text="I/O:", font=tkFont.Font(family="Arial", size=default_fontsize+2)).grid(column=0, row=0, columnspan=6, sticky='w')
    ttk.Button(frm, text="Send", command=lambda: HP.write(MsgBox.get().strip("\n"))).grid(column=0, row=1, padx=10, sticky='w')
    ttk.Button(frm, text="Read", command=lambda: Writebox(HP.inst.read())).grid(column=1, row=1, padx=0, sticky='w')
    ttk.Button(frm, text="Query", command=lambda: Writebox(HP.ask(MsgBox.get().strip("\n")))).grid(column=2, row=1, padx=10, sticky='w')
    MsgBox=ttk.Combobox(frm, width=31, values=["*IDN?", "SYST:ERR?"])
    MsgBox.grid(column=0, row=2, columnspan=6, ipadx=100, padx=5, sticky='w')
    MsgBox.insert(0, "*IDN?")
    AnsBox=ScrolledText(frm, width=24, height=10)
    AnsBox.grid(column=0, row=3, columnspan=6, ipadx=100, padx=5)

    root.mainloop()

try:
    HP=HP4155("GPIB0::17", debug=False)
except:
    conn_fail()

if "HP" in locals():
    myapp = App()
    menubar=tk.Menu(myapp)
    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label="Change GPIB", command=conn_fail)
    filemenu.add_command(label="String I/O", command=string_comm)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=lambda: myapp.master.destroy())
    menubar.add_cascade(label="Command", menu=filemenu)
    myapp.master.title("HPIB")
    myapp.master.maxsize(1280, 720)

    myapp.master.config(menu=menubar)
    myapp.mainloop()

