# An automatic tool for bone measurement

The structure of the project is as following:

```
+-- data
|   +-- iphone_ten
|   +-- structure_sensor
+-- web
|   +-- core_alg
|   +-- out
|   +-- test_picture.py
|   +-- test_scan.py
+-- README.md
+-- .gitignore
```

## Here is the recipe:

### 1. To get all obj files. 
The "./data" folder contains both 3D model from iPhone10 and structure sensor. \
For example, to get an obj file taken from structure_sensor/picture/femur/*. The director path is: data/structure_sensor/picture/femur \
For example, to get an obj file taken from structure_sensor/scan/tibia/*. The director path is: data/structure_sensor/scan/tibia

### 2. To get the code from Github

### 3. The IDE suggested to use is Pycharm 2020.1.2 x 64, and use pip install to install all packages in requirements.txt 

### 4. To run measurements on specific 3D model:
The main file of measurement is in: msresearch/web/test_scan.py. \
This file will take either single 3D model or multi 3D models as input, and output the measurements to a *.csv file.  \
Please specify global variables, such us bone type, input file name, and if the model taken from iPhone or structure sensor. \
For example, to run measurement on femur_4.obj taken by sensor, set bone_type = Bone.Type.FEMUR, and index_default = 4, structure_sensor = True.

### 5. Take the output numbers and compare to ground truth from <msresearch/web/core_alg/utilities/results_anlysis.py>.
If the input are multi models, then it will also output a *.csv file which calculates mean values, absolute errors, standard derivations with ground truth \
If the input is single model, error should be manually computed with a calculator