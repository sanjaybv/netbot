send_func = None

def register(func):
    global send_func
    send_func = func

def send(request, response):
    if send_func:
        send_func(response['text'])

def first_entity(entities, entity, attribute):
    if entity not in entities:
        return None

    val = entities[entity][0][attribute]
    if not val:
        return None

    return val['value'] if isinstance(val, dict) else val

def greet(request):
    context = request['context']
    entities = request['entities']

    print 'context:', context 
    print 'entities:', entities 

    if entities['intent'] and \
        first_entity(entities, 'intent', 'value') == 'greeting':
        print 'intent greeting'
        if entities['contact'] and \
                first_entity(entities, 'contact', 'confidence') > 0.8:
            context['name'] = first_entity(entities, 'contact', 'value')
            context.pop('missingName', None)
        else:
            context['missingName'] = True
            context.pop('name', None)

    print 'return context:', context 
    return context

actions = {
        'send': send,
        'greet': greet,
        }
