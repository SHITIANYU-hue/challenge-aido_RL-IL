import numpy as np
from ddpg import DDPG
from utils import seed
from args import get_ddpg_args_test
from gym_duckietown.simulator import Simulator
import torch
import cv2

env = Simulator(seed=123, map_name="zigzag_dists", max_steps=5000001, domain_rand=True, camera_width=640,
                camera_height=480, accept_start_angle_deg=4, full_transparency=True, distortion=True,
                randomize_maps_on_reset=True, draw_curve=False, draw_bbox=True, frame_skip=4, draw_DDPG_features=True)

# Set seeds
args = get_ddpg_args_test()
seed(args.seed)

state_dim = env.get_features().shape[0]
action_dim = env.action_space.shape[0]
max_action = float(env.action_space.high[0])

# Initialize policy
policy = DDPG(state_dim, action_dim, max_action, net_type="dense")
policy.load("model", directory="./models", for_inference=True)

with torch.no_grad():
    while True:
        env.reset()
        obs = env.get_features()
        env.render()
        rewards = []
        while True:
            action = policy.predict(np.array(obs))
            _, rew, done, misc = env.step(action)
            obs = env.get_features()
            rewards.append(rew)
            env.render()

            try:
                lp = env.get_lane_pos2(env.cur_pos, env.cur_angle)
                dist = abs(lp.dist)
            except:
                dist = 0

            print(f"Reward: {rew:.2f}",
                  f"\t| Action: [{action[0]:.3f}, {action[1]:.3f}]",
                  f"\t| Speed: {env.speed:.2f}",
                  f"\t| Dist.: {dist:.3f}")

            cv2.imshow("obs", obs)
            if cv2.waitKey() & 0xFF == ord('q'):
                break

            if done:
                break
        print("mean episode reward:", np.mean(rewards))
