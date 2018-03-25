from manager import Manager
from threads import GuiThread


configuration = {
    "Area": 80,
    "Agent_Health": 100,
    "Agent_Movement_MaxSpeed": 0.1,
    "Agent_Movement_Cost": 0.1,
    "Agent_Turning_MaxSpeed": 0.02,
    "Agent_Attack_Range": 6,
    "Agent_Attack_Angle": 50,
    "Agent_Attack_Damage": 30,
    "Agent_Attack_Cost": 15,
    "Agent_Attack_Gain": 210,
    "Agent_NaturalDecay": 0.05,
    "Agent_MinPopulation": 4,
    "Agent_Reproduce_At": 400,
    "Agent_Reproduce_Cost": 110,
    "Food_Value": 50,
    "Food_Diameter": 0.5,
    "Food_PerTick": 0.03,
    "Sensor_Food_Range": 12,
    "Sensor_Food_Middle_Angel": 30,
    "Sensor_Food_Side_Angel": 35,
    "Sensor_Agent_Range": 12,
    "Sensor_Agent_Middle_Angel": 30,
    "Sensor_Agent_Side_Angel": 30,
    "Neural_Network_Nodes_In_Layers": [9, 9, 3],
    "Neural_Network_Mutate": 0.1,
}


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
    global manager

    print("########Start########")

    manager = Manager(configuration)
    gui_thread = GuiThread(manager)
    gui_thread.start()

    manager.loop()

    # gui.tkinter_root.canvas.bind("<Button-1>", test_position)


if __name__ == "__main__":
    main()
