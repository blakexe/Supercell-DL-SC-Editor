from json import tool
import pathlib
from tkinter import filedialog
from tkinter.ttk import Progressbar, Treeview
from sc_objects.sc import SC
import os
from tkinter import *
from tkinter.messagebox import showinfo
from tkinter.messagebox import showerror
from sc_compression.compressor import Compressor
from sc_compression.decompressor import Decompressor
from PIL import ImageTk, Image

dir_path = os.path.dirname(os.path.realpath(__file__))

curr_sc = SC()

last_dir = dir_path
last_file = ""

show_polygons = True

#Create structure
root = Tk()
toolbar = Menu(root)

#Tree
tree_browser = Treeview(root, columns=('objects'), show="tree headings")
tree_browser.heading('objects', text='Objects')
tree_browser.grid(row=0, column=0, sticky='nsew')
scrollbar = Scrollbar(root, orient=VERTICAL, command=tree_browser.yview)
tree_browser.configure(yscroll=scrollbar.set)
scrollbar.grid(row=0, column=1, sticky='ns')
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=0)

#Progress popup
popup = Toplevel()
popup.geometry("175x100")
Label(popup, text="Hold on...").grid(row=0,column=0)
progress_bar = Progressbar(popup, orient='horizontal', mode='indeterminate')
progress_bar.grid(row=1, column=0,sticky="NSEW")
progress_bar.start()
popup.pack_slaves()
popup.withdraw()
popup.protocol("WM_DELETE_WINDOW", None)

#Preview on the right
canvas = Canvas(root, width = 500, height = 500)
canvas.grid(row=0, column=1, sticky="nsew")
image_container = canvas.create_image(20, 20, anchor=NW, image=ImageTk.PhotoImage(Image.new("RGBA", (20, 20)))) 

#Credits on bottom
T = Text(root, height = 5, width = 52)
T.insert(END, "Editor made by Blaki.") 
T.grid(row=1, column=0, sticky="nsew")

#Make toolbar sections
file_cascade = Menu(toolbar)
toolbar.add_cascade(label='File', menu=file_cascade)

tools_cascade = Menu(toolbar)
toolbar.add_cascade(label='Tools', menu=tools_cascade)

showstuff_cascade = Menu(toolbar)
toolbar.add_cascade(label='Show', menu=showstuff_cascade)

def show_chunk_polygon():
    global show_polygons

    show_polygons = True
    showstuff_cascade.entryconfig("Show Chunk Polygon", state="disabled")
    showstuff_cascade.entryconfig("Hide Chunk Polygon", state="normal")
    clicked_renderable(None)

def hide_chunk_polygon():
    global show_polygons

    show_polygons = False
    showstuff_cascade.entryconfig("Show Chunk Polygon", state="normal")
    showstuff_cascade.entryconfig("Hide Chunk Polygon", state="disabled")
    clicked_renderable(None)

def export_chunk():
    try:
        path = filedialog.asksaveasfile(mode="w", defaultextension=".png", initialdir=last_dir)
    except AssertionError:
        showerror(title="Error", message="Please pick a directory, not a file.")

    if path is None:
        return

    item = tree_browser.item(tree_browser.focus())
    values = item['values']

    chunk_index = values[0]
    shape_index = values[1]
    chunk = curr_sc.shapes[shape_index].chunks[chunk_index]

    image = chunk.render()

    image.save(path.name, "PNG")

def replace_chunk():
    global last_dir

    item = tree_browser.item(tree_browser.focus())
    values = item['values']

    path = filedialog.askopenfilename(title="Select an image", initialdir=last_dir, filetypes=[('image', '*.*')])

    if path == "":
        return
    last_dir = os.path.dirname(path)

    image = Image.open(path)

    chunk_index = values[0]
    shape_index = values[1]
    chunk = curr_sc.shapes[shape_index].chunks[chunk_index]

    chunk.replace(image)

    clicked_renderable(None)

def clicked_renderable(event):
    global canvas

    item = tree_browser.item(tree_browser.focus())
    tags = item['tags']
    values = item['values']

    tools_cascade.entryconfig("Replace Chunk Image", state="disabled")
    tools_cascade.entryconfig("Export Chunk Image", state="disabled")

    if "shape" in tags:
        sc_object = curr_sc.shapes[values[0]]
    elif "shape_chunk" in tags:
        tools_cascade.entryconfig("Replace Chunk Image", state="normal")
        tools_cascade.entryconfig("Export Chunk Image", state="normal")
        chunk_index = values[0]
        shape_index = values[1]
        sc_object = curr_sc.shapes[shape_index].chunks[chunk_index]
        # print(f"\n\n{sc_object.xy_points}\n\n")
    elif "texture" in tags:
        sc_object = curr_sc.textures[values[0]]
    else:
        return
    
    render = sc_object.render()

    if show_polygons and "shape_chunk" in tags:
        render = Image.alpha_composite(render, sc_object.render_polygon())

    tk_image = ImageTk.PhotoImage(render)

    canvas.itemconfig(image_container, image = tk_image)
    canvas.imgref = tk_image

