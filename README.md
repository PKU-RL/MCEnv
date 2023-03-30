## Modified MineDojo Package

The code is a slightly modified version of [Minedojo](https://github.com/MineDojo/MineDojo). 

### Installation

Please refer to [this document](https://docs.minedojo.org/sections/getting_started/install.html) for the package installation and use. Note that Python>=3.9 is required.

Install modified MineDojo:
```
pip uninstall minedojo
Clone this repo. 
Run `python setup.py install`
```

### Modifications on MineDojo
- We allow repeatedly making a programmatic task. 

- In minedojo.make(), we allow overriding all the default parameters in programmatic tasks (e.g. lidar_rays, initial_inventory).

- We add some mirror URLs to load the simulator faster.

- We support randomly teleporting the player in the fast_reset mode: when calling env.reset(), the player will be teleported to a random location near its initial spawn point.

In minedojo.make(), use `fast_reset=True` to enable random teleportation:
```
env = minedojo.make(
            task_id="harvest_wool_with_shears_and_sheep",
            image_size=(160, 256),
            fast_reset=True,
            fast_reset_random_teleport_range_low=0,
            fast_reset_random_teleport_range_high=100,
        )
```
Then calling  `env.reset()`, the player will be teleported in a distance range of [0,100] by default. To disable moving the agent, use `env.reset(move_flag = False)`.

If you don't set the fast_reset parameters in minedojo.make(), our environment is the same as the original MineDojo.

### Reference

If you find the environment useful, please consider citing [Minedojo](https://arxiv.org/abs/2206.08853).

```bibtex
@article{fan2022minedojo,
  title   = {MineDojo: Building Open-Ended Embodied Agents with Internet-Scale Knowledge},
  author  = {Linxi Fan and Guanzhi Wang and Yunfan Jiang and Ajay Mandlekar and Yuncong Yang and Haoyi Zhu and Andrew Tang and De-An Huang and Yuke Zhu and Anima Anandkumar},
  year    = {2022},
  journal = {arXiv preprint arXiv: Arxiv-2206.08853}
}
```
