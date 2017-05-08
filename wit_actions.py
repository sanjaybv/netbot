import server_commands as sc

send_func = None

def register(func):
    global send_func
    send_func = func

def send(request, response):
    if send_func:
        send_func(response['text'])

def correct_action(context, entities, orig_intent):
    if entities.get('intent'):
        intent = first_entity(entities, 'intent', 'value')
        if intent != orig_intent:
            return actions[intent_actions[intent]]

    return None

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

    print '>>>>>>>> greet()'
    print 'context:', context 
    print 'entities:', entities

    action = correct_action(context, entities, 'greeting')
    if action:
        return action(request)

    if entities.get('contact') and \
            first_entity(entities, 'contact', 'confidence') > 0.8:
        context['name'] = first_entity(entities, 'contact', 'value')
        context.pop('missingName', None)
    else:
        context['missingName'] = True
        context.pop('name', None)

    print 'return context:', context 
    print '<<<<<<<\n'
    return context

def hosts_status(request):
    context = request['context']
    entities = request['entities']

    print '>>>>>>>> hosts_status()'
    print 'context:', context 
    print 'entities:', entities 

    action = correct_action(context, entities, 'hosts_status')
    if action:
        return action(request)

    statuses = sc.get_hosts_status()
    print statuses 
    context['hosts_status'] = statuses

    print 'return context:', context 
    print '<<<<<<<<\n'
    return context

def deploy(request):
    context = request['context']
    entities = request['entities']
    if not entities:
        entities = {}

    print '>>>>>>>> deploy()'
    print 'context:', context 
    print 'entities:', entities 

    action = correct_action(context, entities, 'deploy')
    if action:
        return action(request)


    # clear errors in context
    context.pop('serverUnavailable', None)

    # check for url
    if not context.get('url'):
        if not (entities.get('url') \
            and first_entity(entities, 'url', 'confidence') > 0.8 \
            and first_entity(entities, 'url', 'domain') == 'github.com'):
            context['missingUrl'] = True
            print 'mu return context:', context 
            print '<<<<<<<<\n'
            return context
        context.pop('missingUrl', None)
        context['url'] = first_entity(
                entities, 'url', 'value').split('|')[1][:-1]

    # check for a server name
    if not context.get('server_name'):
        if not (entities.get('server_name') \
                and first_entity(entities, 'server_name', 'confidence') > 0.8):
            context['missingServerName'] = True
            print 'msn return context:', context 
            print '<<<<<<<<\n'
            return context
        context.pop('missingServerName', None)
        context['server_name'] = first_entity(entities, 'server_name', 'value')

    print 'deploying {0} on {1}'.format(
            context.get('url'), context.get('server_name'))


    # call server command to deploy url
    isError = False
    try:
        sc.deploy(context.get('url'), context.get('server_name'))
    except (sc.ServerUnavailableException, sc.SSHUnavailableException) as e:
        isError = True
        context['serverUnavailable'] = str(e)
        context.pop('server_name', None)
    except sc.SCException as e:
        isError = True
        context['deployError'] = str(e)
        
    if isError:
        print 'return context:', context 
        print '<<<<<<<<\n'
        return context 


    context['deployed'] = True
    context.pop('url')
    context.pop('server_name')

    print 'return context:', context 
    print '<<<<<<<<\n'
    return context