def populate_tree():
    #Clear all elements
    tree_browser.delete(*tree_browser.get_children())

    #Make parent item for movieclips
    movieclip_parent_node_id = tree_browser.insert(parent="", index=END, text="Movieclips")

    for movieclip in curr_sc.movieclips:
        #Add export node to tree
        try:
            movieclip_name = curr_sc.movie_clip_info[movieclip.clip_id]
        except:
            try:
                movieclip_name = curr_sc.movie_clip_info[movieclip.clip_id + 1]
            except:
                movieclip_name = "Unknown movieclip name"
                print(f"Movieclip does not have name pair with id: {movieclip.clip_id}")

        movieclip_node_id = tree_browser.insert(parent=movieclip_parent_node_id, index=END, text=movieclip_name)

        for index, shape in enumerate(movieclip.shapes):
            shape_index = curr_sc.shapes.index(shape)
            #Add shape node to tree
            shape_node_id = tree_browser.insert(parent=movieclip_node_id, index=END, text=f"Shape {index}", values=(shape_index), tags=("renderable", "shape"))

            #Add shape chunks to tree
            for chunk_index, chunk in enumerate(shape.chunks):
                tree_browser.insert(parent=shape_node_id, index=END, text=f"Chunk {chunk.chunk_id}", values=(chunk_index, shape_index), tags=("renderable", "shape_chunk"))

    # #Make parent item for shapes
    # shapes_parent_node_id = tree_browser.insert(parent="", index=END, text="Shapes")

    # #Add shapes
    # for index, shape in enumerate(curr_sc.shapes):
    #     #Add shape node to tree
    #     shape_node_id = tree_browser.insert(parent=shapes_parent_node_id, index=END, text=f"Shape {index}", values=(index), tags=("renderable", "shape"))

    #     #Add shape chunks to tree
    #     for chunk_index, chunk in enumerate(shape.chunks):
    #         tree_browser.insert(parent=shape_node_id, index=END, text=f"Chunk {chunk.chunk_id}", values=(chunk_index, index), tags=("renderable", "shape_chunk"))

    #Make parent item for textures
    texture_parent_node_id = tree_browser.insert(parent="", index=END, text="Textures")

    for index, texture in enumerate(curr_sc.textures):
        tree_browser.insert(parent=texture_parent_node_id, index=END, text=f"Texture {index}", values=[index], tags=("renderable", "texture"))

    tree_browser.tag_bind(tagname="renderable", sequence="<<TreeviewSelect>>", callback=clicked_renderable)

def save_sc():
    if last_file == "":
        return

    exported = curr_sc.export_sc()

    compressor = Compressor()

    compressed = compressor.compress(exported, 2)

    with open(last_file, "wb") as f:
        f.write(compressed)

    showinfo(title="Successfully saved", message=f"Saved SC at {last_file}")

def save_sc_as():
    global last_file

    try:
        path = filedialog.asksaveasfile(mode="w", defaultextension=".sc", initialdir=last_dir)
    except AssertionError:
        showerror(title="Error", message="Something went wrong")

    if path is None:
        return

    path = path.name

    last_file = path

    save_sc()


def open_sc():
    global last_dir
    global curr_sc
    global last_file

    print(last_dir)

    path = filedialog.askopenfilename(title="Select _dl.sc file", initialdir=last_dir, filetypes=[('sc files', '*.sc')])

    if path == "":
        return
    last_dir = os.path.dirname(path)
    last_file = path

    # popup.deiconify()
    # popup.grab_set_global()
    # popup.wait_visibility()

    # try:
    #Open
    with open(path, "rb") as f:
        data = f.read()

    #Decompress
    decompressor = Decompressor()
    decompressed = decompressor.decompress(data)

    print(decompressed[:20])

    curr_sc = SC()

    curr_sc.import_sc(decompressed)

    populate_tree()

    # popup.withdraw()

    # except Exception as e:
    #     showerror("Error has occured:", str(e))

def start():
    #'File' options
    file_cascade.add_command(label='Open', command=open_sc)
    file_cascade.add_command(label='Save', command=save_sc)
    file_cascade.add_command(label='Save as...', command=save_sc_as)

    #'Tools' options
    tools_cascade.add_command(label='Replace Chunk Image', command=replace_chunk)
    tools_cascade.add_command(label='Export Chunk Image', command=export_chunk)
    tools_cascade.entryconfig("Replace Chunk Image", state="disabled")
    tools_cascade.entryconfig("Export Chunk Image", state="disabled")

    #'Show' options
    showstuff_cascade.add_command(label='Show Chunk Polygon', command=show_chunk_polygon)
    showstuff_cascade.add_command(label='Hide Chunk Polygon', command=hide_chunk_polygon)
    showstuff_cascade.entryconfig("Show Chunk Polygon", state="disabled")

    #Setup
    root.title("Magic Emote Editor")
    root.geometry('720x512')

    root.config(menu=toolbar)

    #Start application
    root.mainloop()

if __name__ == "__main__":
    start()