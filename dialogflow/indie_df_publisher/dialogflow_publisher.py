
from indie_df_publisher.dialogflow_agent import DialogFlowAgent
from indie_df_publisher.entity_types_publisher import EntityTypesPublisher

import dialogflow_v2 as dialogflow

class DialogFlowPublisher:
    def __init__(self, namespace, project):
        self.namespace = namespace
        self.dialogflow_agent = DialogFlowAgent(namespace, project)
        self.entity_types_publisher = EntityTypesPublisher(namespace, project)
    
    def indie_training_phrases_to_dialogflow_training_phrases(self, indie_training_phrases):
        return [self.indie_training_phrase_to_dialogflow_training_phrase(tp) for tp in indie_training_phrases]
        
    def indie_training_phrase_to_dialogflow_training_phrase(self, indie_training_phrase):
        tp = dialogflow.types.Intent.TrainingPhrase()
        for part in indie_training_phrase['parts']:
            tpp = dialogflow.types.Intent.TrainingPhrase.Part()
            tpp.text = part['text']
            
            if 'alias' in part:
                tpp.alias = part['alias']

            if 'entity_type' in part:
                tpp.entity_type = part['entity_type']

            tp.parts.append(tpp)

        return tp    

    def indie_intent_to_dialogflow_intent(self, indie_intent, indie):
        display_name_suffix = indie_intent['id']

        training_phrases = self.indie_training_phrases_to_dialogflow_training_phrases(indie_intent['utterances'])
        followup_training_phrases = self.indie_training_phrases_to_dialogflow_training_phrases(indie_intent['followup_utterances'])

        parameters = []
        for indie_parameter in indie_intent['parameters']:
            parameter = dialogflow.types.Intent.Parameter(
                display_name=indie_parameter['id'],
                value=f"${indie_parameter['id']}",
                is_list=True,
                mandatory=indie_parameter['mandatory'],
                entity_type_display_name=indie_parameter['entity_type'],
                prompts=[f"What {indie_parameter['friendly_name']}?"])
            parameters.append(parameter)
            
        message = indie_intent['response_template']
        
        main_intent = self.dialogflow_agent.build_intent(display_name_suffix=display_name_suffix,
                                                  training_phrases=training_phrases,
                                                  message_texts=[message],
                                                  parameters=parameters,
                                                  is_fallback=False)

        followup_intent = self.dialogflow_agent.build_intent(display_name_suffix=display_name_suffix + '_followup',
                                                  training_phrases=followup_training_phrases,
                                                  message_texts=[message],
                                                  parameters=parameters,
                                                  is_fallback=False,
                                                  parent_followup_intent_name=main_intent.display_name)

        return main_intent, followup_intent
        

    def publish(self, indie):
        self.dialogflow_agent.delete_indie_intents()
        
        self.entity_types_publisher.delete_indie_entity_types()
        self.entity_types_publisher.create_entity_types(indie['custom_entities'].values(), indie)

        df_intents = []
        df_followup_intents = []
        indie_intents = indie['intents']
        
        for indie_intent in indie_intents:
            main_intent, followup_intent = self.indie_intent_to_dialogflow_intent(indie_intent, indie)
            df_intents.append(main_intent)
            if followup_intent:
                df_followup_intents.append(followup_intent)

        self.dialogflow_agent.create_intents(df_intents)
        intents = self.dialogflow_agent.list_intents()
        
        for df_followup_intent in df_followup_intents:
            df_followup_intent.parent_followup_intent_name = intents[df_followup_intent.parent_followup_intent_name].name

        self.dialogflow_agent.create_intents(df_followup_intents)
        
        self.dialogflow_agent.train()
