import dialogflow_v2 as dialogflow

class EntityTypesPublisher:
    def __init__(self, namespace, project):
        self.client = dialogflow.EntityTypesClient()
        self.project = project
        self.namespace = namespace
        self.table_column_to_custom_entity = {}

    def create_entity_types(self, indie_custom_entities, indie):
        parent = self.client.project_agent_path(self.project)

        entity_type_batch = dialogflow.types.EntityTypeBatch()
        for de in indie_custom_entities:
            et = self.indie_custom_entity_to_dialogflow_entity_type(de)
            if et:
                entity_type_batch.entity_types.append(et)

        response = self.client.batch_update_entity_types(parent, entity_type_batch_inline=entity_type_batch)

        def callback(operation_future):
            # Handle result.
            result = operation_future.result()
            print('Entity types created')
            print(result)

        response.add_done_callback(callback)
        
    def indie_custom_entity_to_dialogflow_entity_type(self, indie_custom_entity):
        entity_type = dialogflow.types.EntityType()
        entity_type.display_name = f"{self.namespace}-{indie_custom_entity['index']}"
        self.table_column_to_custom_entity[f"{indie_custom_entity['table']}.{indie_custom_entity['column']}"] = f"@{entity_type.display_name}"
        entity_type.kind = 1
        
        for value, synonyms in indie_custom_entity['dictionary'].items():
            entity = dialogflow.types.EntityType.Entity()
            entity.value = value
            if len(synonyms) > 0:
                entity.synonyms.extend(synonyms)
            entity_type.entities.append(entity)
        
        return entity_type

    def list_entity_types(self):
        parent = self.client.project_agent_path(self.project)
        return {x.display_name:x for x in self.client.list_entity_types(parent)}
    
    def delete_indie_entity_types(self):
        parent = self.client.project_agent_path(self.project)

        entity_types = self.list_entity_types()
        entity_types_to_delete = []
        for display_name in entity_types:
            if display_name.startswith(self.namespace):
                entity_types_to_delete.append(entity_types[display_name].name)
        if len(entity_types_to_delete) > 0:
            self.client.batch_delete_entity_types(parent, entity_types_to_delete)
        
