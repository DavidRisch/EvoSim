from gui import Gui

import threading
import time


class TickThread (threading.Thread):
    def __init__(self, manager, thread_id, name):
        threading.Thread.__init__(self)
        self.manager = manager
        self.thread_id = thread_id
        self.name = name

    def run(self):
        print("Starting " + self.name)
        while not self.manager.exit_tasks:
            if self.manager.thread_tick_tasks_stage[self.thread_id] == 1:
                for agent in self.manager.thread_tick_tasks[self.thread_id]:
                    self.manager.tick_agent_part_a(agent)

                self.manager.thread_tick_tasks_stage[self.thread_id] = 2
            elif self.manager.thread_tick_tasks_stage[self.thread_id] == 3:
                for agent in self.manager.thread_tick_tasks[self.thread_id]:
                    self.manager.tick_agent_part_b(agent)

                    self.manager.thread_tick_tasks[self.thread_id] = None

                self.manager.thread_tick_tasks_stage[self.thread_id] = 4

            time.sleep(0.00005)  # 0.05ms
        print("Exiting " + self.name)


class GuiThread (threading.Thread):
    def __init__(self, manager):
        threading.Thread.__init__(self)
        self.manager = manager
        self.name = "Gui thread"

    def run(self):
        print("Starting GUI thread")

        gui = Gui(self.manager.configuration)
        gui.manager = self.manager
        gui.bind_buttons()
        gui.tkinter_root.speed_slider.set(self.manager.speed)

        while not self.manager.exit_tasks:
            if not self.manager.frame_information.has_been_used:
                self.manager.frame_information.is_being_used = True
                gui.frame_information = self.manager.frame_information
                gui.draw_frame()
                self.manager.frame_information.is_being_used = False
            self.manager.frame_information.has_been_used = True

            gui.tkinter_root.update_idletasks()
            gui.tkinter_root.update()
            time.sleep(0.0001)  # 0.1ms

        # gui.tkinter_root.after(500, self.loop)

        gui.tkinter_root.mainloop()

        print("Exiting GUI thread")
