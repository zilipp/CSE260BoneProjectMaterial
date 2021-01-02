from datetime import datetime
import logging
import os


def csv_out(bones, bone_type, _user_result_dir):
    bone_type_str = bone_type.name.lower()
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d-%H-%M-%S")
    filename = '{}-{}.csv'.format(dt_string, bone_type_str)
    output_file = os.path.join(_user_result_dir, filename)
    if not os.path.exists(_user_result_dir):
        os.makedirs(_user_result_dir)
    logging.info('Writing results to {}'.format(output_file))
    f = open(output_file, 'w')

    result = bones[0].get_measurement_results()
    keys = sorted(result)
    title = ','.join(keys)
    f.write(title+'\n')
    for bone in bones:
        row = list()
        measurement_results = bone.get_measurement_results()
        for key in keys:
            row.append(str(measurement_results[key]))
        line = ','.join(row)
        f.write(line+'\n')
    f.close()
    return filename
