from distutils.file_util import move_file
from shlex import join
import minedojo
#from minedojo.sim.wrappers import fast_reset
import os
import imageio
import numpy as np
import numpy

if __name__ == "__main__":
    task_id_list=[
        # "harvest_1_cobblestone_with_wooden_pickaxe"
        # "combat_spider_plains_leather_armors_diamond_sword_shield",
        # "combat_enderman_end_diamond_armors_diamond_sword_shield",
        # "combat_zombie_plains_diamond_armors_diamond_sword_shield",
        # "combat_zombie_extreme_hills_diamond_armors_iron_sword_shield",
        # "combat_sheep_plains_diamond_armors_iron_sword_shield",
        # "combat_wither_skeleton_nether_leather_armors_diamond_sword_shield",
        # "harvest_wool_with_shears_and_sheep",
        # "harvest_milk_with_empty_bucket_and_cow",
        "harvest_1_dirt",
        "harvest_1_wheat_swampland",
        "harvest_1_wheat_forest",
        "harvest_1_wheat_taiga",
        "harvest_1_wheat_jungle",
        # "harvest_1_banner_with_crafting_table",
        # "techtree_from_diamond_to_redstone_compass",
    ]
    seed=6+1
    

    save_path="./"
    for i_ in task_id_list:
        np.random.seed(seed)
        save_pth = os.path.join(save_path, i_)
        if not os.path.exists(save_pth):
            os.mkdir(save_pth)    
        env = minedojo.make(
            task_id=i_,
            image_size=(288, 512),
            seed=seed,
            # fast_reset = False,
            fast_reset=True,# set teleport_reset mode
            # # teleport distance: [0,300]
            fast_reset_random_teleport_range_low=0,
            fast_reset_random_teleport_range_high=300,
        )
        print(f"[INFO] Create a task with prompt: {env.task_prompt}")

        env.reset()
        total_num = 100
        for i in range(total_num):
            img_list = []
            stone_flag = False
            obs = []
            for j in range(30):
                action = env.action_space.no_op()
                action[4]=13
                obs, reward, done, info = env.step(action)
                img_list.append(np.transpose(obs['rgb'], [1,2,0]).astype(np.uint8))
                if done:
                    break
            pth = os.path.join(save_pth, '{}.gif'.format(i))
            
            imageio.mimsave(pth, img_list, duration=0.15)
            # move_flag=True: reset and random teleport
            # if in forest env, set forest_flag=True (this flag can be set =True in other envs, but it will make the reset a little bit slower)
            env.reset()
        env.close()

    print("[INFO] Test Success")
