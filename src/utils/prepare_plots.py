import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import json
import os
# from config import JSON_FOLDER
JSON_FOLDER = "."
matplotlib.use('TKAgg')


def plot_results(original_imgs, computed_imgs):
    n = len(original_imgs)  # 10 # how many digits we will display
    plt.figure(figsize=(20, 4))
    for i in range(n):
        # display original
        ax = plt.subplot(2, n, i + 1)
        plt.imshow(original_imgs[i].reshape(100, 100), cmap='gray_r')
        #         plt.gray()
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)

        # display reconstruction
        ax = plt.subplot(2, n, i + 1 + n)
        plt.imshow(computed_imgs[i].reshape(100, 100), cmap='gray_r')
        #         plt.gray()
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
    plt.show()


def plot_jsons(datafolder=JSON_FOLDER):
    for file in os.listdir(datafolder):
        if file.endswith(".json"):
            with open(os.path.join(JSON_FOLDER, file)) as json_file:
                shape_dict = json.load(json_file)
            profile_lines = shape_dict['Profile_lines']
            midcurve_lines = shape_dict['Midcurve_lines']
            plot_lines(profile_lines, 'black')
            plot_lines(midcurve_lines, 'red')
            # for line in profile_lines:
            #     a = np.asarray(line)
            #     x = a[:, 0].T
            #     y = a[:, 1].T
            #     plt.plot(x, y, c='black')
            # for line in midcurve_lines:
            #     a = np.asarray(line)
            #     x = a[:, 0].T
            #     y = a[:, 1].T
            #     plt.plot(x, y, c='red')
        plt.axis('equal')
        plt.show()


def plot_segments(segments, lines, points, color='blue', marker='o'):
    x_coords, y_coords = zip(*points)
    for segment in segments:
        for line_idx in segment:
            line = lines[line_idx]
            x_segment = [x_coords[i] for i in line]
            y_segment = [y_coords[i] for i in line]
            plt.plot(x_segment + [x_segment[0]], y_segment + [y_segment[0]], color=color,
                     marker=marker)


def plot_breps(shapes_brep_dict_list):
    for dct in shapes_brep_dict_list:
        profile_point_list = dct['Profile']
        profile_x_coords, profile_y_coords = zip(*profile_point_list)
        profile_brep = dct['Profile_brep']
        profile_segments = profile_brep["Segments"]
        profile_lines = profile_brep["Lines"]
        profile_segment_color = 'black'
        # Plot Profile segments
        # for segment in profile_segments:
        #     for line_idx in segment:
        #         line = profile_lines[line_idx]
        #         x_segment = [profile_x_coords[i] for i in line]
        #         y_segment = [profile_y_coords[i] for i in line]
        #         plt.plot(x_segment + [x_segment[0]], y_segment + [y_segment[0]], color=profile_segment_color,
        #                  marker='o')
        plot_segments(profile_segments, profile_lines, profile_point_list, profile_segment_color, 'o')

        midcurve_point_list = dct['Midcurve']
        midcurve_x_coords, midcurve_y_coords = zip(*midcurve_point_list)
        midcurve_brep = dct['Midcurve_brep']
        midcurve_segments = midcurve_brep["Segments"]
        midcurve_lines = midcurve_brep["Lines"]
        midcurve_segment_color = 'red'

        # Plot Midcurve segments
        # for segment in midcurve_segments:
        #     for line_idx in segment:
        #         line = midcurve_lines[line_idx]
        #         x_segment = [midcurve_x_coords[i] for i in line]
        #         y_segment = [midcurve_y_coords[i] for i in line]
        #         plt.plot(x_segment + [x_segment[0]], y_segment + [y_segment[0]], color=midcurve_segment_color,
        #                  marker='x')
        plot_segments(midcurve_segments, midcurve_lines, midcurve_point_list, midcurve_segment_color, 'x')
        plt.axis('equal')
        plt.show()


def plot_lines(lines, color='black'):
    for line in lines:
        a = np.asarray(line)
        x = a[:, 0].T
        y = a[:, 1].T
        plt.plot(x, y, c=color)

import numpy as np
import matplotlib.pyplot as plt

