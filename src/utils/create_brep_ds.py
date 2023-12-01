from config import *
from prepare_data import read_dat_files, scale_sequence, rotate_sequence, translate_sequence, mirror_sequence
import pprint
import json
import pandas as pd
from collections import OrderedDict
from prepare_plots import plot_breps


def convert_pointlist_to_brep(is_profile, shape_name, pointlist):
    brep = dict()
    brep["Points"] = pointlist
    if shape_name.startswith('I'):
        if is_profile:
            # Pointlist [(5.0, 5.0), (10.0, 5.0), (10.0, 20.0), (5.0, 20.0)]
            brep["Lines"] = [[0, 1], [1, 2], [2, 3], [3, 0]]  # Point indices/Ids
            brep["Segments"] = [[0, 1, 2, 3]]  # Line indices/Ids
        else:
            # Pointlist [(7.5, 5.0), (7.5, 20.0)]
            brep["Lines"] = [[0, 1]]  # Point indices/Ids
            brep["Segments"] = [[0]]  # Line indices/Ids
    elif shape_name.startswith('T'):
        if is_profile:
            # Pointlist : [(0.0, 25.0),(25.0, 25.0), (25.0, 20.0), (15.0, 20.0), (15.0, 0.0), (10.0, 0.0), (10.0,
            # 20.0),(0.0, 20.0)]
            brep["Lines"] = [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 7], [7, 0]]  # Point indices/Ids
            brep["Segments"] = [[0, 1, 2, 3, 4, 5, 6, 7]]  # Line indices/Ids
        else:
            # Pointlist : [(12.5, 0.0), (12.5, 22.5), (25.0, 22.5), (0.0, 22.5)]
            brep["Lines"] = [[0, 1], [1, 2], [3, 1]]  # Point indices/Ids
            brep["Segments"] = [[0], [1], [2]]  # Line indices/Ids

    elif shape_name.startswith('L'):
        if is_profile:
            # Pointlist : [(5.0, 5.0), (10.0, 5.0), (10.0, 30.0), (35.0, 30.0), (35.0, 35.0), (5.0, 35.0)]
            brep["Lines"] = [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]]  # Point indices/Ids
            brep["Segments"] = [[0, 1, 2, 3, 4, 5]]  # Line indices/Ids
        else:
            # Pointlist : [(7.5, 5.0), (7.5, 32.5), (35.0, 32.5)]
            brep["Lines"] = [[0, 1], [1, 2]]  # Point indices/Ids
            brep["Segments"] = [[0, 1]]  # Line indices/Ids
    elif shape_name.startswith('Plus'):
        if is_profile:
            # Pointlist : [(0.0, 25.0),(10.0, 25.0),(10.0, 45.0),(15.0, 45.0),(15.0, 25.0),(25.0, 25.0),(25.0, 20.0),
            # (15.0, 20.0),(15.0, 0.0),(10.0, 0.0),(10.0, 20.0),(0.0, 20.0)]
            brep["Lines"] = [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 7], [7, 8], [8, 9], [9, 10], [10, 11],
                             [11, 0]]  # Point indices/Ids
            brep["Segments"] = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]]  # Line indices/Ids
        else:
            # Pointlist : [(12.5, 0.0),(12.5, 22.5),(12.5, 45.0), (0.0, 22.5), (25.0, 22.5)]
            brep["Lines"] = [[0, 1], [4, 1], [2, 1], [3, 1]]  # Point indices/Ids
            brep["Segments"] = [[0], [1], [2], [3]]  # Line indices/Ids
    else:
        if is_profile:
            brep["Lines"] = []  # Point indices/Ids
            brep["Segments"] = []  # Line indices/Ids
        else:
            # Pointlist :
            brep["Lines"] = []  # Point indices/Ids
            brep["Segments"] = []  # Line indices/Ids
    return brep


def convert_dict_to_brep(points_dict_list):
    brep_dict_list = []
    for dct in points_dict_list:
        shape_name = dct['ShapeName']
        # original
        profile_point_list = dct['Profile']
        midcurve_point_list = dct['Midcurve']
        profile_brep = convert_pointlist_to_brep(True, shape_name, profile_point_list)
        midcurve_brep = convert_pointlist_to_brep(False, shape_name, midcurve_point_list)

        brep_dict = OrderedDict()
        brep_dict['ShapeName'] = shape_name
        brep_dict['Profile'] = profile_point_list
        brep_dict['Midcurve'] = midcurve_point_list
        brep_dict['Profile_brep'] = profile_brep
        brep_dict['Midcurve_brep'] = midcurve_brep
        brep_dict_list.append(brep_dict)
    return brep_dict_list


