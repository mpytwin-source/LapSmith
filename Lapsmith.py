import math

# --------------------
# FUNCTIONS
# --------------------

def calculate_drag(speed):
    return 0.5 * air_density * speed ** 2 * drag_coefficient * frontal_area

def calculate_downforce(speed):
    return 0.5 * air_density * speed ** 2 * downforce_coefficient * frontal_area

def calculate_engine_force(speed):
    if speed > 0:
        return wheel_power / speed
    return 0

def calculate_corner_speed(radius):
    corner_speed = 20
    for i in range(20):
        downforce = calculate_downforce(corner_speed)
        normal_force = weight * gravity + downforce
        corner_force = tire_grip * normal_force
        corner_speed = math.sqrt((corner_force * radius) / weight)
    return corner_speed

def record_telemetry(time, distance, speed, acceleration, drag, downforce, state):
    telemetry_time.append(time)
    telemetry_distance.append(distance)
    telemetry_speed.append(speed * 2.23694)
    telemetry_acceleration.append(acceleration)
    telemetry_drag.append(drag)
    telemetry_downforce.append(downforce)
    telemetry_state.append(state)


# --------------------
# CHOOSE CAR
# --------------------

print("LapLab Motorsport Simulator")

car_name = input("Choose car type (GT, Formula, Hyper Car, Stock Car): ")

if car_name == "GT":
    horsepower = 550
    weight = 1300
    min_wing = 2
    max_wing = 14
    drag_coefficient = 0.40
    downforce_coefficient = 0.60
    frontal_area = 2.0
    tire_grip = 1.3

elif car_name == "Formula":
    horsepower = 750
    weight = 800
    min_wing = 10
    max_wing = 30
    drag_coefficient = 0.70
    downforce_coefficient = 1.50
    frontal_area = 1.5
    tire_grip = 1.8

elif car_name == "Hyper Car":
    horsepower = 670
    weight = 1030
    min_wing = 0
    max_wing = 12
    drag_coefficient = 0.35
    downforce_coefficient = 1.20
    frontal_area = 1.9
    tire_grip = 1.6

elif car_name == "Stock Car":
    horsepower = 670
    weight = 1500
    min_wing = 0
    max_wing = 5
    drag_coefficient = 0.45
    downforce_coefficient = 0.50
    frontal_area = 2.2
    tire_grip = 1.4

else:
    print("Invalid car type.")
    exit()


# --------------------
# REAR WING
# --------------------

rear_wing = float(input(f"Enter rear wing setting ({min_wing}-{max_wing}): "))

if rear_wing < min_wing or rear_wing > max_wing:
    print("Rear wing setting is outside the allowed range.")
    exit()

wing_position = (rear_wing - min_wing) / (max_wing - min_wing)
drag_coefficient += wing_position * 0.10
downforce_coefficient += wing_position * 0.30


# --------------------
# STARTING SPEED
# --------------------

speed_mph = float(input("Enter starting speed (mph): "))
speed_ms = speed_mph * 0.44704


# --------------------
# CONSTANTS
# --------------------

air_density = 1.225
gravity = 9.81
drivetrain_efficiency = 0.85
time_step = 0.1

power_watts = horsepower * 745.7
wheel_power = power_watts * drivetrain_efficiency


# --------------------
# TEST TRACK
# --------------------

track = [
    ["straight", 500],
    ["corner", 80, 120],
    ["straight", 300],
    ["corner", 40, 90],
    ["straight", 400],
    ["corner", 120, 180],
    ["straight", 250]
]

track_distance = 0

for section in track:
    if section[0] == "straight":
        track_distance += section[1]
    else:
        track_distance += section[2]


# --------------------
# TELEMETRY
# --------------------

telemetry_time = []
telemetry_distance = []
telemetry_speed = []
telemetry_acceleration = []
telemetry_drag = []
telemetry_downforce = []
telemetry_state = []


# --------------------
# LAP SETUP
# --------------------

current_speed = speed_ms
total_time = 0
total_distance = 0

print()
print("==============================")
print("        LAP SIMULATION")
print("==============================")


# --------------------
# LAP SIMULATION
# --------------------

