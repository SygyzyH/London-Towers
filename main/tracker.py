import time

import matplotlib.pyplot as plt

import settings

mistakes = []
mistakes_float = []
starting_time = 0
first_move_time = 0
first_move_happened = False
analysis_start_time = 0
moves = []
moves_float = []


def begin():
    global starting_time
    starting_time = time.time()


def first_move():
    global first_move_time, first_move_happened
    if not first_move_happened:
        first_move_time = time.time() - starting_time
        first_move_happened = True


def add_mistake():
    mistakes.append(int(time.time() - starting_time))
    mistakes_float.append(time.time() - starting_time)


def add_move(failed=False):
    if not failed:
        moves.append(int(time.time() - starting_time))
        moves_float.append(time.time() - starting_time)
    else:
        moves.append(-1)
        moves_float.append(-1)


def stage_completed():
    # mark a stage was completed by saving a list instead of a float
    mistakes_float.append([time.time() - starting_time])
    moves_float.append([time.time() - starting_time])


def plot_results():
    # parse mistakes time
    parsed_mistakes_time, parsed_mistakes_over_time = spread_over_time(mistakes)
    parsed_moves_time, parsed_moves_over_time = spread_over_time(moves)

    # prepare plots
    fig, plots = plt.subplots(2, 2, gridspec_kw={'width_ratios': [3, 1]}, sharex=True)

    # plot mistakes and mistakes over time
    plots[0, 0].plot([0] + parsed_mistakes_time)
    plots[0, 0].plot([0] + parsed_mistakes_over_time, "--")
    plots[0, 0].plot(len(parsed_mistakes_time), max(parsed_mistakes_time), "ro", ms=5)
    plots[0, 0].legend(["Total mistakes over time", "Mistakes per second", "Mistakes made: " + str(len(mistakes))], loc="best")
    plots[0, 0].set(ylabel='Mistakes')
    plots[0, 0].set_title("Accuracy")
    plots[0, 0].grid(True)

    # plot moves and moves over time
    plots[1, 0].plot([0] + parsed_moves_time)
    plots[1, 0].plot([0] + parsed_moves_over_time, "--")
    plots[1, 0].plot(len(parsed_moves_time), len([i for i in moves if i != -1]), "ro", ms=5)
    plots[1, 0].legend(["Total moves over time", "Moves per second", "Total moves: " + str(len([i for i in moves if i != -1]))], loc="best")
    plots[1, 0].set(xlabel='Time', ylabel='Moves')
    plots[1, 0].set_title("Speed")
    plots[1, 0].grid(True)

    # remove additional plots in subplot
    plots[0, 1].remove()
    plots[1, 1].remove()

    # add separation lines after every stage
    for mistake in range(len(mistakes_float)):
        if type(mistakes_float[mistake]) == list:
            x = mistakes_float[mistake][0]
            plots[0, 0].axvline(x=x, color="black", linestyle="dotted")
            plots[1, 0].axvline(x=x, color="black", linestyle="dotted")

    # parse timers
    total_time = []
    moves_taken = []
    first_move_time_table = [round(moves_float[0], 3)]
    counter = 0
    for move in range(len(moves_float)):
        if type(moves_float[move]) == list:
            # total time = this stage completion time - time so far
            total_time.append(round(moves_float[move][0] - sum(total_time), 3))

            # number of moves
            moves_taken.append(counter)
            counter = 0

            # first move = first action time (after this stage's completion) - total time
            if move < len(moves_float) - 1:
                first_move_time_table.append(round(moves_float[move + 1] - moves_float[move][0], 3))
        else:
            counter += 1
    moves_taken.append(counter)

    # rotate table 90 degrees
    table = list(zip(*[first_move_time_table, total_time, moves_taken][::-1]))

    # add the table subplot
    plots = fig.add_subplot(1, 3, 3)

    # decide on the colors of each cell in table
    colors = [['w' for i in range(len(table[0]))] for j in range(len(table))]
    for i in range(len(colors)):
        for j in range(len(colors[i])):
            if j == 0:
                # this case will occur if the patient has done too many moves
                pass
            elif j == 1:
                if table[i][j] >= 120:
                    # this case will occur if the patient took too long to finish the stage.
                    colors[i][j] = '#960200'
            else:
                if table[i][j] < 0:
                    # this case will occur if the patient took too long to finish the stage.
                    colors[i][j] = '#960200'

    # plot timers table
    plots.set_title("Patience")
    table_obj = plots.table(cellText=table, colLabels=["Moves", "Total time", "First move"], cellColours=colors, loc="upper center")
    table_obj.auto_set_font_size(False)
    table_obj.set_fontsize(9)
    plots.axis("off")

    # TODO: solver needs to be able to return the number of steps required to solve a pole stack. than this can
    # TODO: introduced here, replacing starting_time_table in the zip with some argument of minimal steps.

    plt.gcf().canvas.set_window_title("Test Results")
    plt.get_current_fig_manager().resize(settings.SCREEN_DIMENSIONS[0], settings.SCREEN_DIMENSIONS[1])

    # plot
    plt.show()


def spread_over_time(timestamps):
    parsed_actions = [0 for _ in range(int(starting_time), int(analysis_start_time))]
    parsed_actions_over_time = [0 for _ in range(int(starting_time), int(analysis_start_time))]
    total_number_of_actions = 0
    for second in range(int(starting_time), int(analysis_start_time)):
        second -= int(starting_time)
        number_of_moves_over_time = 0
        if second in timestamps:
            total_number_of_actions += timestamps.count(second)
            number_of_moves_over_time += timestamps.count(second)
        parsed_actions[second] = total_number_of_actions
        parsed_actions_over_time[second] = number_of_moves_over_time
    return parsed_actions, parsed_actions_over_time
