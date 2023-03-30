"""
Do fast reset: reset using MC native command `/kill`, instead of waiting for generating new worlds

Side effects:
    1. Changes to the world will not be reset. E.g., if the agent chops lots of trees then calling fast reset
        will not restore those trees.
    2. If you specify agent starting health and food, these specs will only be respected at the first reset
        (i.e., generating a new world) but will not be respected in the following resets (i.e., reset using MC cmds).
        So be careful to use this wrapper if your usages require specific initial health/food.
    3. Statistics/achievements will not be reset. This wrapper will maintain a property `info_prev_reset`. If your
        tasks use stat/achievements to evaluation, please retrieve this property and calculate differences
"""
from __future__ import annotations
from math import pi, sin, cos
from mimetypes import init
import random
import re

import gym

from ..sim import MineDojoSim
from ...sim.mc_meta.mc import MAX_FOOD, MAX_LIFE
from ..inventory import parse_inventory_item, map_slot_number_to_cmd_slot

# estimated slope of the world
TRANS_SLOPE = 0.5

class FastResetWrapper(gym.Wrapper):
    def __init__(
        self,
        env: MineDojoSim,
        random_teleport_range: int | None,
        # random_teleport_range --> ~_high & ~_low
        random_teleport_range_high: int | None,
        random_teleport_range_low: int | None,
        clear_ground: bool = True,
    ):
        super().__init__(env=env)
        self._move_flag = True
        start_time, start_weather = env.start_time, env.initial_weather
        initial_inventory, start_position = env.initial_inventory, env.start_position
        start_health, start_food = env.start_health, env.start_food
        if start_health != MAX_LIFE or start_food != MAX_FOOD:
            print(
                "Warning! You use non-default values for `start_health` and `start_food`. "
                "However, they will not take effects because `fast_reset = True`. "
                "Consider using `fast_reset = False` instead."
            )
        
        if random_teleport_range_high is None and random_teleport_range_low is None:
            self._move_flag = False

        if random_teleport_range_high is None:
            random_teleport_range_high = 20
        assert random_teleport_range_high >= 0

        if random_teleport_range_low is None:
            random_teleport_range_low = 0
        assert random_teleport_range_low >= 0

        assert random_teleport_range_high > random_teleport_range_low

        self.random_teleport_range_high = random_teleport_range_high
        self.random_teleport_range_low = random_teleport_range_low

        self.set_start_position =False
        self._reset_cmds = [
            "/kill",
        ]
        self._reset_cmds.extend(
            [f"/time set {start_time or 0}", f'/weather {start_weather or "normal"}']
        )
        if initial_inventory is not None:
            for inventory_item in initial_inventory:
                slot, item_dict = parse_inventory_item(inventory_item)
                self._reset_cmds.append(
                    f'/replaceitem entity @p {map_slot_number_to_cmd_slot(slot)} minecraft:{item_dict["type"]} {item_dict["quantity"]} {item_dict["metadata"]}'
                )

        self.init_position = None
        if start_position is not None:
            self._reset_cmds.append(
                f'/tp @p {start_position["x"]} {start_position["y"]} {start_position["z"]} {start_position["yaw"]} {start_position["pitch"]}'
            )
            self.set_start_position=True
            self.init_position = {"x":start_position['x'], "y":start_position['y'], "z":start_position['z']}
            
        if clear_ground:
            # kill all creatures
            self._reset_cmds.append("/kill @e[type=!player]")  
            self._reset_cmds.append("/kill @e[type=item]")

        self._server_start = False
        self._info_prev_reset = None
        self.birth_position = None

    def random_teleport(self, *args, **kwargs):
        return self.env.random_teleport(*args, **kwargs)

    # move_flag = True : reset and teleport the agent
    def reset(self, move_flag=True):
        if not self._move_flag:
            move_flag = False
        if not self._server_start:
            self._server_start = True
            return self.env.reset()
        else:
            for cmd in self._reset_cmds:
                # print(cmd)
                obs, _, _, info = self.env.execute_cmd(cmd)
                if self.init_position is None:
                    # self.init_position = {"x":info["xpos"], "y":info["ypos"], "z":info["zpos"]}
                    self.init_position = {"x":obs["location_stats"]["pos"][0], "y":obs["location_stats"]["pos"][2], "z":obs["location_stats"]["pos"][1]}
            
            if self.birth_position is not None:
                move_to_birth = f'/tp {self.birth_position["x"]} {self.birth_position["y"]} {self.birth_position["z"]} ~ ~'
                obs, _, _, info = self.env.execute_cmd(move_to_birth)
                

            # teleport a random distance away from the birth place
            if (self.random_teleport_range_high > 0) and move_flag:
                rel_dis = random.uniform(self.random_teleport_range_low,self.random_teleport_range_high)

                teleport = f"/spreadplayers {int(self.init_position['x'])} {int(self.init_position['y'])} {rel_dis} {rel_dis+1} false @p"
                obs, _, _, info = self.env.execute_cmd(teleport)

                leaves_teleport = f"/execute @p ~ ~ ~ execute @p ~ ~ ~ detect ~ ~-1 ~ minecraft:leaves -1 spreadplayers {int(self.init_position['x'])} {int(self.init_position['y'])} {rel_dis} {rel_dis+1} false @p"
                times = 20
                for _ in range(times):
                    obs, _, _, info = self.env.execute_cmd(leaves_teleport)

                # self.birth_position = {"x":info["xpos"], "y":info["ypos"], "z":info["zpos"]}
                self.birth_position = {"x":obs["location_stats"]["pos"][0], "y":obs["location_stats"]["pos"][1], "z":obs["location_stats"]["pos"][2]}
                # print(info.keys())

            return obs

    def execute_cmd(self, *args, **kwargs):
        return self.env.execute_cmd(*args, **kwargs)

    def spawn_mobs(self, *args, **kwargs):
        return self.env.spawn_mobs(*args, **kwargs)

    def set_block(self, *args, **kwargs):
        return self.env.set_block(*args, **kwargs)

    def clear_inventory(self, *args, **kwargs):
        return self.env.clear_inventory(*args, **kwargs)

    def set_inventory(self, *args, **kwargs):
        return self.env.set_inventory(*args, **kwargs)

    def teleport_agent(self, *args, **kwargs):
        return self.env.teleport_agent(*args, **kwargs)

    def kill_agent(self, *args, **kwargs):
        return self.env.kill_agent(*args, **kwargs)

    def set_time(self, *args, **kwargs):
        return self.env.set_time(*args, **kwargs)

    def set_weather(self, *args, **kwargs):
        return self.env.set_weather(*args, **kwargs)


    @property
    def prev_obs(self):
        return self.env.prev_obs

    @property
    def prev_info(self):
        return self.env.prev_info

    @property
    def info_prev_reset(self):
        return self._info_prev_reset

    @property
    def prev_action(self):
        return self.env.prev_action

    @property
    def is_terminated(self):
        return self.env.is_terminated