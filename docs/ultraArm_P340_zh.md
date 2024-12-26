# API 方法详细说明

**在使用下列函数接口的时候请先在开头导入我们的API库，否则无法运行成功，即输入以下代码：**

```python
from pymycobot.ultraArm import ultraArm
```

**注意：** 若没有安装我们的API库，请参考 [README.md](../README.md) 文档进行安装。

## 1 机械臂整体运行状态

**1.1** `go_zero()`

- **功能：** 机械臂回零。
- **返回值：** 无

**1.2** `power_on()`

- **功能：** 机械臂所有关节上电。
- **返回值：** 无

**1.3** `release_all_servos()`	   

- **功能：** 机械臂所有关节掉电
- **返回值：** 无

**1.4** `is_moving_end()`

- **功能：** 机械臂运动结束标志
- **返回值：** 
  - `1`: 运动结束
  - `0`: 运动未结束

**1.5** `set_system_value(id, address, value)`

- **功能：** 设置系统参数
- **参数说明：**
  - `id`: `int`, 电机ID，4 或者 7
  - `address`: `int`, 参数寄存器地址，0 ~ 69
  - `value`: `int`, 对应寄存器参数取值
- **返回值：**  无

**1.6** `get_system_value(id, address)`

- **功能：** 读取系统参数
- **参数说明：**
  - `id`: `int`, 电机ID，4 或者 7
  - `address`: `int`, 参数寄存器地址，0 ~ 69
- **返回值：** `int`, 对应寄存器参数取值

## 2 输入程序控制模式（MDI模式）

  > 注意：不同系列的机械臂限位有所不同，可设定姿态数值也有所不同具体可查看对应型号的参数介绍

**2.1** `get_angles_info()`

- **功能：** 获取机械臂当前角度。
- **返回值：** `list`一个浮点值的列表，表示所有关节的角度.

**2.2** `set_angle(id, degree, speed)`

- **功能：** 发送指定的单个关节运动至指定的角度
- **参数说明：**
  - `id`: 代表机械臂的关节，三轴有三个关节，可以用数字1-3来表示。
  - `degree`: 表示关节的角度
  
      <table>
        <tr>
            <th>关节 Id</th>
            <th>范围</th>
        </tr>
        <tr>
            <td text-align: center>1</td>
            <td>-150 ~ 170</td>
        </tr>
        <tr>
            <td>2</td>
            <td>-20 ~ 90</td>
        </tr>
        <tr>
            <td>3</td>
            <td>-5 ~ 110</td>
        </tr>
        <tr>
            <td>4（配件）</td>
            <td> -179 ~ 179</td>
        </tr>

    </table>

  - `speed`：表示机械臂运动的速度，范围0~200 (单位：mm/s)。
- **返回值：** 无

**2.3** `set_angles(degrees, speed)`

- **功能：**  发送所有角度给机械臂所有关节
- **参数说明：**
  - `degrees`: (List[float])包含所有关节的角度 ,三轴机器人有三个关节，所以长度为3，表示方法为：[20,20,20]
  - `speed`: 表示机械臂运动的速度，取值范围是0~200 (单位：mm/s)。
- **返回值：** 无

**2.4** `get_coords_info()`

- **功能：** 获取机械臂当前坐标。
- **返回值：** `list`包含坐标的列表, `θ` 为末端的旋转角
  - 三轴：长度为 4，依次为 `[x, y, z, θ]`


**2.5** `send_coord(id,coord,speed)`

- **功能：** 发送单个坐标值给机械臂进行移动
- **参数说明：**
  - `id`:代表机械臂的坐标，三轴有三个坐标，有特定的表示方法。
    X坐标的表示法：`"X"或者"x"`.
  - `coord`: 输入您想要到达的坐标值
  
      <table>
        <tr>
            <th>坐标 Id</th>
            <th>范围</th>
        </tr>
        <tr>
            <td text-align: center>x</td>
            <td>-360 ~ 365.55</td>
        </tr>
        <tr>
            <td>y</td>
            <td>-365.55 ~ 365.55</td>
        </tr>
        <tr>
            <td>z</td>
            <td>-140 ~ 130</td>
        </tr>

      </table>

  - `speed`: 表示机械臂运动的速度，范围是0-200 (单位：mm/s)。
- **返回值：** 无

**2.6** `set_coords(coords, speed)`

- **功能：** 发送整体坐标,让机械臂头部从原来点移动到您指定点。
- **参数说明：**
  - `coords`: 
    - 三轴：[x,y,z] 的坐标值，长度为3
  - `speed`: 表示机械臂运动的速度，范围是0-200 (单位：mm/s)。
- **返回值：** 无

**2.7** `get_radians_info()`

- **功能：** 获取机械臂当前弧度值。
- **返回值：** `list`包含所有关节弧度值的列表.

**2.8** `set_radians(radians, speed)`