def scaled_shape_list(pdlist, factor):
    scaled_pdlist = []
    for dct in pdlist:
        profile_point_list = dct['Profile']
        midcurve_point_list = dct['Midcurve']
        scaled_dict = {'Profile': scale_sequence(profile_point_list, factor),
                       'Midcurve': scale_sequence(midcurve_point_list, factor),
                       'ShapeName': dct['ShapeName'] + "_scaled_" + str(factor)}
        scaled_pdlist.append(scaled_dict)
    return convert_dict_to_brep(scaled_pdlist)


def rotated_shape_list(pdlist, theta):
    rotated_pdlist = []
    for dct in pdlist:
        profile_point_list = dct['Profile']
        midcurve_point_list = dct['Midcurve']
        rotated_dict = {'ShapeName': dct['ShapeName'] + "_rotated_" + str(theta),
                        'Profile': rotate_sequence(profile_point_list, theta),
                        'Midcurve': rotate_sequence(midcurve_point_list, theta)
                        }
        rotated_pdlist.append(rotated_dict)
    return convert_dict_to_brep(rotated_pdlist)


def translated_shape_list(pdlist, dis):
    translated_pdlist = []
    for dct in pdlist:
        profile_point_list = dct['Profile']
        midcurve_point_list = dct['Midcurve']
        translated_dict = {'ShapeName': dct['ShapeName'] + "_translated_" + str(dis),
                           'Profile': translate_sequence(profile_point_list, dis, dis),
                           'Midcurve': translate_sequence(midcurve_point_list, dis, dis)
                           }
        translated_pdlist.append(translated_dict)
    return convert_dict_to_brep(translated_pdlist)


def mirrored_shape_list(pdlist, axis_is_x):
    mirrored_pdlist = []
    for dct in pdlist:
        profile_point_list = dct['Profile']
        midcurve_point_list = dct['Midcurve']
        mirrored_dict = {'Profile': mirror_sequence(profile_point_list, axis_is_x),
                         'Midcurve': mirror_sequence(midcurve_point_list, axis_is_x)}
        if axis_is_x:
            mirrored_dict['ShapeName'] = dct['ShapeName'] + "_mirrored_x"
        else:
            mirrored_dict['ShapeName'] = dct['ShapeName'] + "_mirrored_y"
        mirrored_pdlist.append(mirrored_dict)
    return convert_dict_to_brep(mirrored_pdlist)


def write_to_csv(pdlist, filename):
    full_file_path = path.join(RAW_DATA_FOLDER, "brep", filename)
    for dct in pdlist:
        # convert dict values to strings
        profile_point_list = dct['Profile']
        midcurve_point_list = dct['Midcurve']
        profile_brep = dct['Profile_brep']
        midcurve_brep = dct['Midcurve_brep']
        profile_point_list_s = json.dumps(profile_point_list)
        midcurve_point_list_s = json.dumps(midcurve_point_list)
        profile_brep_s = json.dumps(profile_brep)
        midcurve_brep_s = json.dumps(midcurve_brep)
        dct['Profile'] = profile_point_list_s
        dct['Midcurve'] = midcurve_point_list_s
        dct['Profile_brep'] = profile_brep_s
        dct['Midcurve_brep'] = midcurve_brep_s
    df = pd.DataFrame(pdlist)
    df.to_csv(full_file_path, index=False)


if __name__ == "__main__":
    original_shapes_dict_list = read_dat_files(RAW_DATA_FOLDER)
    shapes_brep_dict_list = convert_dict_to_brep(original_shapes_dict_list)
    plot_breps(shapes_brep_dict_list)

    for i in range(2, 6):
        shapes_brep_dict_list += scaled_shape_list(original_shapes_dict_list, i)
    for i in range(1, 181):
        shapes_brep_dict_list += rotated_shape_list(original_shapes_dict_list, i)
    for i in range(-50, 51, 2):
        shapes_brep_dict_list += translated_shape_list(original_shapes_dict_list, i)
    shapes_brep_dict_list += mirrored_shape_list(original_shapes_dict_list, True)
    shapes_brep_dict_list += mirrored_shape_list(original_shapes_dict_list, False)

    filename = "shapes2brep.csv"
    write_to_csv(shapes_brep_dict_list, filename)
