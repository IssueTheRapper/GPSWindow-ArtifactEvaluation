from almanac_interpretation import *
from Satellite_prediction import *
from Pattern_design import *

# Describe the location of the metasurfaces deployment demanding no precision
# A BLH coordinate of the building, for example, could be fine
location = [0, 0, 0]
# Describe the window orientation
# The angle in degree between the orientation and the north direction in clockwise
window_orientation = 90
# Set True if the download fails for offline demonstration
offline_flag = True
if __name__ == '__main__':
    if not offline_flag:
        interpret_path = almanac_interpretation()
        AoA_integration(interpret_path, "AoA Prediction", location, window_orientation)
    phase_update(offline_flag)

