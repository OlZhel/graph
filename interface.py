import pickle
from tkinter import *
from tkinter.messagebox import *
from math    import *
from lxml    import etree

tree  = etree.parse(open('map.osm', 'rb'))

graph_f = open('./result/graph.pickle', 'rb')
(graph_points, graph_adj) = pickle.load(graph_f)
graph_f.close()

#Целевые точки
target_list = list()

def pg_to_p(p_graph):
    return (p_graph['lon'],p_graph['lat'])

def euclid_dist(p1,p2):
    (x1, y1) = p1
    (x2, y2) = p2
    return sqrt((x1-x2)**2+(y1-y2)**2)

def nearest(points_g, p1, dist=euclid_dist):
    min_d = inf
    p_min = None
    for pg in points_g:
        p2 = pg_to_p(pg)
        d = dist(p2,p1)
        if d < min_d:
            min_d = d
            p_min = pg
    return p_min

def get_objects_by_type(type_str):
    objects_xml = tree.xpath(f"/osm/node[./tag[./@v=\"{type_str}\"]]")
    objects = list()
    for obj_xml in objects_xml:
        name = obj_xml.xpath("./tag[./@k=\"name\"]/@v")
        if not name:
            name = "NONAME"
        else:
            name = name[0]
        obj = { 'name': name,
                'lon': float(obj_xml.attrib['lon']),
                'lat': float(obj_xml.attrib['lat'])
        }
        objects.append(obj)
    return objects

#------------------------------------------------#
#------------------INTERFACE---------------------#
#------------------------------------------------#
def create_win_obj(event):
    try:
        obj_str = type_list.selection_get()
    except Exception:
        print("<Error> Не указан тип объектов!")
        showinfo("Error", "Сначала выберите тип объектов!")
        return
    print("<Log> Открыто окно выбора объектов")
    objects = get_objects_by_type(obj_str)
    win = Toplevel(root)
    win.title("Выбор объектов")
    win.grab_set()
    obj_list = Listbox(win,selectmode=MULTIPLE,height=20, width=70)
    i = 0
    for obj in objects:
        obj_list.insert(END, f"{i}|<{obj['lon']},{obj['lat']}> — {obj['name']}")
        i+=1
    ok_but = Button(win,
                    text="Подтвердить выбор", #надпись на кнопке
                    width=50,height=1, #ширина и высота
                    bg="white") #цвет фона и надписи
    obj_list.pack()
    ok_but.pack()
    win.resizable(width=False, height=False)
    def ok_func(event):
        try:
            sel = obj_list.selection_get()
            if "|" not in sel: raise Exception()
        except Exception:
            print("<Error> Не выбраны объекты!")
            showinfo("Error", "Сначала выберите объекты!")
            return
        strings = sel.split("\n")
        target_list.clear()
        for s in strings:
            (ind, tail) = s.split("|")
            ind = int(ind)
            target_list.append(objects[ind])
        print("<Info>")
        print(sel)
        print("</Info>")
        win.grab_release()
        win.destroy()
        print("<Log> Окно выбора объектов закрыто!")
    ok_but.bind("<Button-1>", ok_func)

def create_csv_svg(event):
    print("<Log> Начало генерации CSV и SVG!")
    try:
        p1 = (lon,lat) = (float(lon_ent.get()),float(lat_ent.get()))
        print(f"<Log> Получены координаты от пользователя <{lon},{lat}>")
    except Exception:
        print("<Error> Ошибка формата чисел!")
        showinfo("Error", "Введите верные координаты!")
        return
    if not target_list:
        print("<Error> Не указаны объекты!")
        showinfo("Error", "Сначала укажите объекты!")
        return
    p_graph = nearest(graph_points, p1)
    print(f"<Log> Ближайшая точка на графе <{p_graph['lon']},{p_graph['lat']}>, id={p_graph['osm_id']}")



root = Tk()
root.title("G")
root.resizable(width=False, height=False)
root.minsize(width=200,height=250) 

lab = Label(root, text="Выберите тип объектов:", font="Arial 10")
types = ['hospital', 'restaurant', 'marketplace']
type_list = Listbox(root,selectmode=SINGLE,height=len(types), width=21)
for t in types:
    type_list.insert(END, t)

object_but = Button(root,
                    text="Выбрать объекты", #надпись на кнопке
                    width=17,height=1, #ширина и высота
                    bg="white") #цвет фона и надписи
object_but.bind("<Button-1>", create_win_obj)

lab_crd = Label(root, text="Введите координаты:", font="Arial 10")
lon_ent = Entry(root, width=20)
lat_ent = Entry(root, width=20)

csv_but = Button(root,
                    text="Создать CSV и SVG", #надпись на кнопке
                    width=17,height=1, #ширина и высота
                    bg="white") #цвет фона и надписи
csv_but.bind("<Button-1>", create_csv_svg)

test_but = Button(root,
                    text="Тест алгоритмов", #надпись на кнопке
                    width=17,height=1, #ширина и высота
                    bg="white") #цвет фона и надписи

lab.pack()
type_list.pack()
object_but.pack()
lab_crd.pack()
lon_ent.pack()
lat_ent.pack()
csv_but.pack()
test_but.pack()

root.mainloop()