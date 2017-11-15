from gui import Gui
from manager import Manager
import saveload

configuration = {
    "Area": 50,
    "Agent_Health": 100,
    "Agent_MaxMovementSpeed": 0.1,
    "Agent_MaxTurningSpeed": 0.02,
    "Agent_NaturalDecay": 0.1,
    "Agent_MinPopulation": 8,
    "Agent_Reproduce_At": 250,
    "Agent_Reproduce_Cost": 100,
    "Food_Value": 50,
    "Food_Diameter": 0.5,
    "Food_PerTick": 0.035,
    "Sensor_Food_Range": 8,
    "Sensor_Food_Middle_Angel": 30,
    "Sensor_Food_Side_Angel": 30,
    "Neural_Network_Nodes_In_Layers": [3, 3, 2],
    "Neural_Network_Mutate": 0.1,
}


gui = None
manager = None


def test_position(event):
    pass
    # agents[0].highlighted = True
    # food_position = [event.x, gui.area_in_px - event.y]
    # for i in [0, 1]:
    #     food_position[i] = food_position[i] / gui.one_unit_in_px
    #
    # distance = agents[0].get_distance(food_position)
    #
    # print(calculate_sensors(agents[0], food_position, distance, [0, 0, 0]))


def start():
    global gui
    global manager

    print("########Start########")

    gui = Gui(configuration)
    manager = Manager(configuration, gui)

    gui.tkinter_root.protocol('WM_DELETE_WINDOW', quit_window)

    gui.tkinter_root.button_save.bind("<Button-1>", save)
    gui.tkinter_root.button_load.bind("<Button-1>", load)
    gui.tkinter_root.button_jump.bind("<Button-1>", jump)
    gui.tkinter_root.bind("y", jump)
    gui.tkinter_root.speed_slider.bind("<B1-Motion>", set_speed)
    gui.tkinter_root.speed_slider.bind("<Button-1>", set_speed)
    gui.tkinter_root.speed_slider.bind("<ButtonRelease-1>", set_speed)

    # gui.tkinter_root.canvas.bind("<Button-1>", click_on_canvas)
    gui.tkinter_root.canvas.bind("<Button-1>", lambda event: gui.click_on_canvas(event, manager.agents))
    gui.tkinter_root.bind("<space>", toggle_pause)
    gui.tkinter_root.tree_view.bind("<<TreeviewSelect>>", lambda event: gui.select_table(manager.agents))

    # gui.tkinter_root.canvas.bind("<Button-1>", test_position)

    gui.tkinter_root.mainloop()


# noinspection PyUnusedLocal
def toggle_pause(event):
    if manager.speed != 0:
        speed_before_pause = manager.speed
        speed = 0
        gui.draw_frame(manager.agents, manager.food_positions, manager.tick_count)
        gui.update_table(manager.agents, manager.tick_count)
    else:
        speed = manager.speed_before_pause

    gui.tkinter_root.speed_slider.set(speed)


# noinspection PyUnusedLocal
def set_speed(event):
    global gui

    manager.speed = int(gui.tkinter_root.speed_slider.get())


# noinspection PyUnusedLocal
def save(event):
    saveload.save(manager)


# noinspection PyUnusedLocal
def load(event):
    saveload.load(manager)


# noinspection PyUnusedLocal
def jump(event):
    manager.tick()


def quit_window():
    manager.exit_tasks = True
    gui.tkinter_root.destroy()


start()
