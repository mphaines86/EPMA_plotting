### -*- coding: utf-8 -*-
"""
Created on Wed Oct 05 17:16:03 2022
@author: felixtheska

Edited and Expanded on Thu Oct 21 2022 by
Michael Haines
"""

import matplotlib.pyplot as plt
import numpy as np
import glob
from scipy import ndimage
import numpy.typing as npt


# Read data from EPMA .txt files from a JEOL silicon drift detector energy dispersive spectrometer and wavelength
# dispersive spectrometer
#
# Parameter descriptions:
#
#    file_location: (string) Directory where the EPMA map .txt files are stored
#
#    exclude: (list[str]) A list of elements to exclude from the EPMA data maps
#
# Returns:
#      dict[str, npt.ArrayLike]
#
def read_data(file_location: str, exclude: list[str] = None) -> dict[str, npt.ArrayLike]:

    if exclude is None:
        exclude = list()

    maps = glob.glob(file_location + "*.txt")
    elements = glob.glob(file_location + "*.pm")
    elements = {x.split('.')[-3].split("\\")[-1]: x.split('.')[-2] for x in elements if x.split('.')[-2] not in exclude}
    datas = {}

    for file_name in maps:
        index = file_name.split("\\")[-1].split("_")[0]
        if index not in list(elements.keys()):
            continue
        datas[elements[index]] = np.loadtxt(file_name)
    return datas


# Generate figures from EPMA map data. By default, the function will export a seperate figure for each element.
# If a tuple is passed to 'figure_grid' then it will export a figure with all elements present. Likely the kwargs
# parameters will need to be altered to get a good looking figure if the figure_grid option is used. These
# arguments pass parameters to the figure, gridspec, and imshow parameters from the matplotlib plotting
# package. However, only the 'data' parameter is required for this function to create individual plots of each
# element which might be useful if the expectation is for editing in a separate program like inkscape or
# photoshop. All other variables are optional.
#
# Parameter Descriptions:
#
#   Datas: (dict[str, NDArray) Input EPMA data in the format of a dictionary where the key is the element and the
#       values are the EPMA map data
#
#   label: (str) label for the figure. The figure will be saved with this name
#
#   pixel_size: (tuple[float, float]) Size of the pixels in µm in the x and y
#
#   figure_grid: (tuple[float, float]) By defining 'figure_grid', a figure with all elements will be exported. The
#       grid must match the number of elements such the number of rows times the number of columns equal the number
#       of elements.
#
#   limits: (dict[str, tuple[int, int]]) Defines the count limits of the maps.
#
#   color_map: (str or list[str]) Can be either a string or a list of strings. The string must be a defined matplotlib
#       colormap. If a string is passed, the colormap is applied to all maps. If a string is passed it will cycle
#       through the list sequentially and loop through said list until all elements have a defined color map. The list
#       does not have to equal the number of elements. If a list is passed, the 'Greys' colormap will be reserved for
#       the 'CP' map if included.
#
#   extension: (str) The format to save the figure in
#
#   kwargs_for_fig, kwargs_for_grid, kwards_for_imshow: (dict) These parameters pass parameters via a dictionary to
#       the figure, gridspec, and imshow functions in matplotlib. Utilize these functions in conjunction with
#       figure_grid to alter plot configurations. (https://matplotlib.org/stable/api/figure_api.html,
#        https://matplotlib.org/stable/api/_as_gen/matplotlib.gridspec.GridSpec.html,
#        https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.imshow.html)
#
# Returns:
#     None
#
def map_series(datas: dict[str, npt.ArrayLike], label="map", pixel_size=(1.0, 1.0),
               figure_grid: tuple[float, float] = None, limits: dict[str, tuple[int, int]] = None,
               color_map='Greys', extension=".png", kwargs_for_fig: dict = None, kwargs_for_grid: dict = None,
               kwargs_for_imshow: dict = None) -> None:

    if kwargs_for_fig is None:
        kwargs_for_fig = {}
    if kwargs_for_grid is None:
        kwargs_for_grid = {}
    if kwargs_for_imshow is None:
        kwargs_for_imshow = {}
    if limits is None:
        limits = {}

    map_size = list(datas.values())[0].shape
    x_map, y_map = np.meshgrid(np.arange(0, (map_size[0]) * pixel_size[0], pixel_size[0]),
                               np.arange(0, (map_size[1]) * pixel_size[1], pixel_size[1]))
    y_map = np.flip(y_map, axis=0)

    if type(color_map) is str:
        color_map = {x: color_map for x in datas.keys()}
    elif type(color_map) is list:
        len_color_map = len(color_map)
        temp_colormap = {}
        index = 0
        for x in datas.keys():
            if x == "CP":
                temp_colormap["CP"] = 'Greys'
                continue
            temp_colormap[x] = color_map[index % len_color_map]
            index += 1
        color_map = temp_colormap

    for itr, (key, values) in enumerate(datas.items()):

        element_map = ndimage.rotate(values, -90)
        fig, ax = plt.subplots()
        if key in list(limits.keys()):
            im = ax.pcolormesh(x_map, y_map, element_map, cmap=color_map[key], vmin=limits[key][0], vmax=limits[key][1],
                               shading='nearest')
        else:
            im = ax.pcolormesh(x_map, y_map, element_map, cmap=color_map[key], shading='nearest')

        ax.axis('scaled')
        ax.set_title(key)
        ax.set_xlabel(r"x ($\mu m$)")
        ax.set_ylabel(r"y ($\mu m$)")
        fig.colorbar(im, label="Counts")
        # print(key, np.amax(element_map), np.amin(element_map))
        plt.tight_layout()
        fig.savefig(label + "_" + key + extension, dpi=300)
        plt.close()

    if figure_grid is not None:
        rows = figure_grid[0]
        columns = figure_grid[1]

        fig = plt.figure(**kwargs_for_fig)
        gs = fig.add_gridspec(rows, columns, **kwargs_for_grid)

        if "CP" in list(datas.keys()):
            ax = fig.add_subplot(gs[0, 0])

            im = ax.pcolormesh(x_map, y_map, ndimage.rotate(datas["CP"], -90), shading='nearest', cmap='Greys_r')
            fig.colorbar(im, ax=ax, label="counts", use_gridspec=True)
            ax.axis('scaled')
            ax.set_ylabel(r"y ($\mu$m)")

            j = 1
            i = 0
        else:
            j = 0
            i = 0

        for key, values in datas.items():
            if key == "CP":
                continue
            ax = fig.add_subplot(gs[i, j])
            element_map = ndimage.rotate(values, -90)

            if key in list(limits.keys()):
                im = ax.pcolormesh(x_map, y_map, element_map, cmap=color_map[key], vmin=limits[key][0],
                                   vmax=limits[key][1], shading='nearest', **kwargs_for_imshow)
            else:
                im = ax.pcolormesh(x_map, y_map, element_map, cmap=color_map[key], shading='nearest',
                                   **kwargs_for_imshow)

            ax.set_title(key)
            ax.axis('scaled')

            if j == 0:
                ax.set_ylabel(r"y ($\mu m$)")
            if i + 1 == rows:
                ax.set_xlabel(r"x ($\mu m$)")

            j += 1
            if not j % columns:
                i += 1
                j %= columns

            fig.colorbar(im, ax=ax, label="counts", use_gridspec=True)

        plt.savefig(label + "_all" + extension, dpi=300)

    # print()
