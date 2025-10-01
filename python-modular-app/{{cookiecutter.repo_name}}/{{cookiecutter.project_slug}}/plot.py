import matplotlib.pyplot as plt


def process_default_figure_axis_input(figure, axis):
    if figure is None and axis is None:
        figure = plt.figure()
        axis = figure.add_subplot(111)
    elif figure is None:
        figure = axis.get_figure()
    elif axis is None:
        axes = figure.axes
        if len(axes) > 0:
            axis = axes[0]
        else:
            axis = figure.add_subplot(111)
    return figure, axis


def plot_SOMETHING(data, figure=None, axis=None):
    figure, axis = process_default_figure_axis_input(figure, axis)
    figure.tight_layout()
    return figure


def plot(data):
    figures = dict()
    figures["SOMETHING"] = plot_SOMETHING(data)
    return figures


def show():
    plt.show()