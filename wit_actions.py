import server_commands as sc

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
    print 'entities:', type(entities)

    if entities.get('intent') \
        and first_entity(entities, 'intent', 'value') == 'greeting':
        if entities.get('contact') and \
                first_entity(entities, 'contact', 'confidence') > 0.8:
            context['name'] = first_entity(entities, 'contact', 'value')
            context.pop('missingName', None)
        else:
            context['missingName'] = True
            context.pop('name', None)

    print 'return context:', context 
    return context

def hosts_status(request):
    context = request['context']
    entities = request['entities']

    print 'context:', context 
    print 'entities:', entities 

    if entities.get('intent') \
        and first_entity(entities, 'intent', 'value') == 'hosts_status':
        statuses = sc.get_hosts_status()
        print statuses 
        context['hosts_status'] = '\n' + '\n'.join(
                [(h + ' - ' + s) for h, s in statuses])

    print 'return context:', context 
    return context

actions = {
        'send': send,
        'greet': greet,
        'hosts_status': hosts_status
        }
