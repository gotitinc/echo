import dialogflow_v2 as dialogflow

class DialogFlowAgent:
    def __init__(self, namespace, project):
        self.namespace = namespace
        self.project = project
        self.agents_client = dialogflow.AgentsClient()
        self.intents_client = dialogflow.IntentsClient()

        self.agent = self.load_agent()

    def load_agent(self):
        parent = self.agents_client.project_path(self.project)
        agent = self.agents_client.get_agent(parent)
        return agent

    def set_default_agent(self):
        parent = self.agents_client.project_path(self.project)

        a2 = dialogflow.types.Agent()
        a2.parent = parent
        a2.display_name = f"{self.namespace} agent"
        a2.default_language_code = "en"
        a2.time_zone = "America/Denver"
        a2.classification_threshold = 0.3
        self.agent = agents_client.set_agent(a2)
        return self.agent
    
    def list_intents(self):
        parent = self.intents_client.project_agent_path(self.project)
        return {x.display_name:x for x in self.intents_client.list_intents(parent)}

    def delete_indie_intents(self):
        parent = self.intents_client.project_agent_path(self.project)

        intents = self.list_intents()
        intents_to_delete = []
        for display_name in intents:
            if display_name.startswith(self.namespace):
                intents_to_delete.append(intents[display_name])
        if len(intents_to_delete) > 0:
            self.intents_client.batch_delete_intents(parent, intents_to_delete)
        
    def build_intent(self, display_name_suffix, training_phrases=None,
                      message_texts=None, parameters=None, is_fallback=False,
                      parent_followup_intent_name=None):
        parent = self.intents_client.project_agent_path(self.project)

        messages = []
        if message_texts:
            text = dialogflow.types.Intent.Message.Text(text=message_texts)
            message = dialogflow.types.Intent.Message(text=text)
            messages.append(message)

        intent = dialogflow.types.Intent(
            display_name=f"{self.namespace}_{display_name_suffix}",
            training_phrases=training_phrases,
            messages=messages,
            parameters=parameters,
            is_fallback=is_fallback,
            parent_followup_intent_name=parent_followup_intent_name)
        
        intent.webhook_state = dialogflow.types.Intent.WebhookState.WEBHOOK_STATE_ENABLED

        return intent

    def create_intents(self, intents):
        parent = self.intents_client.project_agent_path(self.project)

        intents_batch =  dialogflow.types.IntentBatch()
        intents_batch.intents.extend(intents)
        response = self.intents_client.batch_update_intents(parent, intent_batch_inline=intents_batch)

        def callback(operation_future):
            # Handle result.
            result = operation_future.result()
            print('Intents created:')
            print(result)

        response.add_done_callback(callback)
        
    def train(self):
        parent = self.agents_client.project_path(self.project)

        response = self.agents_client.train_agent(parent)
        def callback(operation_future):
            # Handle result.
            result = operation_future.result()
            print('Agent training:')
            print(result)

        response.add_done_callback(callback)
