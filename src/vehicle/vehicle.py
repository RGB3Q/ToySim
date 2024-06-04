import uuid
import numpy as np
from src.geometry.lanes import Lane
from typing import List


# create Vehicle class for simulation
class Vehicle:
    def __init__(self, config={}):
        # set default config
        self.set_default_config()

        # update config
        self.update_config(config)

        self.lead = None
        self.follow = None

        self.dt = 1/60

        # 定义礼貌因子politeness factor，用于权衡自身优势和对他人的影响
        # 这个值可以根据需要调整，0表示完全自私，1表示完全利他
        self.politeness = 0.5

    def set_default_config(self):
        self.id = uuid.uuid4()

        # minimal safe distance
        self.s0 = 4

        # reaction time
        self.T = 1.5

        self.length = 4
        self.v_max = 16
        self._v_max = 16

        self.a_max = 1.5
        self.b_max = 9

        self.path = []
        self.current_road_index = 0

        self.x = 0
        self.v = 0
        self.a = 0
        self.stopped = False

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
        if self.v +self.a * dt < 0:
            self.x -= 0.5*self.v**2 / self.a
            self.v = 0
        else:
            self.v += self.a * dt
            self.x += self.v * dt + self.a*dt**2 / 2

        # Update acceleration
        alpha = 0
        if lead:
            delta_x = lead.x - self.x - lead.length
            delta_v = self.v - lead.v

            alpha = (self.s0 + max(0, self.T * self.v + delta_v * self.v / self.sqrt_ab)) / delta_x

        self.a = self.a_max * (1 - (self.v / self.v_max) ** 4 - alpha ** 2)

        if self.stopped:
            self.a = -self.b_max*self.v / self.v_max

        return self.a

    def evaluate_and_perform_lane_change(self, lanes: List[Lane]):
        """
        Evaluate whether it is safe to change lane
        :param lanes: [left_lane, right_lane] when has both, [None, right_lane] when only right_lane and vice versa
        :return:
        """
        # acquire present_lane_id
        p = self.at_lane
        # 左右车道都存在
        if lanes[0] and lanes[1]:
            left_incentive, l_leader, l_follower = self.calculate_incentive(lanes[0])
            right_incentive, r_leader, r_follower = self.calculate_incentive(lanes[1])

            if left_incentive > right_incentive and left_incentive > 0:
                self.implement_lane_change(lanes[p], lanes[p-1], l_leader, l_follower)
            elif right_incentive > left_incentive and right_incentive > 0:
                self.implement_lane_change(lanes[p], lanes[p-1], r_leader, r_follower)
        # 仅存在左侧车道
        elif lanes[0]:
            left_incentive, l_leader, l_follower = self.calculate_incentive(lanes[0])
            if left_incentive > 0:
                self.implement_lane_change(lanes[p], lanes[p-1], l_leader, l_follower)
        # 仅存在右侧车道
        elif lanes[1]:
            right_incentive, r_leader, r_follower = self.calculate_incentive(lanes[1])
            if right_incentive > 0:
                self.implement_lane_change(lanes[p], lanes[p-1], r_leader, r_follower)

    def implement_lane_change(self, present_lane: Lane, target_lane: Lane, target_lead, target_follow):
        """
        修改目标lane链表：将ego_car插入并更新链表状态
        :param present_lane: lane where vehicle is currently on
        :param target_lane: lane where vehicle wants to go
        :param target_lead: lead vehicle of target_lane after moving into
        :param target_follow: follow vehicle of target_lane after moving into
        """
        present_lane.remove_vehicle(self)
        target_lead.follow = self
        target_follow.lead = self
        self.lead = target_lead
        self.follow = target_follow

        target_lane.vehicles.insert(target_lead.location_in_lane, self)

    def perform_lane_change1(self, present_lane, target_lane):  # MoBIL模型判断是否换道
        candidate_follow, candidate_lead = self.search_adjacent_lane(target_lane)
        present_a = self.IDM(candidate_lead)  # 当前车道的加速度
        target_a = self.IDM(candidate_lead)  # 目标车道的加速度
        follow_a = candidate_follow.IDM(self)  # 目标车道后车的加速度

        if target_a - present_a > 0.1 and follow_a > -4:
            # 执行换道逻辑
            self.change_lane_link_lst(present_lane, target_lane, follow, lead)

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
        # 计算当前车道上的加速度
        current_acceleration = self.IDM(self.lead, self.dt)
        # 假设target_vehicle是目标车道上当前车辆前方的车辆
        # 计算换道后可能的加速度
        target_leader, target_follower = self.search_adjacent_lane(target_lane)
        if target_leader and target_follower:
            present_a = self.IDM(self.lead, self.dt)  # 当前车道的加速度
            target_a = self.IDM(target_leader, self.dt)  # 目标车道的加速度
            follow_a_latent = target_follower.IDM(self)  # 换道后目标车道后车的加速度
            follow_a = target_follower.IDM(target_leader, self.dt)  # 不换道目标车道后车的加速度

            # 计算换道后的自身优势（换道后的加速度 - 换道前的加速度）
            self_advantage = target_a - present_a
            # 计算对目标车道后方车辆的不利影响
            # 假设target_vehicle的后车是目标车道上换道后紧随当前车辆的车辆
            follower_disadvantage = follow_a_latent - follow_a
        elif target_leader and not target_follower:
            present_a = self.IDM(self.lead, self.dt)  # 当前车道的加速度
            target_a = self.IDM(target_leader, self.dt)  # 目标车道的加速度

            # 计算换道后的自身优势（换道后的加速度 - 换道前的加速度
            self_advantage = target_a - present_a
            # 计算对目标车道后方车辆的不利影响
            # 假设target_vehicle的后车是目标车道上换道后紧随当前车辆的车辆
            follow_a_latent = 0
            follower_disadvantage = 0
        else:
            present_a = self.IDM(self.lead, self.dt)  # 当前车道的加速度
            target_a = self.IDM(None, self.dt)  # 目标车道的加速度
            follow_a_latent = target_follower.IDM(self)  # 换道后目标车道后车的加速度
            follow_a = target_follower.IDM(target_leader, self.dt)  # 不换道目标车道后车的加速度

            self_advantage = target_a - present_a
            follower_disadvantage = follow_a_latent - follow_a

        # 计算激励标准
        # 如果自身优势大于礼貌因子乘以对后方车辆的不利影响，则激励换道
        incentive = self_advantage - self.politeness * follower_disadvantage - 0.2
        if follow_a_latent < -4:
            incentive = -1000

        return incentive, target_leader, target_follower

    @ property
    def location_in_lane(self):
        loc = 0
        check = self
        while check.lead:
            check = check.lead
            loc += 1
        return loc

    def stop(self):
        self.stopped = True

    def unstop(self):
        self.stopped = False

    def slow(self, v):
        self.v_max = v

    def unslow(self):
        self.v_max = self._v_max









