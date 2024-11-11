import uuid
import numpy as np
from src.geometry.lanes import Lane
from typing import List
import logging


# create Vehicle class for simulation
class Vehicle:
    def __init__(self, config={}):
        # set default config
        self.set_default_config()

        # update config
        self.update_config(config)

        self.lead = None
        self.follow = None
        self.present_a = None

        self.dt = 1 / 60
        self.t = 0
        self.lc_unlock_t = 0
        # 连续换道的最小时间间隔
        self.lc_gap = 3

        # 定义礼貌因子politeness factor，用于权衡自身优势和对他人的影响
        # 这个值可以根据需要调整，0表示完全自私，1表示完全利他
        self.politeness = 0.5

        # 通过连接器进入下一个路段的lane_id
        self.to_lane = None

    def set_default_config(self):
        self.id = uuid.uuid4()

        # minimal safe distance
        self.s0 = 4

        # reaction time
        self.T = 1

        self.length = 5.3
        self.v_max = 15
        self._v_max = 15

        self.a_max = 1.5
        self.b_max = 9

        self.path = []
        self.current_road_index = 0
        self.at_lane = None

        self.x = 0
        self.v = 0
        self.a = 0

        # possible status change due to traffic lights
        self.stopped = False
        self.slowing_down = False

        self.sqrt_ab = 2 * np.sqrt(self.a_max * self.b_max)

        # inner lane index
        self.at_lane = 0

        # 安全刹车减速度
        self.b_safe = 4

    # update config with new  values
    def update_config(self, config):
        for key, value in config.items():
            setattr(self, key, value)

    # use IDM model to update speed, position and acceleration
    def IDM(self, lead, dt):
        # Update position and velocity
        # if self.v +self.a * dt < 0:
        #     self.x -= 0.5*self.v**2 / self.a
        #     self.v = 0
        # else:
        #     self.v += self.a * dt
        #     self.x += self.v * dt + self.a*dt**2 / 2

        # Update acceleration
        alpha = 0
        if lead:
            delta_x = lead.x - self.x - lead.length
            delta_v = self.v - lead.v

            alpha = (self.s0 + max(0, self.T * self.v + delta_v * self.v / self.sqrt_ab)) / delta_x

        a = self.a_max * (1 - (self.v / self.v_max) ** 4 - alpha ** 2)

        if self.stopped:
            a = -self.b_max * self.v / self.v_max

        return a

    def update_position_and_velocity(self):
        if self.v + self.a * self.dt < 0:
            self.x -= 0.5 * self.v ** 2 / self.a
            self.v = 0
        else:
            self.v += self.a * self.dt
            self.x += self.v * self.dt + self.a * self.dt ** 2 / 2
        self.t += self.dt

    def evaluate_and_perform_lane_change(self, lanes: List[Lane]):
        """
        Evaluate whether it is safe to change lane
        :param present_a: latent acceleration of ego_car if no lane change
        :param lanes: [self_lane, left_lane, right_lane] when has both, [sekf_lane, None, right_lane] when only right_lane and vice versa
        :return:
        """
        # 拿到换道锁的前提下才允许换道：
        if self.lc_lock:
            # 左右车道都存在
            if lanes[1] and lanes[2]:
                left_incentive, l_leader, l_follower, target_a_l = self.calculate_incentive(lanes[1])
                right_incentive, r_leader, r_follower, target_a_r = self.calculate_incentive(lanes[2])

                if left_incentive > right_incentive and left_incentive > 0:
                    self.implement_lane_change(lanes[0], lanes[1], l_leader, l_follower)

                    # print(self.id, "now:", self.t, "lc_unlock_t:", self.lc_unlock_t)
                    # if l_leader and l_leader.x - self.x < 2.5:
                    # print("close lc crash hazard:", self.id, "left", l_leader.id, self.x, l_leader.x, l_follower.x, left_incentive, target_a_l)
                    return target_a_l
                elif right_incentive > left_incentive and right_incentive > 0.2:  # Add bias to right side
                    self.implement_lane_change(lanes[0], lanes[2], r_leader, r_follower)
                    return target_a_r
                else:
                    return self.present_a
            # 仅存在左侧车道
            elif lanes[1]:
                left_incentive, l_leader, l_follower, target_a_l = self.calculate_incentive(lanes[1])
                if left_incentive > 0:
                    self.implement_lane_change(lanes[0], lanes[1], l_leader, l_follower)
                    return target_a_l
                else:
                    return self.present_a
            # 仅存在右侧车道
            elif lanes[2]:
                right_incentive, r_leader, r_follower, target_a_r = self.calculate_incentive(lanes[2])
                if right_incentive > 0.2:  # Add bias to right side
                    self.implement_lane_change(lanes[0], lanes[2], r_leader, r_follower)
                    return target_a_r
                else:
                    return self.present_a
            else:
                return self.present_a
        else:
            # print("lc_refused")
            return self.present_a

    def implement_lane_change(self, present_lane: Lane, target_lane: Lane, target_lead, target_follow):
        """
        修改目标lane链表：将ego_car插入并更新链表状态
        :param present_lane: lane where vehicle is currently on
        :param target_lane: lane where vehicle wants to go
        :param target_lead: lead vehicle of target_lane after moving into
        :param target_follow: follow vehicle of target_lane after moving into
        """
        logging.info("IMPLEMENT LC: %s, %s TO %s, POS: %s" % (self.id, present_lane.lane_id, target_lane.lane_id, self.x))
        present_lane.remove_vehicle(self)
        insert_loc = 0
        if target_lead:
            target_lead.follow = self
            self.lead = target_lead
            insert_loc = target_lead.location_in_lane + 1
        if target_follow:
            target_follow.lead = self
            self.follow = target_follow
        target_lane.vehicles.insert(insert_loc, self)
        self.at_lane = target_lane.lane_index
        self.lc_unlock_t = self.t + self.lc_gap


    def search_adjacent_lane(self, target_lane: Lane):
        """
        Use bisection search to identify lead and follow vehicle of adjacent lane
        :param target_lane: where vehicle wants to go
        :return: lead and follow vehicle of target_lane
        """
        if target_lane.vehicles:
            if target_lane.vehicles[0].x > self.x > target_lane.vehicles[-1].x:
                lead_id = 0
                follow_id = len(target_lane.vehicles) - 1
                while follow_id - lead_id > 1:
                    i = (lead_id + follow_id) // 2
                    if target_lane.vehicles[i].x >= self.x:
                        lead_id = i
                    else:
                        follow_id = i
                return target_lane.vehicles[lead_id], target_lane.vehicles[follow_id]
            elif target_lane.vehicles[0].x < self.x:
                return None, target_lane.vehicles[0]
            elif target_lane.vehicles[-1].x > self.x:
                return target_lane.vehicles[-1], None
            else:
                return None, None
        else:
            return None, None

    def calculate_incentive(self, target_lane: Lane):
        # 假设target_vehicle是目标车道上当前车辆前方的车辆
        # 计算换道后可能的加速度
        target_leader, target_follower = self.search_adjacent_lane(target_lane)
        if target_leader and target_follower:
            if target_leader.x - self.x < self.length+2 or self.x-target_follower.x < self.length+2:
                return -1000, target_leader, target_follower, 0
            target_a = self.IDM(target_leader, self.dt)  # 目标车道的加速度
            follow_a_latent = target_follower.IDM(self, self.dt)  # 换道后目标车道后车的加速度
            if follow_a_latent <= -4:
                follow_a_latent = -100
            follow_a = target_follower.IDM(target_leader, self.dt)  # 不换道目标车道后车的加速度

            # 计算换道后的自身优势（换道后的加速度 - 换道前的加速度）
            self_advantage = target_a - self.present_a
            # 计算对目标车道后方车辆的不利影响
            # 假设target_vehicle的后车是目标车道上换道后紧随当前车辆的车辆
            follower_disadvantage = follow_a_latent - follow_a
        elif target_leader and not target_follower:
            if target_leader.x - self.x < self.length+2:
                return -1000, target_leader, target_follower, 0
            target_a = self.IDM(target_leader, self.dt)  # 目标车道的加速度
            # 计算换道后的自身优势（换道后的加速度 - 换道前的加速度
            self_advantage = target_a - self.present_a
            # 计算对目标车道后方车辆的不利影响
            # 假设target_vehicle的后车是目标车道上换道后紧随当前车辆的车辆
            follow_a_latent = 0
            follower_disadvantage = 0
        elif not target_leader and target_follower:
            if self.x-target_follower.x < self.length+2:
                return -1000, target_leader, target_follower, 0
            target_a = self.IDM(None, self.dt)  # 目标车道的加速度
            follow_a_latent = target_follower.IDM(self, self.dt)  # 换道后目标车道后车的加速度
            follow_a = target_follower.IDM(target_leader, self.dt)  # 不换道目标车道后车的加速度
            if follow_a_latent <= -4:
                follow_a_latent = -100

            self_advantage = target_a - self.present_a
            follower_disadvantage = follow_a_latent - follow_a
        else:
            target_a = self.IDM(None, self.dt)  # 目标车道的加速度
            follow_a_latent = 0
            follower_disadvantage = 0
            self_advantage = target_a - self.present_a

        # 计算激励标准
        # 如果自身优势大于礼貌因子乘以对后方车辆的不利影响，则激励换道
        incentive = self_advantage - self.politeness * follower_disadvantage - 0.2
        if follow_a_latent <= -4:
            incentive = -1000

        return incentive, target_leader, target_follower, target_a

    @property
    def location_in_lane(self):
        loc = 0
        check = self
        while check.lead:
            check = check.lead
            loc += 1
            # if loc>50:
            #     print('possible chain list error: ',self.lead.id, self.id, self.follow.id)
            #     break
        return loc

    def stop(self):
        self.stopped = True

    def unstop(self):
        self.stopped = False

    def slow(self, v):
        self.v_max = v
        self.slowing_down = True

    def unslow(self):
        self.v_max = self._v_max
        self.slowing_down = False

    @property
    def lc_lock(self):
        if self.t >= self.lc_unlock_t:
            return True
        return False
