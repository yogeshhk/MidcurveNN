from config import *
from prepare_data import read_dat_files, scale_sequence, rotate_sequence, translate_sequence, mirror_sequence
import pprint
import json
import pandas as pd


def convert_pointlist_to_brep(is_profile, shapename, pointlist):
    lines = []
    if is_profile:
        for n in range(len(pointlist)):
            first_point = pointlist[n]
            if n == len(pointlist) - 1:
                end_point = pointlist[0]
            else:
                end_point = pointlist[n + 1]
            line = [list(first_point), list(end_point)]
            lines.append(line)
    else:
        if shapename == 'T':
            for n in range(len(pointlist)):
                if pointlist[n] != pointlist[1]:
                    line = [list(pointlist[1]), list(pointlist[n])]
                    lines.append(line)
        elif shapename == 'Plus':
            for n in range(len(pointlist)):
                if pointlist[n] != pointlist[1]:
                    line = [list(pointlist[1]), list(pointlist[n])]
                    lines.append(line)
        else:
            for n in range(len(pointlist)):
                first_point = pointlist[n]
                if n == len(pointlist) - 1:
                    continue
                else:
                    end_point = pointlist[n + 1]
                line = [list(first_point), list(end_point)]
                lines.append(line)
    return lines


def convert_dict_to_brep(pdlist):
    for dct in pdlist:
        shapename = dct['ShapeName']
        # original
        profile_point_list = dct['Profile']
        midcurve_point_list = dct['Midcurve']
        profile_brep = convert_pointlist_to_brep(True, shapename, profile_point_list)
        midcurve_brep = convert_pointlist_to_brep(False, shapename, midcurve_point_list)
        dct['Profile_brep'] = profile_brep
        dct['Midcurve_brep'] = midcurve_brep


def scaled_shape_list(pdlist, factor):
    scaled_pdlist = []
    for dct in pdlist:
        profile_point_list = dct['Profile']
        midcurve_point_list = dct['Midcurve']
        scaled_dict = {'Profile': scale_sequence(profile_point_list, factor),
                       'Midcurve': scale_sequence(midcurve_point_list, factor),
                       'ShapeName': dct['ShapeName'] + "_scaled_" + str(factor)}
        scaled_pdlist.append(scaled_dict)
    convert_dict_to_brep(scaled_pdlist)


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
    convert_dict_to_brep(rotated_pdlist)


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
    convert_dict_to_brep(translated_pdlist)


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
    convert_dict_to_brep(mirrored_pdlist)


def write_to_csv(pdlist):
    filename = path.join(RAW_DATA_FOLDER, "brep.csv")
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
    print(df.head())
    # df.to_csv(filename, index=False)


if __name__ == "__main__":
    shapes_dict_list = read_dat_files(RAW_DATA_FOLDER)
    convert_dict_to_brep(shapes_dict_list)
    pprint.pprint(shapes_dict_list)
    write_to_csv(shapes_dict_list)

    # for i in range(2, 6):
    #     scaled_shape_list(shapes_dict_list, i)
    # for i in range(1, 181):
    #     rotated_shape_list(shapes_dict_list, i)
    # for i in range(-50, 51, 2):
    #     translated_shape_list(shapes_dict_list, i)
    # mirrored_shape_list(shapes_dict_list, True)
    # mirrored_shape_list(shapes_dict_list, False)
