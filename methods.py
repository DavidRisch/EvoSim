import math


def calculate_sensors(agent, food_position, distance, sensors, configuration):
    direction = calculate_direction_difference(agent.position, food_position, agent.direction)

    size_middle = configuration["Sensor_Food_Middle_Angel"] / 360
    size_side = configuration["Sensor_Food_Side_Angel"] / 360
    if (1 - size_middle / 2 - size_side) < direction < (1 - size_middle / 2):
        if sensors[0] > distance:
            sensors[0] = distance

    elif direction < size_middle / 2 or direction > (1 - size_middle / 2):
        if sensors[1] > distance:
            sensors[1] = distance

    elif size_middle / 2 < direction < size_middle / 2 + size_side:
        if sensors[2] > distance:
            sensors[2] = distance

    return sensors


def calculate_direction_difference(position_a, position_b, direction_a):
    a_to_b_x = position_b[0] - position_a[0]
    a_to_b_y = position_b[1] - position_a[1]

    angle = (math.atan2(-a_to_b_y, -a_to_b_x) + math.pi) / 2

    direction = angle / math.pi
    direction = -direction + 0.25

    direction = direction - direction_a
    while direction < 0:
        direction = 1 + direction

    return direction


def confine_number(number, minimum, maximum):
    if minimum is not None:
        if number < minimum:
            number = minimum

    if maximum is not None:
        if number > maximum:
            number = maximum

    return number


def wrap_position(position, configuration):
    for i in [0, 1]:
        if position[i] < 0:
            position[i] = configuration["Area"] + position[i]
        if position[i] > configuration["Area"]:
            position[i] = configuration["Area"] - position[i]

    return position


def wrap_direction(direction):
    if direction < 0:
        direction = 1 + direction
    if direction > 1:
        direction = 1 - direction

    return direction
