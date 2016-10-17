import shelve,tkinter,operator
import tkinter.messagebox
import championfilecreator
class ChampionListEditor():
    def __init__(self,master=None):
        if not master:
            self.master = tkinter.Tk()
            self.master.title("LolUtils database")
            self.master.resizable(0,0)
            self.menu = tkinter.Menu(self.master)
            self.menu.add_command(label="Recreate database",command=self.remakedata)
            self.menu.add_command(label="Add new key",command=self.newkey)
            self.master.config(menu=self.menu)
        if master == "Toplevel":
            self.master = tkinter.Toplevel()
            self.master.title("LolUtils database")
            self.master.resizable(0,0)
            self.menu = tkinter.Menu(self.master)
            self.menu.add_command(label="Recreate database",command=self.remakedata)
            self.menu.add_command(label="Add new key",command=self.newkey)
            self.master.config(menu=self.menu)
        self.datafile = shelve.open("champions")
        self.addwidgets()
        self.populate()
        if not master:
            self.master.mainloop()
    def addwidgets(self):
        self.leftmaster = tkinter.Frame(self.master)
        self.leftmaster.grid(row=0,column=0)
        self.leftframe = tkinter.Frame(self.leftmaster)
        self.leftframe.grid(row=0,column=0,columnspan=2)
        self.lbox = tkinter.Listbox(self.leftframe)
        self.lbox.grid(row=0,column=0)
        self.lbox.bind("<Double-Button-1>", self.callback)
        self.scrollbar = tkinter.Scrollbar(self.leftframe,orient=tkinter.VERTICAL)
        self.scrollbar.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)
        self.lbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.lbox.yview)
        self.datatable = tkinter.Frame(self.master)
        self.datatable.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)
        self.selected_id = tkinter.StringVar()
        self.editor = tkinter.Entry(self.datatable,textvariable=self.selected_id)
        self.editor.pack()
        self.selected_kr = tkinter.StringVar()
        self.editor_kr = tkinter.Entry(self.datatable,textvariable=self.selected_kr)
        self.editor_kr.pack()
        self.editbutton = tkinter.Button(self.datatable,text="Edit",command=self.modify)
        self.editbutton.pack()
        self.sortkey = tkinter.StringVar()
        self.sortkey.set("Name")
        self.keyselector = tkinter.OptionMenu(self.leftmaster,self.sortkey,"Name","ID","Korean")
        self.keyselector.grid(row=1,column=0)
        self.sortbutton = tkinter.Button(self.leftmaster,text="Change",command=self.changesort)
        self.sortbutton.grid(row=1,column=1)

    def changesort(self):
        if self.sortkey.get() == "Name": self.populate()
        elif self.sortkey.get() == "ID": self.populate_id()
    def newkey(self):
        newkeywin = tkinter.Toplevel()
        newkeywin.grab_set()
        newkeywin.focus_set()
        newkeywin.title("LolUtils database")
        keyname = tkinter.StringVar()
        keyid = tkinter.StringVar()
        keykr = tkinter.StringVar()
        tkinter.Label(newkeywin,text="Champion name(key)").grid(row=0,column=0)
        tkinter.Entry(newkeywin,textvariable=keyname).grid(row=0,column=1)
        tkinter.Label(newkeywin,text="Champion ID").grid(row=1,column=0)
        tkinter.Entry(newkeywin,textvariable=keyid).grid(row=1,column=1)
        tkinter.Label(newkeywin,text="Korean name").grid(row=2,column=0)
        tkinter.Entry(newkeywin,textvariable=keykr).grid(row=2,column=1)
        tkinter.Button(newkeywin,text="Add",command=lambda:self.newkey_handler(keyname,keyid,keykr,newkeywin)).grid(row=3,column=0,columnspan=2)
    def newkey_handler(self,name,id,kr,tlvl):
        if tkinter.messagebox.askyesno("","Are you sure?"):
            if name.get() in self.datafile:
                if tkinter.messagebox.askyesno("","The key already exists. Would you like to overwrite?"):
                    self.datafile[name.get()] = {"id":id.get(),"kr":kr.get()}
                    tkinter.messagebox.showinfo("","Key "+name.get()+" added with value "+id.get()+" "+kr.get())
                    tlvl.destroy()
            else:
                self.datafile[name.get()] = {"id":id.get(),"kr":kr.get()}
                tkinter.messagebox.showinfo("","Key "+name.get()+" added with value "+id.get()+" "+kr.get())
                tlvl.destroy()
            self.populate()
    def remakedata(self):
        if tkinter.messagebox.askyesno("","Are you sure?"):
            self.datafile.close()

            championfilecreator.recreate_dynamic()
            self.datafile = shelve.open("champions")

            tkinter.messagebox.showinfo("","Recreated database")
            self.populate()

    def populate(self):
        self.lbox.delete(0,tkinter.END)
        for items in sorted(self.datafile):
            self.lbox.insert(tkinter.END,items)
    def populate_id(self):
        pass

    def callback(self,event):
            widget = event.widget
            selection=widget.curselection()
            value = widget.get(selection[0])
            self.selected_id.set(self.datafile[value]["id"])
            self.selected_kr.set(self.datafile[value]["kr"])

    def modify(self):
        if tkinter.messagebox.askyesno("","Are you sure?"):
            try:
                selected = self.lbox.curselection()
                info = self.lbox.get(selected[0])
            except IndexError: tkinter.messagebox.showerror("","Please select an item from the left")
            else:

                self.datafile[info] = {"id":self.selected_id.get(),"kr":self.selected_kr.get()}
                tkinter.messagebox.showinfo("","Edited Key "+info+" to value "+self.selected_id.get()+" "+self.selected_kr.get())
                self.lbox.delete(0,tkinter.END)
                self.populate()
if __name__ == "__main__":
    ChampionListEditor(None)