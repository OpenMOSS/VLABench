import random
import numpy as np
from VLABench.utils.register import register
from VLABench.tasks.config_manager import BenchTaskConfigManager
from VLABench.tasks.dm_task import LM4ManipBaseTask

@register.add_config_manager("get_coffee")
class GetCoffeeConfigManager(BenchTaskConfigManager):
    def __init__(self,
                 config,
                 num_objects=[1],
                 **kwargs
                 ):
        super().__init__(config, num_objects, **kwargs)

    def get_condition_config(self, target_entity, target_container, **kwargs):
        condition_config = dict(
            contain=dict(
                container=target_container,
                entities=[target_entity]
            )
        )
        self.config["task"]["conditions"] = condition_config
    
    def get_instruction(self, target_entity, target_container, **kwargs):
        instruction = [f"Get me a cup of coffee."]
        self.config["task"]["instructions"] = instruction
    
    def load_objects(self, target_entity, *kwargs):
        super().load_objects(target_entity, *kwargs)
        self.config["task"]["components"][-1]["randomness"] = None
        self.config["task"]["components"][-1]["position"] = [random.uniform(0.2, 0.3),
                                                             random.uniform(0, 0.2),
                                                             0.85]
        self.config["task"]["components"][-1]["orientation"] = [0, 0, -np.pi/2]
        box_config = dict(
            name="bottom",
            size=[0.06, 0.06, 0.02],
            position=[0, 0, -0.06],
            geom_type="box"
        )
        box_config["class"] = "BoxFlatContainer"
        self.config["task"]["components"][-1]["subentities"] = [box_config]
        
        
    def load_containers(self, target_container):
        super().load_containers(target_container)
        self.config["task"]["components"][-1]["position"] = [random.uniform(-0.3, -0.2), 
                                                             random.uniform(0.25, 0.35), 
                                                             0.78]
        
    
@register.add_config_manager("get_coffee_with_sugar")
class GetCoffeeWithSugarConfigManager(GetCoffeeConfigManager):
    def load_objects(self, target_entity):
        super().load_objects(target_entity)
        sugar_pos = [random.uniform(0.1, 0.2), random.uniform(-0.1, 0.), 0.05]
        sugar_config = self.get_entity_config("sugar", position=sugar_pos, orientation=[0, 0, np.pi/2], randomness=None)
        box_config = dict(
            name="bottom_sugar",
            size=[0.06, 0.06, 0.02],
            position=[sugar_pos[0], sugar_pos[1], sugar_pos[2]-0.07],
            geom_type="box"
        )
        box_config["class"] = "BoxFlatContainer"
        self.config["task"]["components"][-1]["subentities"].extend([sugar_config, box_config])
        
        
    def get_condition_config(self, **kwargs):
        condition_config = dict(
            pour=dict(
                target_entity="sugar"
            ),
            contain=dict(
                entities=["mug"],
                container="bottom"
            )
        )
        self.config["task"]["conditions"] = condition_config
    
    def get_instruction(self, target_entity, target_container, **kwargs):
        instruction = [f"Get me a cup of coffee with sugar."]
        self.config["task"]["instructions"] = instruction
        
@register.add_config_manager("get_coffee_with_milk")
class GetCoffeeWithMilkConfigManager(GetCoffeeConfigManager):
    def load_objects(self, target_entity):
        super().load_objects(target_entity)
        milk_pos = [random.uniform(0.2, 0.4), random.uniform(0.2, 0.3), 0.85]
        milk_config = self.get_entity_config("milk", position=milk_pos)
        self.config["task"]["components"].append(milk_config)
    
    def get_condition_config(self, target_entity, target_container, **kwargs):
        condition_config = dict(
            pour=dict(
                target_entity="milk"
            ),
            above_platform=dict(
                target_entity="milk",
                platform="bottom"
            )
        )
        self.config["task"]["conditions"] = condition_config

@register.add_task("get_coffee")
class GetCoffeeTask(LM4ManipBaseTask):
    def __init__(self, task_name, robot, **kwargs):
        super().__init__(task_name, robot=robot, **kwargs)
    
    def build_from_config(self, config, eval=False):
        super().build_from_config(config, eval)
        for key, entity in self.entities.items():
            if "coffee_machine" in key:
                entity.detach()
                self._arena.attach(entity)
    
    def should_terminate_episode(self, physics):
        condition_is_met = super().should_terminate_episode(physics)
        is_active = self.entities["coffee_machine"].is_pressed()
        if condition_is_met and is_active:
            return True
        else:
            return False
        
@register.add_task("get_coffee_with_sugar")
class GetCoffeeWithSugarTask(GetCoffeeTask):
    def __init__(self, task_name, robot, **kwargs):
        super().__init__(task_name, robot=robot, **kwargs)
    
    def initialize_episode(self, physics, random_state):
        self.machine_activated = False
        return super().initialize_episode(physics, random_state)
    
    def should_terminate_episode(self, physics):
        condition_is_met = self.conditions.is_met(physics)
        is_active = self.entities["coffee_machine"].is_pressed()
        if is_active: self.machine_activated = True # mean machine has been activated
        if condition_is_met and self.machine_activated:
            return True
        else:
            return False 
    
@register.add_task("get_coffee_with_milk")
class GetCoffeeWithMilkTask(GetCoffeeWithSugarTask):
    def __init__(self, task_name, robot, **kwargs):
        super().__init__(task_name, robot=robot, **kwargs)