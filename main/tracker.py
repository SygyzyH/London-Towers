import time

import matplotlib.pyplot as plt

import settings

mistakes = []
mistakes_float = []
starting_time = 0  # this works
first_move_time = 0  # this works
first_move_happened = False  # this works
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
    parsed_mistakes_time = [0 for _ in range(int(starting_time), int(analysis_start_time))]
    parsed_mistakes_over_time = [0 for _ in range(int(starting_time), int(analysis_start_time))]
    number_of_mistakes = 0
    for second in range(int(starting_time), int(analysis_start_time)):
        second -= int(starting_time)
        number_of_mistakes_over_time = 0
        if second in mistakes:
            number_of_mistakes += mistakes.count(second)
            number_of_mistakes_over_time += mistakes.count(second)
        parsed_mistakes_time[second] = number_of_mistakes
        parsed_mistakes_over_time[second] = number_of_mistakes_over_time

    # parse number of moves
    parsed_moves_time = [0 for _ in range(int(starting_time), int(analysis_start_time))]
    parsed_moves_over_time = [0 for _ in range(int(starting_time), int(analysis_start_time))]
    number_of_moves = 0
    for second in range(int(starting_time), int(analysis_start_time)):
        second -= int(starting_time)
        number_of_moves_over_time = 0
        if second in moves:
            number_of_moves += moves.count(second)
            number_of_moves_over_time += moves.count(second)
        parsed_moves_time[second] = number_of_moves
        parsed_moves_over_time[second] = number_of_moves_over_time

    # prepare plots
    fig, plots = plt.subplots(2, 2, gridspec_kw={'width_ratios': [3, 1]}, sharex=True)

    # mistakes over time
    plots[0, 0].plot([0] + parsed_mistakes_time)
    plots[0, 0].plot([0] + parsed_mistakes_over_time, "--")
    plots[0, 0].plot(len(parsed_mistakes_time), max(parsed_mistakes_time), "ro", ms=5)
    plots[0, 0].legend(["Total mistakes over time", "Mistakes per second", "Mistakes made: " + str(len(mistakes))], loc="best")
    plots[0, 0].set(ylabel='Mistakes')
    plots[0, 0].set_title("Accuracy")
    plots[0, 0].grid(True)

    # number of moves over time
    plots[1, 0].plot([0] + parsed_moves_time)
    plots[1, 0].plot([0] + parsed_moves_over_time, "--")
    plots[1, 0].plot(len(parsed_moves_time), len([i for i in moves if i != -1]), "ro", ms=5)
    plots[1, 0].legend(["Total moves over time", "Moves per second", "Total moves: " + str(len([i for i in moves if i != -1]))], loc="best")
    plots[1, 0].set(xlabel='Time', ylabel='Moves')
    plots[1, 0].set_title("Speed")
    plots[1, 0].grid(True)

    plots[0, 1].axis("off")
    plots[1, 1].axis("off")

    # add separation lines after every stage
    for mistake in range(len(mistakes_float)):
        if type(mistakes_float[mistake]) == list:
            plots[0, 0].axvline(x=mistakes_float[mistake][0], color="black", linestyle="dotted")

    for move in range(len(moves_float)):
        if type(moves_float[move]) == list:
            plots[1, 0].axvline(x=moves_float[move][0], color="black", linestyle="dotted")

    # parse starting times
    starting_time_table = [0]
    for move in range(len(moves_float)):
        if type(moves_float[move]) == list:
            starting_time_table.append(round(moves_float[move][0], 3))

    # parse first move times table
    first_move_time_table = [round(moves_float[0], 3)]
    for move in range(len(moves_float)):
        if type(moves_float[move]) == list:
            first_move_time_table.append(round(moves_float[move + 1], 3))

    # rotate 90 degrees
    table = list(zip(*[first_move_time_table, starting_time_table][::-1]))

    # add the differance column
    parsed_table = []
    for row in table:
        row = list(row)
        row.append(round(row[1] - row[0], 3))
        parsed_table.append(row)

    # add the total time column
    for row in range(len(parsed_table) - 1):
        parsed_table[row][1] = round(parsed_table[row + 1][0] - parsed_table[row][0], 3)
    parsed_table[-1][1] = round((analysis_start_time - starting_time) - parsed_table[-1][0], 3)

    # add the steps taken for each stage
    moves_taken = []
    counter = 0
    for i in range(len(moves_float)):
        if type(moves_float[i]) == list:
            moves_taken.append(counter)
            counter = 0
        else:
            counter += 1
    # takes care of the last move
    moves_taken.append(counter)

    for move in range(len(moves_taken)):
        parsed_table[move][0] = moves_taken[move]

    plots = fig.add_subplot(1, 3, 3)

    # decide on the colors of each cell in table
    colors = [['w' for i in range(len(parsed_table[0]))] for j in range(len(parsed_table))]
    print(colors, parsed_table)
    for i in range(len(colors)):
        for j in range(len(colors[i])):
            if j == 0:
                # this case will occur if the patient has done too many moves
                pass
            elif j == 1:
                if parsed_table[i][j] >= 120:
                    # this case will occur if the patient took too long to finish the stage.
                    colors[i][j] = '#960200'
            else:
                if parsed_table[i][j] < 0:
                    # this case will occur if the patient took too long to finish the stage.
                    colors[i][j] = '#960200'

    # first move times table
    plots.set_title("Patience")
    table_obj = plots.table(cellText=parsed_table, colLabels=["Extra moves", "Total time", "First move"], cellColours=colors, loc="upper center")
    table_obj.auto_set_font_size(False)
    table_obj.set_fontsize(9)
    plots.axis("off")

    # TODO: solver needs to be able to return the number of steps required to solve a pole stack. than this can
    # TODO: introduced here, replacing starting_time_table in the zip with some argument of minimal steps.

    plt.gcf().canvas.set_window_title("Test Results")
    plt.get_current_fig_manager().resize(settings.SCREEN_DIMENSIONS[0], settings.SCREEN_DIMENSIONS[1])

    # plot
    plt.show()
