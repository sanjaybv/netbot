send_func = None

def register(func):
    global send_func
    send_func = func

def send(request, response):
    if send_func:
        send_func(response['text'])

def first_entity_value(entities, entity):
    if entity not in entities:
        return None

    val = entities[entity][0]['value']
    if not val:
        return None

    return val['value'] if isinstance(val, dict) else val

def greet(request):
    context = request['context']
    entities = request['entities']

    print 'context:', context 
    print 'entities:', entities 

    context['name'] = 'Nameless'

    print 'return context:', context 
    return context

actions = {
        'send': send,
        'greet': greet,
        }
