import atexit
import traitlets
from traitlets.config.configurable import Configurable

left_motor_value = 0
right_motor_value = 0

class Motor(Configurable):

    value = traitlets.Float()
    
    # config
    alpha = traitlets.Float(default_value=1.0).tag(config=True)
    beta = traitlets.Float(default_value=0.0).tag(config=True)

    def __init__(self, driver, channel, *args, **kwargs):
        super(Motor, self).__init__(*args, **kwargs)  # initializes traitlets

        self._driver = driver
        self._channel = channel
        atexit.register(self._release)
        
    @traitlets.observe('value')
    def _observe_value(self, change):
        self._write_value(change['new'])

    def _write_value(self, value):
        """Sets motor value between [-1, 1]"""
        mapped_value = int(255.0 * (self.alpha * value + self.beta))
        speed = min(max(abs(mapped_value), 0), 255)

        global left_motor_value
        global right_motor_value

        # speed is in the range [0,255], for the Pololu motors we want [-300,300].
        direction = 1 if mapped_value >= 0 else -1
        motor_speed = direction * speed * 300 / 255

        if self._channel == 1:
            left_motor_value = motor_speed
        else:
            right_motor_value = motor_speed

        self._driver.motors(int(left_motor_value), int(right_motor_value))

    def _release(self):
        """Stops motor"""
        self._driver.motors(0, 0)