for i in range(len(track)):
    section = track[i]
    section_type = section[0]

    # STRAIGHT
    if section_type == "straight":
        straight_length = section[1]
        section_distance = 0
        section_time = 0
        entry_speed = current_speed
        target_speed = None

        # Check next corner
        if i + 1 < len(track):
            next_section = track[i + 1]

            if next_section[0] == "corner":
                corner_radius = next_section[1]
                target_speed = calculate_corner_speed(corner_radius)

        # Drive straight
        while section_distance < straight_length:
            drag = calculate_drag(current_speed)
            downforce = calculate_downforce(current_speed)
            normal_force = weight * gravity + downforce
            distance_left = straight_length - section_distance
            braking = False

            # Decide when to brake
            if target_speed is not None and current_speed > target_speed:
                braking_force = tire_grip * normal_force + drag
                deceleration = braking_force / weight
                braking_distance = (current_speed ** 2 - target_speed ** 2) / (2 * deceleration)

                if distance_left <= braking_distance:
                    braking = True

            # Brake
            if braking:
                braking_force = tire_grip * normal_force + drag
                acceleration = -(braking_force / weight)
                current_speed += acceleration * time_step

                if current_speed < target_speed:
                    current_speed = target_speed

                state = "braking"

            # Accelerate
            else:
                engine_force = calculate_engine_force(current_speed)
                max_traction = tire_grip * normal_force

                if engine_force > max_traction:
                    engine_force = max_traction

                net_force = engine_force - drag
                acceleration = net_force / weight
                current_speed += acceleration * time_step
                state = "accelerating"

            # Update distance and time
            step_distance = current_speed * time_step
            remaining_distance = straight_length - section_distance
            actual_time_step = time_step

            if step_distance > remaining_distance:
                step_distance = remaining_distance

                if current_speed > 0:
                    actual_time_step = step_distance / current_speed

            section_distance += step_distance
            total_distance += step_distance
            section_time += actual_time_step
            total_time += actual_time_step

            record_telemetry(
                total_time, total_distance, current_speed,
                acceleration, drag, downforce, state
            )

        # Straight results
        entry_speed_mph = entry_speed * 2.23694
        exit_speed_mph = current_speed * 2.23694

        print()
        print("Straight:", straight_length, "m")
        print("Entry Speed:", round(entry_speed_mph, 2), "mph")
        print("Exit Speed:", round(exit_speed_mph, 2), "mph")
        print("Time:", round(section_time, 2), "seconds")

    # CORNER
    elif section_type == "corner":
        corner_radius = section[1]
        corner_length = section[2]
        corner_limit = calculate_corner_speed(corner_radius)

        section_distance = 0
        section_time = 0
        entry_speed = current_speed

        # Drive corner
        while section_distance < corner_length:
            drag = calculate_drag(current_speed)
            downforce = calculate_downforce(current_speed)
            normal_force = weight * gravity + downforce

            # Too fast
            if current_speed > corner_limit:
                braking_force = tire_grip * normal_force + drag
                acceleration = -(braking_force / weight)
                current_speed += acceleration * time_step

                if current_speed < corner_limit:
                    current_speed = corner_limit

                state = "corner braking"

            # Below corner limit
            elif current_speed < corner_limit:
                engine_force = calculate_engine_force(current_speed)
                max_traction = tire_grip * normal_force

                if engine_force > max_traction:
                    engine_force = max_traction

                net_force = engine_force - drag
                acceleration = net_force / weight
                current_speed += acceleration * time_step

                if current_speed > corner_limit:
                    current_speed = corner_limit

                state = "corner acceleration"

            # At corner limit
            else:
                acceleration = 0
                state = "cornering"

            # Update distance and time
            step_distance = current_speed * time_step
            remaining_distance = corner_length - section_distance
            actual_time_step = time_step

            if step_distance > remaining_distance:
                step_distance = remaining_distance

                if current_speed > 0:
                    actual_time_step = step_distance / current_speed

            section_distance += step_distance
            total_distance += step_distance
            section_time += actual_time_step
            total_time += actual_time_step

            record_telemetry(
                total_time, total_distance, current_speed,
                acceleration, drag, downforce, state
            )

        # Corner results
        entry_speed_mph = entry_speed * 2.23694
        exit_speed_mph = current_speed * 2.23694
        corner_limit_mph = corner_limit * 2.23694

        print()
        print("Corner Radius:", corner_radius, "m")
        print("Corner Length:", corner_length, "m")
        print("Entry Speed:", round(entry_speed_mph, 2), "mph")
        print("Corner Limit:", round(corner_limit_mph, 2), "mph")
        print("Exit Speed:", round(exit_speed_mph, 2), "mph")
        print("Corner Time:", round(section_time, 2), "seconds")


# --------------------
# FINAL RESULTS
# --------------------

final_speed_mph = current_speed * 2.23694
average_speed_ms = track_distance / total_time
average_speed_mph = average_speed_ms * 2.23694
average_speed_kmh = average_speed_ms * 3.6

minutes = int(total_time // 60)
seconds = total_time % 60

print()
print("==============================")
print("         LAP RESULTS")
print("==============================")
print("Car:", car_name)
print("Horsepower:", horsepower, "hp")
print("Weight:", weight, "kg")
print("Rear Wing:", rear_wing)
print("Tire Grip:", tire_grip)
print()
print("Track Distance:", track_distance, "m")
print("Simulated Distance:", round(total_distance, 2), "m")
print("Starting Speed:", speed_mph, "mph")
print("Final Speed:", round(final_speed_mph, 2), "mph")
print("Average Speed:", round(average_speed_mph, 2), "mph")
print("Average Speed:", round(average_speed_kmh, 2), "km/h")
print("Lap Time:", f"{minutes}:{seconds:05.2f}")


# --------------------
# TELEMETRY SAMPLE
# --------------------

print()
print("==============================")
print("       TELEMETRY SAMPLE")
print("==============================")

for i in range(0, len(telemetry_time), 20):
    print(
        round(telemetry_time[i], 1), "s |",
        round(telemetry_distance[i], 1), "m |",
        round(telemetry_speed[i], 1), "mph |",
        telemetry_state[i]
    )


# --------------------
# GRAPH
# --------------------

try:
    import matplotlib.pyplot as plt

    plt.plot(telemetry_distance, telemetry_speed)
    plt.xlabel("Distance (m)")
    plt.ylabel("Speed (mph)")
    plt.title("LapLab Speed vs Distance")
    plt.grid()
    plt.show()

except ImportError:
    print()
    print("Install matplotlib to see the telemetry graph.")
    print("Run: pip install matplotlib")