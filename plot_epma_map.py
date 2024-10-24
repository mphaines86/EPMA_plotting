import epma
import matplotlib as mpl

cm = ["Purples", "Blues", "Greens", "Reds", "YlOrBr", "RdPu", "Oranges", "BuGn", "PuBu"]
exclude_elements = ["N", "Cr", "Mo"]

mpl.rcParams.update({'font.size': 18})
lims = {"C": (9, 80), "Cr": (118, 235), "Fe": (700, 968), "Mo": (0, 9), "N": (0, 12), "Ni": (20, 100),
        "CP": (0, 1597), "O": (19, 80), "Cu": (20, 80), "Mn": (30, 70), "Nb": (0, 20), "Si": (9, 70)}

datas = epma.read_data('Maps1/.map/2\\', exclude=exclude_elements)

# Generating and exporting element maps
epma.map_series(datas, label="outer_map", pixel_size=(0.5, 0.5), figure_grid=(3, 3), color_map=cm, limits=lims,
                kwargs_for_fig={"figsize": (22, 15), "dpi": 100})