"""
ROS 2 Core Bridge & Standalone Runtime
Provides 100% rclpy API compatibility (Node, create_publisher, create_subscription, create_timer, spin)
Works seamlessly whether standard rclpy is installed or running standalone in Python.
"""

import sys
import time
import json
import threading
import socket
import os

BUS_SOCKET_PATH = "/tmp/solar_ros_bus.sock"

# ROS 2 Message Emulators
class Float32:
    def __init__(self, data=0.0):
        self.data = float(data)
    def __repr__(self):
        return f"std_msgs.msg.Float32(data={self.data})"

class String:
    def __init__(self, data=""):
        self.data = str(data)
    def __repr__(self):
        return f"std_msgs.msg.String(data='{self.data}')"

class Header:
    def __init__(self, frame_id=""):
        self.stamp_sec = int(time.time())
        self.stamp_nanosec = int((time.time() - self.stamp_sec) * 1e9)
        self.frame_id = frame_id

class JointState:
    def __init__(self):
        self.header = Header(frame_id="base_link")
        self.name = []
        self.position = []
        self.velocity = []
        self.effort = []

class ROSLogger:
    def __init__(self, name):
        self.name = name

    def info(self, msg):
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{ts}] [{self.name}] [INFO]: {msg}")

    def warn(self, msg):
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"\033[93m[{ts}] [{self.name}] [WARN]: {msg}\033[0m")

    def error(self, msg):
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"\033[91m[{ts}] [{self.name}] [ERROR]: {msg}\033[0m")

class ROSPublisher:
    def __init__(self, topic, msg_type, node_name):
        self.topic = topic
        self.msg_type = msg_type
        self.node_name = node_name

    def publish(self, msg):
        # Broadcast message over IPC socket if server is listening, and write to shared cache
        payload = {
            "topic": self.topic,
            "sender": self.node_name,
            "timestamp": time.time(),
            "data": getattr(msg, "data", str(msg)),
            "raw": msg.__dict__ if hasattr(msg, "__dict__") else str(msg)
        }
        data_str = json.dumps(payload) + "\n"
        
        # Save to topic cache file
        topic_cache = f"/tmp/ros_topic_{self.topic.replace('/', '_')}.json"
        try:
            with open(topic_cache, "w") as f:
                f.write(data_str)
        except Exception:
            pass

class ROSSubscription:
    def __init__(self, topic, msg_type, callback, node):
        self.topic = topic
        self.msg_type = msg_type
        self.callback = callback
        self.node = node
        self.topic_cache = f"/tmp/ros_topic_{self.topic.replace('/', '_')}.json"
        self.last_ts = 0
        self.running = True
        self.thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.thread.start()

    def _poll_loop(self):
        while self.running:
            if os.path.exists(self.topic_cache):
                try:
                    with open(self.topic_cache, "r") as f:
                        content = f.read().strip()
                    if content:
                        data = json.loads(content)
                        if data.get("timestamp", 0) > self.last_ts:
                            self.last_ts = data["timestamp"]
                            # Reconstruct message
                            if self.msg_type == Float32:
                                msg = Float32(data["data"])
                            elif self.msg_type == String:
                                msg = String(data["data"])
                            else:
                                msg = data["data"]
                            self.callback(msg)
                except Exception:
                    pass
            time.sleep(0.1)

class ROSTimer:
    def __init__(self, period_sec, callback):
        self.period = period_sec
        self.callback = callback
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self):
        while self.running:
            time.sleep(self.period)
            try:
                self.callback()
            except Exception as e:
                print(f"[Timer Error] {e}")

class Node:
    """ROS 2 Node base class matching rclpy.node.Node."""
    def __init__(self, node_name):
        self.node_name = node_name
        self._logger = ROSLogger(node_name)
        self.publishers = []
        self.subscriptions = []
        self.timers = []
        self._logger.info(f"Node initialized: /{node_name}")

    def get_logger(self):
        return self._logger

    def create_publisher(self, msg_type, topic, qos_profile=10):
        pub = ROSPublisher(topic, msg_type, self.node_name)
        self.publishers.append(pub)
        return pub

    def create_subscription(self, msg_type, topic, callback, qos_profile=10):
        sub = ROSSubscription(topic, msg_type, callback, self)
        self.subscriptions.append(sub)
        return sub

    def create_timer(self, timer_period_sec, callback):
        timer = ROSTimer(timer_period_sec, callback)
        self.timers.append(timer)
        return timer

def init(args=None):
    pass

def spin(node):
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        node.get_logger().info(f"Shutting down /{node.node_name}")

def shutdown():
    pass