def plot_list_of_lines(list_of_lines, names, color='black', figsize=(15, 5)):
    """
    Plot each geometrical figure in its own subplot with a given name as title.
    
    Parameters:
    -----------
    list_of_lines : list
        List where each element is a set of lines comprising a geometrical figure.
        Each figure is a list of line coordinates where each line is a tuple of points.
    names : list
        List of names for each figure (used as subplot titles).
    color : str or list, optional
        Color to use for plotting lines. Can be a single color for all figures
        or a list of colors (one per figure). Default: 'black'.
    figsize : tuple, optional
        Figure size (width, height) in inches (default: (15, 5)).
    """
    # Check if list_of_lines and names have the same length
    if len(list_of_lines) != len(names):
        raise ValueError("The lengths of 'list_of_lines' and 'names' must be the same.")
    
    # Handle colors
    if isinstance(color, str):
        colors = [color] * len(list_of_lines)
    elif len(color) >= len(list_of_lines):
        colors = color
    else:
        colors = color * (len(list_of_lines) // len(color) + 1)
        colors = colors[:len(list_of_lines)]
    
    # Create subplots
    fig, axes = plt.subplots(1, len(list_of_lines), figsize=figsize)
    
    # Handle case where there's only one figure
    if len(list_of_lines) == 1:
        axes = [axes]
    
    # Plot each figure in its own subplot
    for i, (lines, name, line_color) in enumerate(zip(list_of_lines, names, colors)):
        for line in lines:
            a = np.asarray(line)
            x = a[:, 0].T
            y = a[:, 1].T
            axes[i].plot(x, y, c=line_color)
        
        axes[i].set_title(name)
        axes[i].axis('equal')
    
    # Adjust layout
    plt.tight_layout()
    
    return fig, axes



if __name__ == "__main__":
    chatgpt_lines = [((2.5, 0), (2.5, 22.5)), ((2.5, 22.5), (2.5, 45.0)), ((2.5, 22.5), (25.0, 22.5)),
                     ((2.5, 22.5), (12.5, 22.5)), ((2.5, 22.5), (0, 22.5)), ((2.5, 22.5), (25.0, 22.5))]
    perplexity_lines = [((12.5, 0), (12.5, 22.5)), ((12.5, 22.5), (12.5, 45.0)), ((12.5, 22.5), (0, 22.5)),
                        ((12.5, 22.5), (25.0, 22.5))]
    bard_liens = [((12.5, 0), (12.5, 25.0)), ((12.5, 25.0), (25.0, 25.0)), ((25.0, 25.0), (25.0, 0))]
    huggingface_chat_lines = [((12.5, 0), (12.5, 22.5)), ((12.5, 22.5), (25.0, 22.5)), ((25.0, 22.5), (25.0, 25.0))]
    gpt4_lines = [((12.5, 0), (12.5, 22.5)), ((12.5, 22.5), (0, 22.5)), ((12.5, 22.5), (25.0, 22.5))]
    claude_lines = [((12.5, 0.0), (12.5, 22.5)), ((12.5, 22.5), (12.5, 25.0)), ((12.5, 22.5), (0.0, 22.5)),
                    ((12.5, 22.5), (25.0, 22.5))]
    gemini_pro_lines = [((12.5,0), (12.5, 22.5)), ((12.5, 22.5),(12.5,45.0)), ((12.5, 22.5), (0,22.5))]

    profile =  [((-5.65, -4.26), (-10.6, -3.56), (-14.08, -28.32), (-38.83, -24.84), (-39.53, -29.79), (-9.82, -33.96), (-5.65, -4.26))]
    actual_midcurve = [((-8.12, -3.91), (-11.95, -31.14), (-39.18, -27.31))]
    predicted_midcurve = [((-8.13, -3.91), (-18.31, -31.51), (-26.46, -26.58))]
    
    
    list_of_lines = [profile, actual_midcurve, predicted_midcurve]
    figure_names = ["profile", "actual_midcurve", "predicted_midcurve"]
    
    fig, axes = plot_list_of_lines(list_of_lines, figure_names, color=['red', 'blue','green'])
    plt.show()
        
    # plot_lines(test_lines, 'red')
    # plt.axis('equal')
    # plt.show()
    # # plot_jsons()
