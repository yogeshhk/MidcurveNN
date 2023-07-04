from config import *
from prepare_data import read_dat_files, plot_profile_dict, scale_sequence
import pprint
import json


def convert_pointlist_to_linelist(is_profile, shapename, pointlist):
    lines = []
    if is_profile:
        for i in range(len(pointlist)):
            first_point = pointlist[i]
            if i == len(pointlist) - 1:
                end_point = pointlist[0]
            else:
                end_point = pointlist[i + 1]
            line = (first_point, end_point)
            lines.append(line)
    else:
        if shapename == 'T':
            for i in range(len(pointlist)):
                if pointlist[i] != pointlist[1]:
                    line = (pointlist[1], pointlist[i])
                    lines.append(line)
        elif shapename == 'Plus':
            for i in range(len(pointlist)):
                if pointlist[i] != pointlist[1]:
                    line = (pointlist[1], pointlist[i])
                    lines.append(line)
        else:
            for i in range(len(pointlist)):
                first_point = pointlist[i]
                if i == len(pointlist) - 1:
                    continue
                else:
                    end_point = pointlist[i + 1]
                line = (first_point, end_point)
                lines.append(line)
    return lines


def convert_dict_to_lines(pdlist):
    for dct in pdlist:
        shapename = dct['ShapeName']
        # original
        profile_point_list = dct['Profile']
        midcurve_pointlist = dct['Midcurve']
        proile_lines = convert_pointlist_to_linelist(True, shapename, profile_point_list)
        midcurve_lines = convert_pointlist_to_linelist(False, shapename, midcurve_pointlist)
        dct['Profile_lines'] = proile_lines
        dct['Midcurve_lines'] = midcurve_lines
        # scale
        # for factor in range(1, 5):
        #     scaled_profile_points = scale_sequence(profile_point_list, factor)
        #     scaled_profile_lines = convert_pointlist_to_linelist(scaled_profile_points)
        #     dct['Profile_scaled_lines_' + str(factor)] = scaled_profile_lines
        # translate
        # rotate


def write_to_json(pdlist):
    for dct in pdlist:
        filename = path.join(RAW_DATA_FOLDER, dct['ShapeName'] + ".json")
        with open(filename, 'w') as fp:
            json.dump(dct, fp, indent=4)


if __name__ == "__main__":
    shapes_dict_list = read_dat_files(RAW_DATA_FOLDER)
    convert_dict_to_lines(shapes_dict_list)
    # for dct in profiles_dict_list:
    #     plot_profile_dict(dct)
    pprint.pprint(shapes_dict_list)
    write_to_json(shapes_dict_list)
