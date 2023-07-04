from config import *
from prepare_data import read_dat_files


def convert_pointlist_to_linelist(shapename, pointlist, is_profile):
    lines = []
    return lines


def convert_dict_to_lines(pdlist):
    for dct in pdlist:
        profile_point_list = dct['Profile']
        shapename = dct['ShapeName']
        midcurve_pointlist = dct['Midcurve']
        proile_lines = convert_pointlist_to_linelist(shapename, profile_point_list, True)
        midcurve_lines = convert_pointlist_to_linelist(shapename, midcurve_pointlist,False)
        dct['Profile_lines'] = proile_lines
        dct['Midcurve_lines'] = midcurve_lines


if __name__ == "__main__":
    profiles_dict_list = read_dat_files(RAW_DATA_FOLDER)
    convert_dict_to_lines(profiles_dict_list)
    print(profiles_dict_list)