def stop(request):
    context = request['context']
    entities = request['entities']
    if not entities:
        entities = {}

    print '>>>>>>>> stop()'
    print 'context:', context 
    print 'entities:', entities 

    action = correct_action(context, entities, 'stop')
    if action:
        return action(request)

    # check for url
    if not context.get('url'):
        if not (entities.get('url') \
            and first_entity(entities, 'url', 'confidence') > 0.8 \
            and first_entity(entities, 'url', 'domain') == 'github.com'):
            context['stopMissingUrl'] = True
            print 'mu return context:', context 
            print '<<<<<<<<\n'
            return context
        context.pop('stopMissingUrl', None)
        context['url'] = first_entity(
                entities, 'url', 'value').split('|')[1][:-1]

    # check for a server name
    if not context.get('server_name'):
        if not (entities.get('server_name') \
                and first_entity(entities, 'server_name', 'confidence') > 0.8):
            context['stopMissingServerName'] = True
            print 'msn return context:', context 
            print '<<<<<<<<\n'
            return context
        context.pop('stopMissingServerName', None)
        context['server_name'] = first_entity(entities, 'server_name', 'value')

    print 'stopping {0} on {1}'.format(
            context.get('url'), context.get('server_name'))

    # call server command to stop service
    isError = False
    try:
        stop_status = sc.stop(context.get('url'), context.get('server_name'))
    except sc.SCException as e:
        isError = True
        context['stopError'] = str(e)
        
    if not isError:
        context['stopped'] = stop_status
        context.pop('url')
        context.pop('server_name')

    print 'return context:', context 
    print '<<<<<<<<\n'
    return context


def get_service_status(request):
    context = request['context']
    entities = request['entities']

    print '>>>>>>>> get_service_status()'
    print 'context:', context 
    print 'entities:', entities 

    action = correct_action(context, entities, 'service_status')
    if action:
        return action(request)

    try:
        statuses = sc.get_all_service_status()
        context['serviceStatus'] = statuses
    except Exception as e:
        context['serviceStatus'] = str(e)

    print 'return context:', context 
    print '<<<<<<<<\n'
    return context

'''
def get_service_status(request):
    context = request['context']
    entities = request['entities']

    print '>>>>>>>> get_service_status()'
    print 'context:', context 
    print 'entities:', entities

    # action = correct_action(context, entities, 'get_service_status')
    # if action:
    #     return action(request)
    
    # check for url
    if not context.get('url'):
        if not (entities.get('url') \
            and first_entity(entities, 'url', 'confidence') > 0.8 \
            and first_entity(entities, 'url', 'domain') == 'github.com'):
            context['serviceStatusMissingURL'] = True
            print 'mu return context:', context 
            print '<<<<<<<<\n'
            return context
        context.pop('serviceStatusMissingURL', None)
        context['url'] = first_entity(
                entities, 'url', 'value').split('|')[1][:-1]

    # check for a server name
    if not context.get('server_name'):
        if not (entities.get('server_name') \
                and first_entity(entities, 'server_name', 'confidence') > 0.8):
            context['serviceStatusMissingServerName'] = True
            print 'msn return context:', context 
            print '<<<<<<<<\n'
            return context
        context.pop('serviceStatusMissingServerName', None)
        context['server_name'] = first_entity(entities, 'server_name', 'value')


    
    serviceStatus = sc.get_service_status(context.get('url'), context.get('server_name'))    
    if serviceStatus != None:
        context['serviceStatus'] = serviceStatus
        print 'return context:', context 
        print '<<<<<<<<\n'
        return context 


    # context[''] = True
    # context.pop('url')
    # context.pop('server_name')
    
    print 'return context:', context 
    print '<<<<<<<<\n'
    return context
'''

def end_conversation(request):
    context = request['context']
    entities = request['entities']

    print '>>>>>>>> end_conversation()'
    print 'context:', context 
    print 'entities:', entities 

    context = {}

    print 'return context:', context 
    print '<<<<<<<<\n'
    return context

actions = {
        'send': send,
        'greet': greet,
        'hosts_status': hosts_status,
        'deploy': deploy,
        'stop': stop,
        'end_conversation': end_conversation,
        'get_service_status': get_service_status
        }

intent_actions = {
        'greet': 'greet',
        'hosts_status': 'hosts_status',
        'deploy': 'deploy',
        'end_conversation': 'end_conversation',
        'service_status': 'get_service_status',
        'stop':'stop',
        }
