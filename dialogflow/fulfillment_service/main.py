from flask import jsonify, make_response
import json
from pydialogflow_fulfillment import DialogflowRequest, DialogflowResponse, OutputContexts
import os
import requests

class DialogFlowFulfillmentService:
    def __init__(self):
        self.namespace = 'gotit'

    def parameters_to_slot_values(self, parameters):
        slot_values = {}

        for k, v in parameters.items():
            if k.startswith('slot-') and v:
                # Use first value of slot
                # TODO: Use multiple values for a slot
                if isinstance(v, list):
                    value = v[0]
                else:
                    value = v

                # Handle system entities
                if isinstance(value, dict):
                    if 'startDate' in value:
                        values = [value['startDate'], value['endDate']]
                    elif 'name' in value:
                        values = [value['name']]
                else:
                    values = [value]

                slot_values[k] = values

        return slot_values

    def results(self, request):
        # build a request object
        dialogflow_request = DialogflowRequest(request.data)
        project_id = dialogflow_request.get_project_id()
        session_id = dialogflow_request.get_session_id()

        # fetch action from json
        intent_name = dialogflow_request.get_intent_displayName()
        intent_id = intent_name.replace(f"{self.namespace}_", '')

        if not intent_id:
            return {'error': f"Intent name '{intent_name}' must start with '{self.namespace}_'"}

        parameters = dialogflow_request.get_parameters()
        print("parameters", parameters)
        if not parameters:
            return {'error': "No parameters found in dialogflow request"}

        print("---------------------")
        print("parameters", parameters)
        slot_values = self.parameters_to_slot_values(parameters)
        print("slot_values", slot_values)

        response_template = request.get_json()['queryResult']['fulfillmentText']
        print("response_template", response_template)

        payload = {
            'intent_id': intent_id,
            'slot_values': slot_values,
            'response_template': response_template
        }

        print('calling InDiE fulfillment: ', payload)

        indie_fulfillment_service_url = os.environ['INDIE_FULFILLMENT_SERVICE_URL']
        r = requests.post(indie_fulfillment_service_url, json=payload, verify=False)
        if r.ok:
            r = r.json()

            if 'response_text' in r:
                response_text = r['response_text']
                dialogflow_response = DialogflowResponse(response_text)
                return json.loads(dialogflow_response.get_final_response())
            else:
                if 'error' in r:
                    return r

        return {'error': "Failed to receive response from InDiE fulfillment service"}

def webhook(request):
    fulfillment_service = DialogFlowFulfillmentService()
    return make_response(jsonify(fulfillment_service.results(request)))
