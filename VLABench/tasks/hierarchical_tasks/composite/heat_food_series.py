import random
import numpy as np
from VLABench.utils.register import register
from VLABench.tasks.config_manager import BenchTaskConfigManager
from VLABench.tasks.dm_task import LM4ManipBaseTask

@register.add_config_manager("heat_food")
class HeatFoodConfigManager(BenchTaskConfigManager):
    """
    Heat the cooked foods instead of raw foods.
    """
    disturbance_objects = ["ingredient", "canned_food"]
    def __init__(self, 
                 task_name,
                 num_objects = [3],
                 **kwargs):
        super().__init__(task_name, num_objects, **kwargs)
    
    def load_containers(self, target_container):
        super().load_containers(target_container)
        self.config["task"]["components"][-1]["position"] = [random.uniform(-0.15, -0.1), 
                                                             random.uniform(0.3, 0.4), 
                                                             0.8]
    
    def load_init_containers(self, init_container):
        if init_container is not None:
            self.init_container_config = self.get_entity_config(init_container,
                                                           position=[random.uniform(0.25, 0.35), 
                                                                    random.uniform(-0.1, 0.), 
                                                                    0.8],
                                                           orientation=[0, 0, np.pi/2])
            self.config["task"]["components"].append(self.init_container_config)
        
    def load_objects(self, target_entity):
        self.init_container_config["subentities"] = []
        
        objects = []
        objects.append(target_entity)
        objects.extend([random.choice(self.disturbance_objects) for _ in range(self.num_object-1)])
        random.shuffle(objects)
        for i, object in enumerate(objects):
            pos = [-0.1 + 0.1*i + random.uniform(-0.02, 0.02), random.uniform(-0.05, 0.05), 0.05]
            object_config = self.get_entity_config(object, 
                                                   position=pos,
                                                   orientation=[0, 0, -np.pi/2])
            self.init_container_config["subentities"].append(object_config)
    
    def get_instruction(self, target_entity, init_container, **kwargs):
        self.config["task"]["instructions"] = [f"Please heat {target_entity} from {init_container}."]
        return self.config
    
    def get_condition_config(self, target_entity, target_container, **kwargs):
        condition_config = dict(
            contain=dict(
                entities=[target_entity],
                container=target_container
            )
        )
        self.config["task"]["conditions"] = condition_config

@register.add_config_manager("plug_cord_and_heat_food")
class PlugCordAndHeatFoodConfigManager(HeatFoodConfigManager):
    def get_instruction(self, target_entity, init_container, **kwargs):
        self.config["task"]["instructions"] = [f"Please plug the cord and heat {target_entity} from {init_container}."]
        return self.config
    
    def load_containers(self, target_container):
        super().load_containers(target_container)
        cord_config = self.get_entity_config("cord", position=[-0.2, 0.34, 0], randomness=None)
        self.config["task"]["components"][-1]["subentities"] = [cord_config]

@register.add_task("heat_food")
class HeatFoodTask(LM4ManipBaseTask):
    def __init__(self, task_name, robot, **kwargs):
        super().__init__(task_name, robot=robot, **kwargs)

    def build_from_config(self, config, eval=False):    
        super().build_from_config(config, eval)
        for key, entity in self.entities.items():
                if "microwave" in key:
                    entity.detach()
                    self._arena.attach(entity)
    
    def should_terminate_episode(self, physics):
        condition_met = super().should_terminate_episode(physics)
        is_closed = self.entities[self.config_manager.target_container].is_closed(physics)
        is_active = self.entities[self.config_manager.target_container].is_activate(physics)
        success = condition_met and is_closed and is_active
        return success
        
@register.add_task("plug_cord_and_heat_food")
class PlugCordAndHeatFoodTask(HeatFoodTask):
    def __init__(self, task_name, robot, **kwargs):
        super().__init__(task_name, robot=robot, **kwargs)

    def build_from_config(self, config, eval=False):
        super().build_from_config(config, eval)
        for key, entity in self.entities.items():
            if "microwave" in key:
                microwave = entity
            if "cord" in key:
                cord = entity
        cord.detach()
        microwave.attach(cord)
    
    def after_step(self, physics, random_state):
        # TODO attach plug to the outlet
        return super().after_step(physics, random_state)