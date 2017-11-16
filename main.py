from gui import Gui
from manager import Manager


configuration = {
    "Area": 50,
    "Agent_Health": 100,
    "Agent_Movement_MaxSpeed": 0.1,
    "Agent_Movement_Cost": 0.1,
    "Agent_Turning_MaxSpeed": 0.02,
    "Agent_Attack_Range": 6,
    "Agent_Attack_Angle": 50,
    "Agent_Attack_Damage": 15,
    "Agent_Attack_Cost": 15,
    "Agent_Attack_Gain": 210,
    "Agent_NaturalDecay": 0.1,
    "Agent_MinPopulation": 8,
    "Agent_Reproduce_At": 250,
    "Agent_Reproduce_Cost": 100,
    "Food_Value": 50,
    "Food_Diameter": 0.5,
    "Food_PerTick": 0.03,
    "Sensor_Food_Range": 8,
    "Sensor_Food_Middle_Angel": 30,
    "Sensor_Food_Side_Angel": 35,
    "Sensor_Agent_Range": 12,
    "Sensor_Agent_Middle_Angel": 30,
    "Sensor_Agent_Side_Angel": 30,
    "Neural_Network_Nodes_In_Layers": [7, 5, 3],
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


def main():
    global gui
    global manager

    print("########Start########")

    gui = Gui(configuration)
    manager = Manager(configuration, gui)
    gui.bind_buttons(manager)

    # gui.tkinter_root.canvas.bind("<Button-1>", test_position)

    gui.tkinter_root.mainloop()


if __name__ == "__main__":
    main()