- **功能：** 发送弧度值给机械臂所有关节
- **参数说明：**
  - `radians`: 每个关节的弧度值列表( `List[float]`)
  
      <table>
        <tr>
            <th>关节 Id</th>
            <th>范围</th>
        </tr>
        <tr>
            <td text-align: center>1</td>
            <td>2.6179 ~ 2.9670</td>
        </tr>
        <tr>
            <td>2</td>
            <td>-0.3490 ~ 1.5707</td>
        </tr>
        <tr>
            <td>3</td>
            <td>-0.0872 ~ 1.9198</td>
        </tr>
        <tr>
            <td>4（配件）</td>
            <td> -3.1241 ~ + 3.1241</td>
        </tr>
      </table>

  - `speed`: 表示机械臂运动的速度，范围是0-200 (单位：mm/s)。
- **返回值：** 无

**2.9** `set_mode()`

- **功能：** 设置坐标模式
- **参数说明：**
  - `0`:绝对笛卡尔模式。
  - `1`:相对笛卡尔模式。
- **返回值：** 无

**2.10** `sleep()`

- **功能：** 延迟
- **参数说明：**
  - `Time`: 延迟的时间( `Int`类型)，
- **返回值：** 无

**2.12** `set_init_pose()`		

- **功能：** 设置当前位置为某个固定位置。如（0,0,0）就把这个位置设为零点
- **参数说明：**
  - `coords`: 机械臂所有坐标
  - `speed`: 表示机械臂运动的速度，范围是0-200 (单位：mm/s)。
- **返回值：** 无

**2.13** `set_pwm()`			 

- **功能：** 设置PWM占空比
- **参数说明：** P：占空比，范围：0-255
- **返回值：** 无

**2.14** `set_fan_state()`

- **功能：** 设置风扇状态
- **参数说明：** 
  - `0`: close
  - `1`: open
- **返回值：** 无


**2.15** `get_switch_state()`

- **功能：** 获取限位开关状态
- **参数说明：** 
  - `X`：关节三是否到达限位
  - `Y`：关节二是否到达限位
  - `Z`：关节一是否到达限位
- **返回值：** 有


**2.16** `set_speed_mode(mode)`

- **功能：** 设置速度模式
- **参数说明：** 
  - `0`: 匀速模式
  - `2`: 加减速模式
- **返回值：** 无



## 3  JOG 模式和操作

**3.1** `set_jog_angle(id, direction, speed)`

- **功能：** 设置点动模式（角度）
- **参数说明：**
  - `id`: 代表机械臂的关节，按照关节id给入1~3来表示
  - `direction`: 主要控制机器臂移动的方向，给入0 为负值移动，给入1为正值移动
  - `speed`: 速度 0 ~ 200 (单位：mm/s)。
- **返回值：** 无

**3.2** `set_jog_coord(axis, direction, speed)`

- **功能：** 控制机器人按照指定的坐标或姿态值持续移动
- **参数说明：**
  - `axis`: 代表机械臂的关节，按照关节axis给入x/y/z来表示
  - `direction`: 主要控制机器臂移动的方向，给入0 为负值移动，给入1为正值移动
  - `speed`: 速度 0 ~ 200 (单位：mm/s)。
- **返回值：** 无

**3.3** `set_jog_stop()`

- **功能：** 停止 jog 控制下的持续移动
- **返回值：** 无



## 4 IO控制

**4.1** `set_gpio_state(state)`

- **功能：** 设置 吸泵状态。
- **参数说明：**
  - `state` (int)：输入0表示开启吸泵，输入1表示关闭吸泵。
- **返回值：** 无

**4.2** `set_gripper_zero()`

- **功能：** 设置夹爪零位（设置当前位置为零位）。
- **返回值：** 无

**4.3** `set_gripper_state(state):`

- **功能：** 设置夹爪开关
- **参数说明:** `state`：输入0表示张开夹爪，输入1表示闭合夹爪。
- **返回值：** 无

**4.4** `get_gripper_angle():`

- **功能：** 获取夹爪角度
- **返回值：** 夹爪角度值

## 5 功能接口

**5.1** `play_gcode_file(filename)`

- **功能：** 播放导入的轨迹文件。
- **参数说明：**
  - `filename` ：轨迹文件名称
- **返回值：** 无


## 6 使用案例

```bash
import time
import platform
from pymycobot.ultraArm import ultraArm

# 自动选择系统并连接机械臂
if platform.system() == "Windows":
    ua = ultraArm('COM6', 115200)
    ua.go_zero()
elif platform.system() == "Linux":
    ua = ultraArm('/dev/ttyUSB0', 115200)
    ua.go_zero()
    
# 机械臂运动的位置
angles = [
    [-81.71, 0.0, 0.0],
    [-90.53, 21.77, 47.56],
    [-90.53, 0.0, 0.0],
    [-59.01, 21.77, 45.84],
    [-59.01, 0.0, 0.0]
]

# 吸取小物块
ua.set_angles(angles[0], 50)
time.sleep(3)
ua.set_angles(angles[1], 50)
time.sleep(3)

# 开启吸泵
ua.set_gpio_state(0)

ua.set_angles(angles[2], 50)
time.sleep(3)
ua.set_angles(angles[3], 50)

# 关闭吸泵
ua.set_gpio_state(1)
time.sleep(3)

ua.set_angles(angles[4], 50)
```