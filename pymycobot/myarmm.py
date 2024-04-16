# coding=utf-8

from __future__ import division
import time
import math
import threading
import logging

from pymycobot.log import setup_logging
from pymycobot.generate import CommandGenerator
from pymycobot.common import ProtocolCode, write, read
from pymycobot.error import calibration_parameters


class MyArmM(CommandGenerator):
    """

    """

    def __init__(self, port, baudrate="115200", timeout=0.1, debug=False):
        """
        Args:
            port     : port string
            baudrate : baud rate string, default '115200'
            timeout  : default 0.1
            debug    : whether show debug info
        """
        super(MyArmM, self).__init__(debug)
        self.calibration_parameters = calibration_parameters
        import serial
        self._serial_port = serial.Serial()
        self._serial_port.port = port
        self._serial_port.baudrate = baudrate
        self._serial_port.timeout = timeout
        self._serial_port.rts = False
        self._serial_port.open()
        self.lock = threading.Lock()

    _write = write
    _read = read

    def _mesg(self, genre, *args, **kwargs):
        """
        Args:
            genre: command type (Command)
            *args: other data.
                   It is converted to octal by default.
                   If the data needs to be encapsulated into hexadecimal,
                   the array is used to include them. (Data cannot be nested)
            **kwargs: support `has_reply`
                has_reply: Whether there is a return value to accept.
        """
        real_command, has_reply = super(MyArmM, self)._mesg(genre, *args, **kwargs)
        command = self._flatten(real_command)
        with self.lock:
            self._write(command)

            if has_reply:
                data = self._read(genre, command=command)
                res = self._process_received(data, genre, arm=7)
                if res == []:
                    return None
                if genre in [
                    ProtocolCode.ROBOT_VERSION,
                    ProtocolCode.GET_ROBOT_ID,
                    ProtocolCode.IS_POWER_ON,
                    ProtocolCode.IS_CONTROLLER_CONNECTED,
                    ProtocolCode.IS_PAUSED,  # TODO have bug: return b''
                    ProtocolCode.IS_IN_POSITION,
                    ProtocolCode.IS_MOVING,
                    ProtocolCode.IS_SERVO_ENABLE,
                    ProtocolCode.IS_ALL_SERVO_ENABLE,
                    ProtocolCode.GET_SERVO_DATA,
                    ProtocolCode.GET_DIGITAL_INPUT,
                    ProtocolCode.GET_GRIPPER_VALUE,
                    ProtocolCode.IS_GRIPPER_MOVING,
                    ProtocolCode.GET_SPEED,
                    ProtocolCode.GET_ENCODER,
                    ProtocolCode.GET_BASIC_INPUT,
                    ProtocolCode.GET_TOF_DISTANCE,
                    ProtocolCode.GET_END_TYPE,
                    ProtocolCode.GET_MOVEMENT_TYPE,
                    ProtocolCode.GET_REFERENCE_FRAME,
                    ProtocolCode.GET_FRESH_MODE,
                    ProtocolCode.GET_GRIPPER_MODE,
                    ProtocolCode.GET_ERROR_INFO,
                    ProtocolCode.SET_SSID_PWD,
                    ProtocolCode.SetHTSGripperTorque,
                    ProtocolCode.GetHTSGripperTorque,
                    ProtocolCode.GetGripperProtectCurrent,
                    ProtocolCode.InitGripper,
                    ProtocolCode.SET_FOUR_PIECES_ZERO
                ]:
                    return self._process_single(res)
                elif genre in [ProtocolCode.GET_ANGLES]:
                    return [self._int2angle(angle) for angle in res]
                elif genre in [ProtocolCode.GET_COORDS, ProtocolCode.GET_TOOL_REFERENCE,
                               ProtocolCode.GET_WORLD_REFERENCE]:
                    if res:
                        r = []
                        for idx in range(3):
                            r.append(self._int2coord(res[idx]))
                        for idx in range(3, 6):
                            r.append(self._int2angle(res[idx]))
                        return r
                    else:
                        return res
                elif genre in [ProtocolCode.GET_SERVO_VOLTAGES]:
                    return [self._int2coord(angle) for angle in res]
                elif genre in [ProtocolCode.GET_JOINT_MAX_ANGLE, ProtocolCode.GET_JOINT_MIN_ANGLE]:
                    return self._int2coord(res[0])
                elif genre in [ProtocolCode.GET_BASIC_VERSION, ProtocolCode.SOFTWARE_VERSION,
                               ProtocolCode.GET_ATOM_VERSION]:
                    return self._int2coord(self._process_single(res))
                elif genre == ProtocolCode.GET_ANGLES_COORDS:
                    r = []
                    for index in range(len(res)):
                        if index < 7:
                            r.append(self._int2angle(res[index]))
                        elif index < 10:
                            r.append(self._int2coord(res[index]))
                        else:
                            r.append(self._int2angle(res[index]))
                    return r
                elif genre == ProtocolCode.GET_SOLUTION_ANGLES:
                    return self._int2angle(res[0])
                else:
                    return res
            return None

    def get_robot_modified_version(self):
        """Get the bot correction version number

        Returns:
                version (int): the bot correction version number
        """
        return self._mesg(ProtocolCode.GET_ROBOT_MODIFIED_VERSION, has_reply=True)

    def get_robot_firmware_version(self):
        """Obtaining the Robot Firmware Version (Major and Minor Versions)

        Returns:
                version (int): the robot firmware
        """
        version = self._mesg(ProtocolCode.GET_ROBOT_FIRMWARE_VERSION, has_reply=True)
        return version

    def get_robot_auxiliary_firmware_version(self):
        """Obtaining the Robot Auxiliary Control Firmware Version (PICO)"""
        return self._mesg(ProtocolCode.GET_ROBOT_AUXILIARY_FIRMWARE_VERSION, has_reply=True)

    def get_robot_atom_modified_version(self):
        """Get the remediation version of the bot tool"""
        return self._mesg(ProtocolCode.GET_ROBOT_ATOM_MODIFIED_VERSION, has_reply=True)

    def get_robot_tool_firmware_version(self):
        """Get the Robot Tool Firmware Version (End Atom)"""
        return self._mesg(ProtocolCode.GET_ROBOT_TOOL_FIRMWARE_VERSION, has_reply=True)

    def get_robot_serial_number(self):
        """Get the bot number"""
        return self._mesg(ProtocolCode.GET_ROBOT_SERIAL_NUMBER, has_reply=True)

    def set_robot_err_check_state(self, status):  # !!!!
        """Set Error Detection Status You can turn off error detection, but do not turn it off unless necessary

        Args:
            status (int): 1 open; o close

        Returns:
            status (int): 1 open; o close. default 1
        """
        return self._mesg(ProtocolCode.SET_ROBOT_ERROR_CHECK_STATE, status, has_reply=True)

    def get_robot_err_check_state(self):
        """Read error detection status"""
        return self._mesg(ProtocolCode.GET_ROBOT_ERROR_CHECK_STATE, has_reply=True)

    def get_robot_error_status(self):
        """Get the bot error status

        Returns:

        """
        return self._mesg(ProtocolCode.GET_ROBOT_ERROR_STATUS, has_reply=True)

    def get_robot_power_status(self):
        """Get the robot power status
        Returns:
            power_status (int): 0: power on, 1: power off
        """
        return self._mesg(ProtocolCode.IS_POWER_ON, has_reply=True)

    def set_robot_power_on(self):
        """Set the robot to power on

        Returns: (int) 1
        """
        return self._mesg(ProtocolCode.POWER_ON, has_reply=True)

    def set_robot_power_off(self):
        """Set the robot to power off

        Returns: (int) 1
        """
        return self._mesg(ProtocolCode.POWER_OFF, has_reply=True)

    def clear_robot_err(self):
        """Clear the robot abnormality Ignore the error joint and continue to move"""
        self._mesg(ProtocolCode.SET_FRESH_MODE)

    def get_joint_current_angle(self, joint_id):
        """
        Gets the current angle of the specified joint
        Args:
            joint_id (int): 0 - 254

        Returns:

        """
        return self._mesg(ProtocolCode.COBOTX_GET_ANGLE, joint_id, has_reply=True)

    def set_joint_angle(self, joint_id, angle, speed):
        """Sets the individual joints to move to the target angle

        Args:
            joint_id (int) : 0 - 254
            angle (int) : 0 - 254
            speed (int) : 1 - 100
        """
        self._mesg(ProtocolCode.SEND_ANGLE, joint_id, [self._angle2int(angle)], speed)

    def get_joint_current_angles(self):
        """Gets the current angle of all joints

        Returns:

        """
        return self._mesg(ProtocolCode.GET_ANGLES, has_reply=True)

    def set_joint_angles(self, angles, speed):
        """Sets all joints to move to the target angle

        Args:
            angles (list[int]):  0 - 254
            speed (int): 0 - 100
        """
        angles = list(map(self._angle2int, angles))
        return self._mesg(ProtocolCode.SEND_ANGLES, angles, speed)

    def is_robot_moving(self):
        """See if the robot is moving

        Returns:
            1: moving
            0: not moving
        """
        return self._mesg(ProtocolCode.IS_MOVING, has_reply=True)

    def stop_robot(self):
        """The robot stops moving"""
        self._mesg(ProtocolCode.STOP)

    # def is_in_position(self):
    #     """Whether the robot has reached the specified point
    #     Returns:
    #
    #     """
    #     return self._mesg(ProtocolCode.IS_IN_POSITION, reply=True)

    def get_joints_max(self):
        """Read the maximum angle of all joints"""
        return self._mesg(ProtocolCode.GET_JOINT_MAX_ANGLE, has_reply=True)

    def get_joints_min(self):
        """Read the minimum angle of all joints"""
        return self._mesg(ProtocolCode.GET_JOINT_MIN_ANGLE, has_reply=True)

    def set_single_servo_motor_callibrate(self, servo_id):
        """Sets the zero position of the specified servo motor

        Args:
            servo_id (int): 0 - 254
        """

        self._mesg(ProtocolCode.SET_SERVO_CALIBRATION, servo_id)

    def get_single_servo_motor_current_encoder(self, servo_id):
        """Gets the current encoder potential value for the specified servo motor

        Args:
            servo_id:servo_id (int): 0 - 254
        """
        return self._mesg(ProtocolCode.GET_ENCODERS, servo_id, has_reply=True)

    def set_single_servo_motor_encoder(self, servo_id, position, speed):
        """Sets the individual motor motion to the target encoder potential value

        Args:
            servo_id: (int) 0 - 254
            position: (int) 0 - 4095
            speed: (int) 1 - 100

        """
        return self._mesg(ProtocolCode.SET_ENCODER, servo_id, position, speed)

    def get_multiple_servo_motor_current_encoders(self):
        """Obtain the current encoder potential values for multiple servo motors"""
        return self._mesg(ProtocolCode.GET_ENCODER, has_reply=True)

    def set_multiple_servo_motor_encoders(self, positions, speed):
        """Set the encoder potential value for multiple motors moving to the target

        Args:
            positions (list[int]): 0 - 4095:
            speed (int): 1 - 100:
        """
        self._mesg(ProtocolCode.SET_ENCODERS, positions, speed)

    def get_single_servo_motor_current_speed(self):
        """Gets the current movement speed of multiple servo motors"""
        return self._mesg(ProtocolCode.GET_SERVO_SPEED, has_reply=True)

    def set_encoders_drag(self, encoders, speeds):
        """Set multiple servo motors with a specified speed to the target encoder potential value"""
        self.calibration_parameters(class_name=self.__class__.__name__, encoders=encoders, speeds=speeds)
        self._mesg(ProtocolCode.SET_ENCODERS_DRAG, encoders, speeds)

    def is_all_servo_enabled(self):
        """Get the connection status of multiple servo motors"""
        return self._mesg(ProtocolCode.IS_ALL_SERVO_ENABLE, has_reply=True)

    def get_single_servo_motor_current_T(self):
        """Obtain the temperature of multiple servo motors"""
        return self._mesg(ProtocolCode.GET_SERVO_TEMPS, has_reply=True)

    def get_single_servo_motor_current_V(self):
        """Get the voltage of multiple servo motors"""
        return self._mesg(ProtocolCode.GET_SERVO_VOLTAGES, has_reply=True)

    def get_single_servo_motor_current_I(self):
        """Obtain the current of multiple servo motors"""
        return self._mesg(ProtocolCode.GET_SERVO_CURRENTS, has_reply=True)

    def get_single_servo_motor_all_status(self):
        """Get all the statuses of multiple servo motors"""
        return self._mesg(ProtocolCode.GET_SERVO_STATUS, has_reply=True)

    def get_single_servo_protect_current(self):
        """Obtain multiple servo motor protection currents"""
        return self._mesg(ProtocolCode.GET_SERVO_LASTPDI, has_reply=True)

    def set_servo_motor_torque_switch(self, joint_id, torque_enable):
        """Set the servo motor torque switch

        Args:
            joint_id (int): 0-254 254-all
            torque_enable: 0/1
                1-focus
                0-release
        """
        self._mesg(ProtocolCode.RELEASE_ALL_SERVOS, joint_id, torque_enable)

    def set_single_servo_motor_p(self, servo_id, data):
        """Sets the proportionality factor of the position loop P of the specified servo motor

        Args:
            servo_id (int): 0-254
            data (int): 0-254

        """
        self._mesg(ProtocolCode.MERCURY_DRAG_TECH_SAVE, servo_id, data)

    def get_single_servo_motor_p(self, servo_id):
        """Reads the position loop P scale factor of the specified servo motor

        Args:
            servo_id (int): 0-254
        """
        self._mesg(ProtocolCode.SERVO_RESTORE, servo_id)

    def set_single_servo_motor_d(self, servo_id, data):
        """Sets the proportional factor for the position ring D of the specified servo motor

        Args:
            servo_id (int): 0-254
            data (int): 0-254
        """
        self._mesg(ProtocolCode.MERCURY_DRAG_TECH_EXECUTE, servo_id, data, has_reply=True)

    def get_single_servo_motor_d(self, servo_id):
        """Reads the position ring D scale factor for the specified servo motor

        Args:
            servo_id (int): 0-254
        """
        return self._mesg(ProtocolCode.SET_ERROR_DETECT_MODE, servo_id, has_reply=True)

    def set_single_servo_motor_i(self, servo_id, data):
        """Set the proportional factor of the position ring I of the specified servo motor

        Args:
            servo_id:
            data:
        """
        return self._mesg(ProtocolCode.MERCURY_DRAG_TEACH_CLEAN, servo_id, data)

    def get_single_servo_motor_i(self, servo_id):
        """Reads the position loop I scale factor of the specified servo motor"""
        return self._mesg(ProtocolCode.GET_ERROR_DETECT_MODE, servo_id, has_reply=True)

    def set_single_servo_clockwise(self, servo_id, data):
        """Sets the clockwise insensitivity zone of the encoder for the specified servo motor"""
        self._mesg(ProtocolCode.SET_SERVO_MOTOR_CLOCKWISE, servo_id, data)

    def get_single_servo_clockwise(self, servo_id):
        """Reads the clockwise insensitive area of the encoder for the specified servo motor"""
        return self._mesg(ProtocolCode.GET_SERVO_MOTOR_CLOCKWISE, servo_id, has_reply=True)

    def set_single_servo_counter_clockwise(self, servo_id, data):
        """Sets the counterclockwise insensitive zone of the encoder for the specified servo motor"""
        return self._mesg(ProtocolCode.SET_SERVO_MOTOR_COUNTER_CLOCKWISE, servo_id, data, has_reply=True)

    def get_single_servo_counter_clockwise(self, servo_id):
        """Reads the counterclockwise insensitive area of the encoder of the specified servo motor"""
        return self._mesg(ProtocolCode.GET_SERVO_MOTOR_COUNTER_CLOCKWISE, servo_id, has_reply=True)

    def set_single_servo_config_data(self, servo_id, addr, mode, data):
        """Set the system parameters for the specified servo motor"""
        self._mesg(ProtocolCode.SET_SERVO_MOTOR_CONFIG, servo_id, addr, mode, data, has_reply=True)

    def get_single_servo_config_data(self, servo_id, addr, data):
        """Read the system parameters of the specified servo motor"""
        return self._mesg(ProtocolCode.GET_SERVO_MOTOR_CONFIG, servo_id, addr, data, has_reply=True)

    def set_master_pin_status(self, io_number, status=1):
        """Set the host I/O pin status

        Args:
            io_number: 1/2
            status: 0/1; 0: low; 1: high. default: 1

        """
        self._mesg(ProtocolCode.SET_MASTER_PIN_STATUS, io_number, status)

    def get_master_pin_status(self, io_number):
        """get the host I/O pin status

        Args:
            io_number: pin number

        Returns:
                0 or 1. 1: high 0: low
        """
        return self._mesg(ProtocolCode.GET_MASTER_PIN_STATUS, io_number, has_reply=True)

    def set_auxiliary_pin_status(self, io_number, status=1):
        """Set the auxiliary pin status

        Args:
            io_number: 1/2
            status: 0/1; 0: low; 1: high. default: 1

        """
        self._mesg(ProtocolCode.SET_AUXILIARY_PIN_STATUS, io_number, status)

    def get_auxiliary_pin_status(self, io_number):
        """Get the auxiliary pin status

        Args:
            io_number (int): pin number

        Returns:
            0 or 1. 1: high 0: low

        """
        return self._mesg(ProtocolCode.GET_AUXILIARY_PIN_STATUS, io_number, has_reply=True)

    def set_atom_pin_status(self, io_number, status=1):
        """Set the Atom pin status

        Args:
            io_number (int): pin number
            status: 0 or 1; 0: low; 1: high. default: 1

        """
        self._mesg(ProtocolCode.SET_ATOM_PIN_STATUS, io_number, status)

    def get_atom_pin_status(self, io_number):
        """Get the Atom pin status

        Args:
            io_number (int): pin number

        Returns:
            0 or 1. 1: high 0: low

        """
        return self._mesg(ProtocolCode.GET_ATOM_PIN_STATUS, io_number, has_reply=True)

    def set_atom_led_color(self, r, g, b):
        """Set the Atom LED color

        Args:
            r: 0-255
            g: 0-255
            b: 0-255

        """
        self._mesg(ProtocolCode.GET_ATOM_LED_COLOR, r, g, b)

    def get_atom_press_status(self):
        """read the atom press status

        Returns:
            int: 0 or 1. 1: press

        """
        return self._mesg(ProtocolCode.GET_ATOM_PRESS_STATUS, has_reply=True)
