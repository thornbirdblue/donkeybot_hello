#!/usr/bin/env python3
import os
import time
import logging
from docopt import docopt


import donkeycar as dk
from donkeycar.parts import actuator, pins
from donkeycar.parts.transform import TriggeredCallback, DelayedTrigger
from donkeycar.parts.tub_v2 import TubWriter
from donkeycar.parts.datastore import TubHandler
from donkeycar.parts.controller import LocalWebController, WebFpv, JoystickController
from donkeycar.parts.throttle_filter import ThrottleFilter
from donkeycar.parts.behavior import BehaviorPart
from donkeycar.parts.file_watcher import FileWatcher
from donkeycar.parts.launch import AiLaunch
from donkeycar.utils import *

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def drive(cfg, model_path=None, use_joystick=False, model_type=None,
          camera_type='single', meta=[]):
    logger.info(f'PID: {os.getpid()}')

    #Initialize car
    V = dk.vehicle.Vehicle()

    logger.info("cfg.CAMERA_TYPE %s"%cfg.CAMERA_TYPE)
    from donkeycar.parts.camera import PiCamera
    cam = PiCamera(image_w=cfg.IMAGE_W, image_h=cfg.IMAGE_H, image_d=cfg.IMAGE_DEPTH, framerate=cfg.CAMERA_FRAMERATE, vflip=cfg.CAMERA_VFLIP, hflip=cfg.CAMERA_HFLIP)

    V.add(cam, inputs=inputs, outputs=outputs, threaded=threaded)

#This web controller will create a web server that is capable
    #of managing steering, throttle, and modes, and more.
    ctr = LocalWebController(port=cfg.WEB_CONTROL_PORT, mode=cfg.WEB_INIT_MODE)
    
    V.add(ctr,
        inputs=['cam/image_array', 'tub/num_records', 'user/mode', 'recording'],
        outputs=['user/angle', 'user/throttle', 'user/mode', 'recording'],
        threaded=True)
        
    print("You can now go to <your hostname.local>:%d to drive your car." % cfg.WEB_CONTROL_PORT)        

    # run the vehicle
    V.start(rate_hz=cfg.DRIVE_LOOP_HZ, max_loop_count=cfg.MAX_LOOPS)


if __name__ == '__main__':
    args = docopt(__doc__)
    cfg = dk.load_config(myconfig=args['--myconfig'])

    if args['drive']:
        model_type = args['--type']
        camera_type = args['--camera']
        drive(cfg, model_path=args['--model'], use_joystick=args['--js'],
              model_type=model_type, camera_type=camera_type,
              meta=args['--meta'])
