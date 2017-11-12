from tkinter import *
import tkinter
from PIL import Image    # pip install pillow
from PIL import ImageTk  # pip install pillow


class Gui:
    configuration = {}
    area_in_px = 800
    tkinter_root = None

    one_unit_in_px = 0
    agent_images = []
    images = {}

    def __init__(self, configuration):
        self.configuration = configuration

        window_width = 5 + self.area_in_px + 5
        window_height = 5 + 60 + 5 + self.area_in_px + 5 + 100 + 5

        self.tkinter_root = tkinter.Tk()
        self.tkinter_root.geometry(str(window_width) + "x" + str(window_height) + "+10+10")

        self.tkinter_root.button_save = tkinter.Button(self.tkinter_root, text="Save", fg="black")
        self.tkinter_root.button_save.pack()
        self.tkinter_root.button_save.place(x=5, y=5, width=60, height=30)

        self.tkinter_root.button_load = tkinter.Button(self.tkinter_root, text="Load", fg="black")
        self.tkinter_root.button_load.pack()
        self.tkinter_root.button_load.place(x=70, y=5, width=60, height=30)

        self.tkinter_root.speed_slider = Scale(self.tkinter_root, from_=0, to=800, orient=HORIZONTAL)
        self.tkinter_root.speed_slider.pack()
        self.tkinter_root.speed_slider.place(x=(window_width - 405), y=5, width=400, height=65)

        label_y = 5 + 60 + 5 + self.area_in_px + 5
        label_width = (window_width / 2 - 10)

        self.tkinter_root.agent_information_text = StringVar()
        self.tkinter_root.agent_information_text.set("")
        agent_information = Label(self.tkinter_root, anchor=NW, justify=LEFT,
                                  textvariable=self.tkinter_root.agent_information_text)
        agent_information.pack()

        agent_information.place(x=(window_width / 2 + 5), y=label_y, width=label_width, height=100)

        self.tkinter_root.general_information_text = StringVar()
        self.tkinter_root.general_information_text.set("")
        general_information = Label(self.tkinter_root, anchor=NW, justify=LEFT,
                                    textvariable=self.tkinter_root.general_information_text)
        general_information.pack()

        general_information.place(x=5, y=label_y, width=label_width, height=100)

        self.prepare_canvas()

    def draw_frame(self, agents, food_positions, tick_count):
        self.tkinter_root.canvas.delete("all")
        for agent in agents:
            self.draw_agent(agent)
            if agent.highlighted:
                self.tkinter_root.agent_information_text.set(agent.get_information_string(tick_count, [],
                                                                                          agent.output))

        for position in food_positions:
            self.draw_food(position)

        string = "Tick: " + str(tick_count) + "\n"
        string += "Agents: " + str(len(agents)) + " / " + str(self.configuration["Agent_MinPopulation"])
        self.tkinter_root.general_information_text.set(string)

    def draw_agent(self, agent):
        image_index = round(agent.direction * 60)
        if image_index == 60:
            image_index = 0
        image = self.agent_images[image_index]

        center_x = agent.position[0] * self.one_unit_in_px
        center_y = self.area_in_px - agent.position[1] * self.one_unit_in_px

        self.tkinter_root.canvas.create_image(center_x, center_y, anchor=CENTER, image=image)

        if agent.highlighted:
            self.tkinter_root.canvas.create_image(center_x, center_y, anchor=CENTER, image=self.images["Highlight"])

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

    # def click_on_canvas(self, event):
    #     global highlighted_agent
    #
    #     position = [event.x, area_in_px - event.y]
    #     for i in [0, 1]:
    #         position[i] = position[i] / one_unit_in_px
    #
    #     closest_distance = 9999999999
    #     closest_agent = None
    #
    #     for agent in agents:
    #         distance = agent.get_distance(position)
    #         if distance < closest_distance:
    #             closest_distance = distance
    #             closest_agent = agent
    #
    #     highlighted_agent = closest_agent

    # def toggle_pause(self, event=None):
    #     global speed
    #     global speed_before_pause
    #
    #     if speed != 0:
    #         speed_before_pause = speed
    #         speed = event.type  # suppress error (unused value)
    #         speed = 0
    #     else:
    #         speed = speed_before_pause
    #
    #     speed_slider.set(speed)

    # def set_speed(value):
    #     global speed
    #     speed = int(value)

    # def save(event):
    #     print("Saving...")
    #     agents_data = []
    #     for agent in agents:
    #         agent_data = {
    #             "position": agent.position,
    #             "direction": agent.direction,
    #             "health": agent.health,
    #         }
    #         agents_data.append(agent_data)
    #
    #     data = {
    #         "agent_data": agents_data,
    #         "configuration": configuration,
    #         "food_positions": food_positions,
    #     }
    #     print(data)
    #     saveload.save(data)
    #
    # def load(event):
    #     print("Loading...")

    def click_on_canvas(self, event, agents):
        position = [event.x, self.area_in_px - event.y]
        for i in [0, 1]:
            position[i] = position[i] / self.one_unit_in_px

        closest_distance = 9999999999
        closest_agent = None

        for agent in agents:
            agent.highlighted = False

            distance = agent.get_distance(position)
            if distance < closest_distance:
                closest_distance = distance
                closest_agent = agent

        closest_agent.highlighted = True
