import saveload

from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog
import tkinter
import os
from PIL import Image                # pip install pillow
from PIL import ImageTk              # pip install pillow


class Gui:
    manager = None

    configuration = {}
    area_in_px = 800
    tkinter_root = None

    one_unit_in_px = 0
    agent_images = []
    images = {}
    speed_before_pause = 20

    frame_information = None
    highlighted_agent_id = None

    def __init__(self, configuration):
        self.configuration = configuration

        window_width = 5 + self.area_in_px + 5 + 500 + 5
        window_height = 5 + 60 + 5 + self.area_in_px + 5 + 100 + 5

        self.tkinter_root = tkinter.Tk()
        self.tkinter_root.geometry(str(window_width) + "x" + str(window_height) + "+10+10")

        self.tkinter_root.button_save = tkinter.Button(self.tkinter_root, text="Save", fg="black")
        self.tkinter_root.button_save.pack()
        self.tkinter_root.button_save.place(x=5, y=5, width=60, height=30)

        self.tkinter_root.button_load = tkinter.Button(self.tkinter_root, text="Load", fg="black")
        self.tkinter_root.button_load.pack()
        self.tkinter_root.button_load.place(x=70, y=5, width=60, height=30)

        self.tkinter_root.button_jump = tkinter.Button(self.tkinter_root, text="Jump 1 tick [y]", fg="black")
        self.tkinter_root.button_jump.pack()
        self.tkinter_root.button_jump.place(x=140, y=5, width=100, height=30)

        self.tkinter_root.speed_slider = Scale(self.tkinter_root, from_=0, to=500, orient=HORIZONTAL)
        self.tkinter_root.speed_slider.pack()
        self.tkinter_root.speed_slider.place(x=(5+self.area_in_px - 405), y=5, width=400, height=65)

        label_y = 5 + 60 + 5 + self.area_in_px + 5
        label_width = (self.area_in_px / 2 - 10)

        self.tkinter_root.agent_information_text = StringVar()
        self.tkinter_root.agent_information_text.set("")
        agent_information = Label(self.tkinter_root, anchor=NW, justify=LEFT,
                                  textvariable=self.tkinter_root.agent_information_text)
        agent_information.pack()

        agent_information.place(x=(self.area_in_px / 2 + 5), y=label_y, width=label_width, height=100)

        self.tkinter_root.general_information_text = StringVar()
        self.tkinter_root.general_information_text.set("")
        general_information = Label(self.tkinter_root, anchor=NW, justify=LEFT,
                                    textvariable=self.tkinter_root.general_information_text)
        general_information.pack()

        general_information.place(x=5, y=label_y, width=label_width, height=100)

        self.prepare_canvas()
        self.create_table()

    def bind_buttons(self):
        self.tkinter_root.protocol('WM_DELETE_WINDOW', self.quit_window)

        self.tkinter_root.button_save.bind("<Button-1>", self.save)
        self.tkinter_root.button_load.bind("<Button-1>", self.load)
        self.tkinter_root.button_jump.bind("<Button-1>", self.jump)
        self.tkinter_root.bind("y", self.jump)
        self.tkinter_root.speed_slider.bind("<B1-Motion>", self.set_speed)
        self.tkinter_root.speed_slider.bind("<Button-1>", self.set_speed)
        self.tkinter_root.speed_slider.bind("<ButtonRelease-1>", self.set_speed)

        self.tkinter_root.canvas.bind("<Button-1>", self.click_on_canvas)
        self.tkinter_root.bind("<space>", self.toggle_pause)
        self.tkinter_root.tree_view.bind("<<TreeviewSelect>>", self.select_table)

    def draw_frame(self):
        self.tkinter_root.canvas.delete("all")
        for agent in self.frame_information.agents:
            self.draw_agent(agent)
            if agent.id == self.highlighted_agent_id:
                self.tkinter_root.agent_information_text.set(
                    agent.get_information_string(self.frame_information.tick_count))

        for position in self.frame_information.food_positions:
            self.draw_food(position)

        string = "Tick: " + str(self.frame_information.tick_count) + "\n"
        string += "Agents: " + str(len(self.frame_information.agents)) \
                  + " / " + str(self.configuration["Agent_MinPopulation"])
        self.tkinter_root.general_information_text.set(string)

        self.update_table()

    def draw_agent(self, agent):
        image_index = round(agent.direction * 60)
        image_index %= 60
        image = self.agent_images[image_index]

        center_position = [agent.position[0] * self.one_unit_in_px,
                           self.area_in_px - agent.position[1] * self.one_unit_in_px]

        self.tkinter_root.canvas.create_image(center_position[0], center_position[1], anchor=CENTER, image=image)

        if agent.id == self.highlighted_agent_id:
            self.tkinter_root.canvas.create_image(center_position[0], center_position[1], anchor=CENTER,
                                                  image=self.images["Highlight"])

            angle = 360 * agent.direction
            angle = -angle + 90

            self.draw_agent_arcs(center_position, angle)

        if agent.marked:
            self.tkinter_root.canvas.create_image(center_position[0], center_position[1], anchor=CENTER,
                                                  image=self.images["Marker"])

    def draw_agent_arcs(self, center_position, angle):
        colors = {"Food": "#ffde00",
                  "Agent": "#4eff00",
                  "Attack": "#a80000"}

        for sensor_type in ["Food", "Agent"]:
            sensor_middle_angle = self.configuration["Sensor_"+sensor_type+"_Middle_Angel"]
            sensor_side_angle = self.configuration["Sensor_"+sensor_type+"_Side_Angel"]
            sensor_range = self.configuration["Sensor_"+sensor_type+"_Range"] * self.one_unit_in_px
            color = colors[sensor_type]

            x1 = center_position[0] - sensor_range
            x2 = center_position[0] + sensor_range
            y1 = center_position[1] - sensor_range
            y2 = center_position[1] + sensor_range

            self.tkinter_root.canvas.create_arc(x1, y1, x2, y2, outline=color,
                                                start=angle + sensor_middle_angle / 2 + sensor_side_angle,
                                                extent=-sensor_side_angle)

            self.tkinter_root.canvas.create_arc(x1, y1, x2, y2, outline=color,
                                                start=angle - sensor_middle_angle / 2,
                                                extent=sensor_middle_angle)

            self.tkinter_root.canvas.create_arc(x1, y1, x2, y2, outline=color,
                                                start=angle - sensor_middle_angle / 2 - sensor_side_angle,
                                                extent=sensor_side_angle)

            self.tkinter_root.canvas.create_arc(x1, y1, x2, y2, outline=color,
                                                start=angle + sensor_middle_angle / 2 + sensor_side_angle,
                                                extent=(360 - 2*sensor_side_angle - sensor_middle_angle))

        attack_angle = self.configuration["Agent_Attack_Angle"]
        attack_range = self.configuration["Agent_Attack_Range"] * self.one_unit_in_px
        color = colors["Attack"]

        x1 = center_position[0] - attack_range
        x2 = center_position[0] + attack_range
        y1 = center_position[1] - attack_range
        y2 = center_position[1] + attack_range

        self.tkinter_root.canvas.create_arc(x1, y1, x2, y2, outline=color,
                                            start=angle - attack_angle / 2,
                                            extent=attack_angle)

    def draw_food(self, position):
        self.tkinter_root.canvas.create_image(position[0] * self.one_unit_in_px,
                                              self.area_in_px - position[1] * self.one_unit_in_px,
                                              anchor=CENTER, image=self.images["Food"])

    def prepare_canvas(self):

        self.one_unit_in_px = self.area_in_px / self.configuration["Area"]
        self.one_unit_in_px = round(self.one_unit_in_px)

        self.tkinter_root.canvas = Canvas(self.tkinter_root, width=1, height=1, bg="#eeeeee")
        self.tkinter_root.canvas.configure(highlightthickness=0, borderwidth=0)
        self.tkinter_root.canvas.place(x=5, y=70, width=self.area_in_px, height=self.area_in_px)

        agent_image = Image.open("graphics/Agent.png")
        for i in range(0, 60):
            image = agent_image
            image = image.rotate(-(i / 60) * 360)
            image = image.resize((self.one_unit_in_px, self.one_unit_in_px), Image.ANTIALIAS)
            image = ImageTk.PhotoImage(image)

            self.agent_images.append(image)

        image = Image.open("graphics/Food.png")
        size = round(self.one_unit_in_px * self.configuration["Food_Diameter"])
        image = image.resize((size, size), Image.ANTIALIAS)
        self.images["Food"] = ImageTk.PhotoImage(image)

        image = Image.open("graphics/Highlight.png")
        size = round(self.one_unit_in_px * 0.5)
        image = image.resize((size, size), Image.ANTIALIAS)
        self.images["Highlight"] = ImageTk.PhotoImage(image)

        image = Image.open("graphics/Marker.png")
        size = round(self.one_unit_in_px * 1)
        image = image.resize((size, size), Image.ANTIALIAS)
        self.images["Marker"] = ImageTk.PhotoImage(image)

    def click_on_canvas(self, event):
        position = [event.x, self.area_in_px - event.y]
        for i in [0, 1]:
            position[i] = position[i] / self.one_unit_in_px

        closest_distance = 9999999999
        closest_agent = None

        for agent in self.frame_information.agents:
            distance = agent.get_distance(position, self.configuration["Area"])
            if distance < closest_distance:
                closest_distance = distance
                closest_agent = agent

        self.highlighted_agent_id = closest_agent.id

    def create_table(self):
        self.tkinter_root.tree_view = Treeview(self.tkinter_root)

        self.tkinter_root.tree_view['columns'] = ('generation', 'age', 'health')
        self.tkinter_root.tree_view.heading("#0", text='', anchor='w')
        self.tkinter_root.tree_view.column("#0", anchor="w", width=1)
        self.tkinter_root.tree_view.heading('generation', text='generation')
        self.tkinter_root.tree_view.column('generation', anchor='center', width=100)
        self.tkinter_root.tree_view.heading('age', text='age')
        self.tkinter_root.tree_view.column('age', anchor='center', width=100)
        self.tkinter_root.tree_view.heading('health', text='health')
        self.tkinter_root.tree_view.column('health', anchor='center', width=100)

        self.tkinter_root.tree_view.pack()
        self.tkinter_root.tree_view.place(x=810, y=70, width=500, height=self.area_in_px)

    # noinspection PyUnusedLocal
    def select_table(self, event):
        item = self.tkinter_root.tree_view.item(self.tkinter_root.tree_view.focus())
        i = int(item["text"])

        self.highlighted_agent_id = self.frame_information.agents[i].id

    def update_table(self):
        self.tkinter_root.tree_view.delete(*self.tkinter_root.tree_view.get_children())

        i = 0
        # highlighted = None
        for agent in self.frame_information.agents:
            generation = agent.generation
            age = round(self.frame_information.tick_count - agent.birth, 2)
            health = round(agent.health, 2)

            self.tkinter_root.tree_view.insert('', 'end', text=i, values=(generation, age, health), tag=i)

            # if agent.highlighted:
            #   highlighted = i

            i += 1

        # if highlighted is not None:
        #   self.tkinter_root.tree_view.selection_set(self.tkinter_root.tree_view.tag_has(highlighted)[0])

    def open_file_dialog(self):
        self.manager.speed = 0
        path = os.getcwd() + "\saves"
        print(path)
        file_name = filedialog.askopenfilename(initialdir=path, title="Select file",
                                               filetypes=(("EvoSim saves", "*.EvoSim"), ("all files", "*.*")))
        return file_name

    # noinspection PyUnusedLocal
    def toggle_pause(self, event):
        if self.manager.speed != 0:
            self.speed_before_pause = self.manager.speed
            self.manager.speed = 0
            self.draw_frame()
            self.update_table()
        else:
            self.manager.speed = self.speed_before_pause

        self.tkinter_root.speed_slider.set(self.manager.speed)

    # noinspection PyUnusedLocal
    def set_speed(self, event):
        self.manager.speed = int(self.tkinter_root.speed_slider.get())

    # noinspection PyUnusedLocal
    def save(self, event):
        saveload.save(self.manager)

    # noinspection PyUnusedLocal
    def load(self, event):
        saveload.load(self.manager)

    # noinspection PyUnusedLocal
    def jump(self, event):
        self.manager.tick()

    def quit_window(self):
        self.manager.exit_tasks = True
        self.tkinter_root.destroy()
