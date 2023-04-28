import json

def 
    origin_file_name = 
    output_file_name = 
    file = {'cells': []}

    for x in json.load(open(output_file_name))['cells']: 
        file['cells'].append(x)

    with open(origin_file_name, 'w') as out: 
        out.write(json.dumps(file))