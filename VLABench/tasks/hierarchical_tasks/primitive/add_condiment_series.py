import random
from VLABench.tasks.dm_task import LM4ManipBaseTask, SpatialMixin, SemanticMixin, CommonSenseReasoningMixin
from VLABench.utils.register import register
from VLABench.tasks.config_manager import BenchTaskConfigManager
from VLABench.utils.utils import flatten_list
from VLABench.configs.constant import name2class_xml

SHAKER_INGRADIENTS = ["salt", "sugar"]

register.add_config_manager("add_condiment")
class AddCondimentConfigManager(BenchTaskConfigManager):
    def __init__(self,
                 config,
                 num_objects=[3, 4],
                 **kwargs
                 ):
        super().__init__(config, num_objects, **kwargs)
    
    def load_containers(self, target_container):
        stove_config = self.get_entity_config("stove", position=[0.1, 0, 0], randomness=None)
        container_config = self.get_entity_config(target_container, position=[random.uniform(-0.2, -0.1), random.uniform(-0.2, 0.), 0.84], randomness=None)
        container_config["subentities"] = [self.get_entity_config("dishes", position=[0, 0.03, 0.0], randomness=None)]
        self.config["task"]["components"].append(stove_config)
        self.config["task"]["components"].append(container_config)
        
    def get_instruction(self, target_entity, **kwargs):
        instruction = [f"Add {target_entity} to the dish"]
        self.config["task"]["instructions"] = instruction
     
    def get_condition_config(self, target_entity, target_container, **kwargs):
        conditions_config = dict(
            pour=dict(
                target_entity=target_entity
            ),
            above_platform=dict(
                target_entity=target_entity,
                platform=target_container
            )
        )
        self.config["task"]["conditions"] = conditions_config
    
    def load_objects(self, target_entity):
        objects = []
        objects.append(target_entity)
        other_objects = flatten_list(self.seen_object) + flatten_list(self.unseen_object)
        other_objects.remove(target_entity)
        objects.extend(random.sample(other_objects, self.num_object-1))
        random.shuffle(objects)
        for i, object in enumerate(objects):
            if target_entity == object:
                self.space_order = i + 1
            object_config = self.get_entity_config(object, 
                                                   position=[random.uniform(0.15, 0.2), 
                                                             -0.15+0.15*i, 
                                                             0.85])
            if object in SHAKER_INGRADIENTS:
                nametag_config = dict(
                    name=f"{object}_tag",
                    xml_path=name2class_xml["nametag"][-1],
                    position=[0.1, 0, -0.1],
                    content=object,
                    scale=2
                )
                nametag_config["class"] = name2class_xml["nametag"][0]
                object_config["subentities"] = [nametag_config]
                            
            self.config["task"]["components"].append(object_config)

@register.add_task("add_condiment")
class AddCondimentTask(LM4ManipBaseTask):
    def __init__(self, task_name, robot, **kwargs):
        super().__init__(task_name, robot=robot, **kwargs)
    
    def build_from_config(self, config, eval=False):
        """
        attach the dished to the pan and fix the nametag of shakers to worldframe 
        for reasonable and stable visual display.
        """
        super().build_from_config(config, eval)
        for key in list(self.entities.keys()):
            if "pan" in key:
                pan = self.entities[key]
        for key in list(self.entities.keys()):
            if "tag" in key:
                nametag = self.entities[key]
                nametag.detach()
                self._arena.attach(nametag)
            if "dishes" in key:
                dishes = self.entities[key]
                dishes.detach()
                pan.attach(dishes)

@register.add_config_manager("add_condiment_spatial")
class AddCondimentSpatialConfigManager(AddCondimentConfigManager):
    def get_instruction(self, target_entity, **kwargs):
        instruction = [f"Add {self.space_order}th condiment from bottom to the dish"]
        self.config["task"]["instructions"] = instruction

@register.add_config_manager("add_condiment_common_sense")
class AddCondimentCommonSenseConfigManager(AddCondimentConfigManager):
    """Judging based on the flavor and effect of the seasoning."""
    def get_instruction(self, target_entity, **kwargs):
       instruction = [f"The dish tastes sweet. Add some condiments to make it better."]
       self.config["task"]["instructions"] = instruction

@register.add_config_manager("add_condiment_semantic")
class AddCondimentSemanticConfigManager(AddCondimentConfigManager):
    def get_instruction(self, target_entity, **kwargs):
        instruction = [f"Add {target_entity} to the dish"]
        self.config["task"]["instructions"] = instruction

@register.add_task("add_condiment_spatial")
class AddCondimentSpatialTask(AddCondimentTask, SpatialMixin):
    def __init__(self, task_name, robot, **kwargs):
        super().__init__(task_name, robot, **kwargs)

@register.add_task("add_condiment_common_sense")
class AddCondimentCommonSenseTask(AddCondimentTask, CommonSenseReasoningMixin):
    def __init__(self, task_name, robot, **kwargs):
        super().__init__(task_name, robot, **kwargs)

@register.add_task("add_condiment_semantic")
class AddCondimentSemanticTask(AddCondimentTask, SemanticMixin):
    def __init__(self, task_name, robot, **kwargs):
        super().__init__(task_name, robot, **kwargs)