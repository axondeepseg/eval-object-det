```                                               
                 _         _     _           _         _      _   
  _____   ____ _| |   ___ | |__ (_) ___  ___| |_    __| | ___| |_ 
 / _ \ \ / / _` | |  / _ \| '_ \| |/ _ \/ __| __|  / _` |/ _ \ __|
|  __/\ V / (_| | | | (_) | |_) | |  __/ (__| |_  | (_| |  __/ |_ 
 \___| \_/ \__,_|_|  \___/|_.__// |\___|\___|\__|  \__,_|\___|\__|
                              |__/                                                              
```

![schematics](postprocessing_before_obj_detection_eval.png)

## Setup the environment
You know the drill: setup a venv to isolate your environment (using `conda`, `pyenv`, ...). For example:

```
conda create python==3.12.9 -n eval-obj-det
conda activate eval-obj-det
conda env update --file environment.yaml
```

This should install AxonDeepSeg so we can use its utilities to postprocess the semantic segmentations.

